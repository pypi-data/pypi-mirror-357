from dataclasses import dataclass
from typing import Type, Optional, List

from .base import BaseRequest, BaseResponse, PageRequest, PageResponse

# #################################################################
# Size Group
# #################################################################


@dataclass
class SizeGroupDetail:
    id: Optional[int] = None
    name: Optional[str] = None


@dataclass
class SizeGroupDetailResponse(BaseResponse):
    data: Optional[SizeGroupDetail] = None


@dataclass
class SizeGroupSaveDTO:
    name: str
    id: Optional[int] = None


@dataclass
class SizeGroupSaveRequest(BaseRequest[SizeGroupDetailResponse]):
    size_group_save_dto: Optional['SizeGroupSaveDTO'] = None

    def response_class(self) -> Type[SizeGroupDetailResponse]:
        return SizeGroupDetailResponse

    def get_api_url(self) -> str:
        return "api/open/size/group/add"

    def get_request_type(self) -> str:
        return "POST"


@dataclass
class SizeGroupListResponse(PageResponse):
    data: Optional[List[SizeGroupDetail]] = None


@dataclass
class SizeGroupListRequest(PageRequest[SizeGroupListResponse]):
    name: Optional[str] = None

    def response_class(self) -> Type[SizeGroupListResponse]:
        return SizeGroupListResponse

    def get_api_url(self) -> str:
        return "api/open/size/group/list"

    def get_request_type(self) -> str:
        return "GET"


@dataclass
class SizeGroupDetailRequest(BaseRequest[SizeGroupDetailResponse]):
    size_group_id: Optional[int] = None

    def response_class(self) -> Type[SizeGroupDetailResponse]:
        return SizeGroupDetailResponse

    def get_api_url(self) -> str:
        return "api/open/size/group/get"

    def get_request_type(self) -> str:
        return "GET"


# #################################################################
# Size Base
# #################################################################

@dataclass
class SizeDetail:
    id: Optional[int] = None
    name: Optional[str] = None
    size_group_id: Optional[int] = None
    show_order: Optional[int] = None
    status: Optional[int] = None
    is_default: Optional[int] = None
    remark: Optional[str] = None


@dataclass
class SizeDetailResponse(BaseResponse):
    data: Optional[SizeDetail] = None


@dataclass
class SizeSaveDTO:
    name: str
    size_group_id: int
    is_default: int
    show_order: Optional[int] = None
    status: Optional[int] = None
    remark: Optional[str] = None


@dataclass
class SizeSaveRequest(BaseRequest[SizeDetailResponse]):
    size_save_dto: Optional['SizeSaveDTO'] = None

    def response_class(self) -> Type[SizeDetailResponse]:
        return SizeDetailResponse

    def get_api_url(self) -> str:
        return "api/open/size/base/add"

    def get_request_type(self) -> str:
        return "POST"


@dataclass
class SizeListResponse(PageResponse):
    data: Optional[List[SizeDetail]] = None


@dataclass
class SizeListRequest(PageRequest[SizeListResponse]):
    name: Optional[str] = None

    def response_class(self) -> Type[SizeListResponse]:
        return SizeListResponse

    def get_api_url(self) -> str:
        return "api/open/size/base/list"

    def get_request_type(self) -> str:
        return "GET"


@dataclass
class SizeDetailRequest(BaseRequest[SizeDetailResponse]):
    size_id: Optional[int] = None

    def response_class(self) -> Type[SizeDetailResponse]:
        return SizeDetailResponse

    def get_api_url(self) -> str:
        return "api/open/size/base/get"

    def get_request_type(self) -> str:
        return "GET" 