from pydantic import BaseModel
from typing import Optional, Dict, List

from heimdall.models.authorization_result_data import AuthorizationResultData
from heimdall.models.dataset import Dataset
from heimdall.models.filter import Filter
from heimdall.models.mask import Mask


class Decision(BaseModel):
    table: Optional[Dataset] = None
    user: Optional[AuthorizationResultData] = None
    masks: Optional[Dict[str, Mask]] = None
    filter: Optional[List[Filter]] = None
