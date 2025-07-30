from dataclasses import dataclass
from typing import Type, Optional, List

from .base import BaseRequest, BaseResponse, PageRequest, PageResponse

# #################################################################
# Storehouse
# #################################################################


@dataclass
class StorehouseDetail:
    id: Optional[int] = None
    name: Optional[str] = None
    type: Optional[str] = None


@dataclass
class StorehouseListResponse(PageResponse):
    data: Optional[List[StorehouseDetail]] = None


@dataclass
class StorehouseListRequest(PageRequest[StorehouseListResponse]):
    name: Optional[str] = None

    @property
    def response_class(self) -> Type[StorehouseListResponse]:
        return StorehouseListResponse

    @property
    def api_url(self) -> str:
        return "api/open/storehouse/base/list"

    def get_request_type(self) -> str:
        return "GET" 