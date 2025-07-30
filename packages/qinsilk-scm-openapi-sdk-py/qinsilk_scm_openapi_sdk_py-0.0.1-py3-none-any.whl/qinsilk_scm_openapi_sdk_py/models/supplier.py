from dataclasses import dataclass
from typing import Optional, List, Type

from .base import BaseRequest, PageRequest, BaseResponse, PageResponse


@dataclass
class SupplierSaveDTO:
    supplier_name: str
    supplier_type: str
    status: int
    id: Optional[int] = None
    code: Optional[str] = None
    supplier_name_py: Optional[str] = None
    virtual_storehouse_id: Optional[int] = None
    cellphone: Optional[str] = None
    level_id: Optional[int] = None
    province_id: Optional[int] = None
    city_id: Optional[int] = None
    county_id: Optional[int] = None
    address: Optional[str] = None
    show_order: Optional[int] = None
    remark: Optional[str] = None
    bank: Optional[str] = None
    bank_account: Optional[str] = None
    bank_account_id: Optional[str] = None
    bank_remark: Optional[str] = None


@dataclass
class SupplierDetail:
    id: Optional[int] = None
    supplier_name: Optional[str] = None
    code: Optional[str] = None
    supplier_name_py: Optional[str] = None
    supplier_type: Optional[str] = None
    virtual_storehouse: Optional[str] = None
    virtual_storehouse_id: Optional[int] = None
    cellphone: Optional[str] = None
    level_id: Optional[int] = None
    province_id: Optional[int] = None
    city_id: Optional[int] = None
    county_id: Optional[int] = None
    address: Optional[str] = None
    show_order: Optional[int] = None
    status: Optional[int] = None
    remark: Optional[str] = None
    bank: Optional[str] = None
    bank_account: Optional[str] = None
    bank_account_id: Optional[str] = None
    bank_remark: Optional[str] = None


@dataclass
class SupplierDetailResponse(BaseResponse):
    data: Optional[SupplierDetail] = None


@dataclass
class SupplierListResponse(PageResponse):
    data: Optional[List[SupplierDetail]] = None


@dataclass
class SupplierSaveRequest(BaseRequest):
    supplier_save_dto: Optional[SupplierSaveDTO] = None

    def response_class(self) -> Type[SupplierDetailResponse]:
        return SupplierDetailResponse

    def get_api_url(self) -> str:
        return 'api/open/supplier/base/add'


@dataclass
class SupplierDetailRequest(BaseRequest):
    supplier_id: Optional[int] = None

    def response_class(self) -> Type[SupplierDetailResponse]:
        return SupplierDetailResponse

    def get_api_url(self) -> str:
        return 'api/open/supplier/base/get'


@dataclass
class SupplierListRequest(PageRequest):
    supplier_name: Optional[str] = None
    code: Optional[str] = None

    def response_class(self) -> Type[SupplierListResponse]:
        return SupplierListResponse

    def get_api_url(self) -> str:
        return 'api/open/supplier/base/list' 