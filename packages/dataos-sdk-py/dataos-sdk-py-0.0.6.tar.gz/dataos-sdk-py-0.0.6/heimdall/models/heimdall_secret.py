from typing import List, Dict

from pydantic import Field, BaseModel

from commons.utils import helper
from heimdall.models.data import Data
from heimdall.models.links import Links


class HeimdallSecret(BaseModel):
    id: str
    data: List[Data]
    links: Links = Field(alias="_links")

    ACCESS_KEY_ID: str = "awsaccesskeyid"
    SECRET_KEY: str = "awssecretaccesskey"
    AZURE_STORAGE_ACCOUNT_NAME: str = "azurestorageaccountname"
    AZURE_STORAGE_ACCOUNT_KEY: str = "azurestorageaccountkey"
    GCS_KEY_JSON = "gcskey_json"
    PRIVATE_KEY = "privatekey"
    PRIVATE_KEY_ID = "privatekeyid"
    EMAIL = "email"
    GCS_CLIENT_EMAIL = "client_email"
    GCS_PRIVATE_KEY_ID = "private_key_id"
    GCS_PRIVATE_KEY = "private_key"
    GCS_SERVICE_ACCOUNT_EMAIL = "fs.gs.auth.service.account.email"
    GCS_SERVICE_PRIVATE_KEY_ID = "fs.gs.auth.service.account.private.key.id"
    GCS_SERVICE_PRIVATE_KEY = "fs.gs.auth.service.account.private.key"
    ABFSS_STORAGE_ACCOUNT_KEY_TEMPLATE: str = "fs.azure.account.key.%s.dfs.core.windows.net"
    WASBS_STORAGE_ACCOUNT_KEY_TEMPLATE: str = "fs.azure.account.key.%s.blob.core.windows.net"
    S3_ACCESS_KEY: str = "fs.s3a.access.key"
    S3_SECRET_KEY: str = "fs.s3a.secret.key"

    def toS3Secrets(self, key: str) -> Dict[str, str]:
        props = self.toSecretProperties(key)
        accessKey = props[self.ACCESS_KEY_ID]
        secretKey = props[self.SECRET_KEY]

        secrets = {}
        secrets[self.S3_ACCESS_KEY] = accessKey
        secrets[self.S3_SECRET_KEY] = secretKey
        return secrets

    def toABFSSSecrets(self, key: str) -> Dict[str, str]:
        props = self.toSecretProperties(key)
        storageAccountName = props[self.AZURE_STORAGE_ACCOUNT_NAME]
        storageAccountKey = props[self.AZURE_STORAGE_ACCOUNT_KEY]

        storageSparkConfKey = self.ABFSS_STORAGE_ACCOUNT_KEY_TEMPLATE % storageAccountName
        secrets = {}
        secrets[storageSparkConfKey] = storageAccountKey
        return secrets

    def toWASBSSecrets(self, key: str) -> Dict[str, str]:
        props = self.toSecretProperties(key)
        storageAccountName = props[self.AZURE_STORAGE_ACCOUNT_NAME]
        storageAccountKey = props[self.AZURE_STORAGE_ACCOUNT_KEY]

        storageSparkConfKey = self.WASBS_STORAGE_ACCOUNT_KEY_TEMPLATE % storageAccountName
        secrets = {}
        secrets[storageSparkConfKey] = storageAccountKey
        return secrets

    def toGCSSecrets(self, key: str) -> Dict[str, str]:
        props = self.toSecretProperties(key)
        gcsKeyJson = helper.getValueOrThrow(props, self.GCS_KEY_JSON)
        jsonProperties = helper.convertJsonToProperties(gcsKeyJson)
        email = helper.getValueOrNull(props, self.EMAIL)
        if email is None:
            email = helper.getValueOrThrow(jsonProperties, self.GCS_CLIENT_EMAIL)

        privateKey = helper.getValueOrNull(props, self.PRIVATE_KEY)
        if privateKey is None:
            privateKey = helper.getValueOrThrow(jsonProperties, self.GCS_PRIVATE_KEY)

        privateKey
