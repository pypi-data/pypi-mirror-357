from dataclasses import dataclass
from typing import Type, Optional, List

from .base import BaseRequest, BaseResponse, PageRequest, PageResponse

# #################################################################
# Color Group
# #################################################################


@dataclass
class ColorGroupDetail:
    id: Optional[int] = None
    name: Optional[str] = None


@dataclass
class ColorGroupDetailResponse(BaseResponse):
    data: Optional[ColorGroupDetail] = None


@dataclass
class ColorGroupSaveDTO:
    name: str
    id: Optional[int] = None


@dataclass
class ColorGroupSaveRequest(BaseRequest[ColorGroupDetailResponse]):
    color_group_save_dto: Optional[ColorGroupSaveDTO] = None

    def response_class(self) -> Type[ColorGroupDetailResponse]:
        return ColorGroupDetailResponse

    def get_api_url(self) -> str:
        return "api/open/color/group/add"

    def get_request_type(self) -> str:
        return "POST"


@dataclass
class ColorGroupListResponse(PageResponse):
    data: Optional[List[ColorGroupDetail]] = None


@dataclass
class ColorGroupListRequest(PageRequest[ColorGroupListResponse]):
    name: Optional[str] = None

    def response_class(self) -> Type[ColorGroupListResponse]:
        return ColorGroupListResponse

    def get_api_url(self) -> str:
        return "api/open/color/group/list"

    def get_request_type(self) -> str:
        return "GET"


@dataclass
class ColorGroupDetailRequest(BaseRequest[ColorGroupDetailResponse]):
    color_group_id: Optional[int] = None

    def response_class(self) -> Type[ColorGroupDetailResponse]:
        return ColorGroupDetailResponse

    def get_api_url(self) -> str:
        return "api/open/color/group/get"

    def get_request_type(self) -> str:
        return "GET"


# #################################################################
# Color Base
# #################################################################

@dataclass
class ColorBaseDetail:
    """Color Detail Information"""
    id: Optional[int] = None
    name: Optional[str] = None
    color_value: Optional[str] = None
    color_group_id: Optional[int] = None
    show_order: Optional[int] = None
    status: Optional[int] = None
    is_default: Optional[int] = None
    remark: Optional[str] = None


@dataclass
class ColorBaseDetailResponse(BaseResponse):
    """Response for color detail operations."""
    data: Optional[ColorBaseDetail] = None


@dataclass
class ColorBaseSaveDTO:
    """Data Transfer Object for saving a color."""
    name: str
    color_group_id: int
    color_value: Optional[str] = None
    show_order: Optional[int] = None
    status: Optional[int] = None
    is_default: Optional[int] = None
    remark: Optional[str] = None


@dataclass
class ColorBaseSaveRequest(BaseRequest[ColorBaseDetailResponse]):
    """Request to save a color."""
    color_save_dto: Optional[ColorBaseSaveDTO] = None

    def response_class(self) -> Type[ColorBaseDetailResponse]:
        return ColorBaseDetailResponse

    def get_api_url(self) -> str:
        return "api/open/color/base/add"

    def get_request_type(self) -> str:
        return "POST"


@dataclass
class ColorBaseListResponse(PageResponse):
    data: Optional[List[ColorBaseDetail]] = None


@dataclass
class ColorBaseListRequest(PageRequest[ColorBaseListResponse]):
    name: Optional[str] = None

    def response_class(self) -> Type[ColorBaseListResponse]:
        return ColorBaseListResponse

    def get_api_url(self) -> str:
        return "api/open/color/base/list"

    def get_request_type(self) -> str:
        return "GET"


@dataclass
class ColorBaseDetailRequest(BaseRequest[ColorBaseDetailResponse]):
    color_id: Optional[int] = None

    def response_class(self) -> Type[ColorBaseDetailResponse]:
        return ColorBaseDetailResponse

    def get_api_url(self) -> str:
        return "api/open/color/base/get"

    def get_request_type(self) -> str:
        return "GET"