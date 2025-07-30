from pydantic import BaseModel
from typing import Optional, Dict, List, Any


class MaskHash(BaseModel):
    algo: str


class MaskPassThrough(BaseModel):
    pass


class MaskBucketNumber(BaseModel):
    buckets: List[int]


class MaskBucketDate(BaseModel):
    precision: str


class MaskRandPattern(BaseModel):
    pattern: str


class MaskRandRegexify(BaseModel):
    pattern: str


class MaskRegexReplace(BaseModel):
    pattern: str
    replacement: str


class Mask(BaseModel):
    operator: str
    pass_through: Optional[MaskPassThrough] = None
    hash: Optional[MaskHash] = None
    redact: Optional[Dict[str, Any]] = None
    bucket_number: Optional[MaskBucketNumber] = None
    bucket_date: Optional[MaskBucketDate] = None
    rand_pattern: Optional[MaskRandPattern] = None
    rand_regexify: Optional[MaskRandRegexify] = None
    regex_replace: Optional[MaskRegexReplace] = None
    supported_data_types: Optional[List[str]] = None
