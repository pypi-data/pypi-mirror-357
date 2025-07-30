from dataclasses import dataclass, field, fields, is_dataclass
from typing import Type, TypeVar, Generic, Optional, List, get_origin, get_args, Union
import time

from ..exceptions import OpenException

T = TypeVar('T', bound='BaseResponse')


@dataclass
class BaseResponse:
    code: str = "0"
    exception: Optional[OpenException] = None

    def is_success(self) -> bool:
        return self.code == "0"


@dataclass
class Pager:
    page_no: int = 1
    page_size: int = 18
    total_count: int = 0
    page_count: int = 0
    first_no: int = 0


@dataclass
class PageResponse(BaseResponse):
    page: Optional[Pager] = None


@dataclass
class BaseRequest(Generic[T]):
    access_token: Optional[str] = None
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
    version: str = "1.0"

    def is_need_token(self) -> bool:
        return True

    def get_request_type(self) -> str:
        return "POST"

    def response_class(self) -> Type[T]:
        raise NotImplementedError

    def get_api_url(self) -> str:
        raise NotImplementedError


@dataclass
class QueryOrderByDTO:
    sidx: str
    sord: str


@dataclass
class PageRequest(BaseRequest[T]):
    page: int = 1
    size: int = 10
    order_by_list: Optional[List[QueryOrderByDTO]] = None


@dataclass
class ClientTokenResponse(BaseResponse):
    token_type: Optional[str] = None
    client_token: Optional[str] = None
    expires_in: Optional[int] = None


@dataclass
class ClientTokenRequest(BaseRequest[ClientTokenResponse]):
    grant_type: str = "client_credentials"
    client_id: Optional[str] = None
    client_secret: Optional[str] = None

    def is_need_token(self) -> bool:
        return False

    def get_request_type(self) -> str:
        return "GET"

    def response_class(self) -> Type[ClientTokenResponse]:
        return ClientTokenResponse

    def get_api_url(self) -> str:
        return "api/oauth2/client_token" 