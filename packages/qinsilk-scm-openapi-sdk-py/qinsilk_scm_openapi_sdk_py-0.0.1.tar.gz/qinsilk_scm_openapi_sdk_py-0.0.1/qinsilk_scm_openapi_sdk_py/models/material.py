from dataclasses import dataclass
from typing import Type, Optional, List
from decimal import Decimal

from .base import BaseRequest, BaseResponse, PageRequest, PageResponse

# #################################################################
# Material Base
# #################################################################


@dataclass
class MaterialDetail:
    name: Optional[str] = None
    type: Optional[int] = None
    type_id: Optional[int] = None
    sn: Optional[str] = None
    barcode: Optional[str] = None
    category_id: Optional[int] = None
    unit_id: Optional[int] = None
    price: Optional[Decimal] = None
    composition: Optional[str] = None
    post_process: Optional[str] = None
    part: Optional[str] = None
    fabric_width: Optional[Decimal] = None
    gram_weight: Optional[Decimal] = None
    qunce: Optional[Decimal] = None
    roll_weight: Optional[Decimal] = None
    net_weight: Optional[Decimal] = None
    meter_output: Optional[Decimal] = None
    paper_bucket: Optional[Decimal] = None
    empty_gap: Optional[Decimal] = None
    empty_gap_rate: Optional[Decimal] = None
    default_supplier_id: Optional[int] = None
    supplier_sn: Optional[str] = None
    multiplying_power: Optional[Decimal] = None
    round_way: Optional[int] = None
    state: Optional[int] = None
    remark: Optional[str] = None
    img_url: Optional[str] = None
    enable_property: Optional[int] = None
    enable_sku: Optional[int] = None
    enable_sku_price: Optional[int] = None
    handler_id: Optional[int] = None
    last_handler_id: Optional[int] = None
    loss_rate: Optional[Decimal] = None
    shrink_rate: Optional[Decimal] = None
    fabric_type: Optional[int] = None
    loss_rate_stair_enable: Optional[int] = None
    loss_rate_stair_type: Optional[int] = None


@dataclass
class MaterialListResponse(PageResponse):
    data: Optional[List[MaterialDetail]] = None


@dataclass
class MaterialListRequest(PageRequest[MaterialListResponse]):
    material_sn: Optional[str] = None

    def response_class(self) -> Type[MaterialListResponse]:
        return MaterialListResponse

    def get_api_url(self) -> str:
        return "api/open/material/base/list"

    def get_request_type(self) -> str:
        return "GET"


@dataclass
class MaterialDetailResponse(BaseResponse):
    data: Optional[MaterialDetail] = None


@dataclass
class MaterialDetailRequest(BaseRequest[MaterialDetailResponse]):
    material_id: Optional[int] = None

    def response_class(self) -> Type[MaterialDetailResponse]:
        return MaterialDetailResponse

    def get_api_url(self) -> str:
        return "api/open/material/base/get"

    def get_request_type(self) -> str:
        return "GET"


# #################################################################
# Material Purchase
# #################################################################


@dataclass
class MaterialPurchaseDetail:
    orders_sn: Optional[str] = None
    group_orders_sn: Optional[str] = None
    count_rule: Optional[int] = None
    supplier_id: Optional[int] = None
    storehouse_id: Optional[int] = None
    payment: Optional[Decimal] = None
    total_wipe_zero: Optional[Decimal] = None
    account_id: Optional[int] = None
    remark: Optional[str] = None
    submitter_id: Optional[int] = None
    handler_id: Optional[int] = None
    last_handler_id: Optional[int] = None
    state: Optional[int] = None
    business_time: Optional[str] = None
    expect_time: Optional[str] = None
    is_direct_store_in: Optional[int] = None
    is_from_material_demand: Optional[int] = None
    is_direct_pick: Optional[int] = None
    is_direct_pick_store_out: Optional[int] = None
    direct_completed_when_finish: Optional[int] = None


@dataclass
class MaterialPurchaseListResponse(PageResponse):
    data: Optional[List[MaterialPurchaseDetail]] = None


@dataclass
class MaterialPurchaseListRequest(PageRequest[MaterialPurchaseListResponse]):
    order_sn: Optional[str] = None

    def response_class(self) -> Type[MaterialPurchaseListResponse]:
        return MaterialPurchaseListResponse

    def get_api_url(self) -> str:
        return "api/open/material/purchase/list"

    def get_request_type(self) -> str:
        return "GET"


@dataclass
class MaterialPurchaseDetailResponse(BaseResponse):
    data: Optional[MaterialPurchaseDetail] = None


@dataclass
class MaterialPurchaseDetailRequest(BaseRequest[MaterialPurchaseDetailResponse]):
    purchase_id: Optional[int] = None

    def response_class(self) -> Type[MaterialPurchaseDetailResponse]:
        return MaterialPurchaseDetailResponse

    def get_api_url(self) -> str:
        return "api/open/material/purchase/get"

    def get_request_type(self) -> str:
        return "GET" 