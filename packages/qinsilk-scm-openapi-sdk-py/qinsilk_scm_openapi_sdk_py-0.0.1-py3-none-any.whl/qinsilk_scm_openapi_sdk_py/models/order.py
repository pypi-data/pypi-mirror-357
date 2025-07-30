from dataclasses import dataclass
from typing import Type, Optional, List
from decimal import Decimal
from datetime import datetime

from ..models import PageRequest, PageResponse, BaseResponse, BaseRequest

# #################################################################
# Produce Order
# #################################################################


@dataclass
class ProduceOrderDetail:
    orders_sn: Optional[str] = None
    produce_batch_sn: Optional[str] = None
    type: Optional[int] = None
    storehouse_id: Optional[int] = None
    supplier_id: Optional[int] = None
    business_time: Optional[datetime] = None
    delivery_time: Optional[datetime] = None
    contract_time: Optional[datetime] = None
    follower_id: Optional[int] = None
    client_id: Optional[int] = None
    account_id: Optional[int] = None
    purchase_price: Optional[Decimal] = None
    total_produce_in_number: Optional[Decimal] = None
    order_type: Optional[int] = None
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    state: Optional[int] = None
    cut_bed_state: Optional[int] = None
    store_in_state: Optional[int] = None
    is_purchase_order_sn: Optional[str] = None
    handler_id: Optional[int] = None
    last_handler_id: Optional[int] = None
    remark: Optional[str] = None
    custom_design_sn: Optional[str] = None
    produce_description: Optional[str] = None
    purchase_description: Optional[str] = None
    source: Optional[int] = None
    estimate_begin_time: Optional[datetime] = None
    bom_state: Optional[int] = None
    material_storehouse_id: Optional[int] = None
    pattern_designer_id: Optional[int] = None
    last_process: Optional[str] = None
    pmc_user_id: Optional[int] = None
    purchase_user_id: Optional[int] = None
    online_sn: Optional[str] = None
    pay_time: Optional[datetime] = None


@dataclass
class ProduceOrderListResponse(PageResponse):
    data: Optional[List[ProduceOrderDetail]] = None


@dataclass
class ProduceOrderListRequest(PageRequest[ProduceOrderListResponse]):
    order_sn: Optional[str] = None

    @property
    def response_class(self) -> Type[ProduceOrderListResponse]:
        return ProduceOrderListResponse

    @property
    def api_url(self) -> str:
        return "api/open/order/produce/list"

    def get_request_type(self) -> str:
        return "GET"


@dataclass
class ProduceOrderDetailResponse(BaseResponse):
    data: Optional[ProduceOrderDetail] = None


@dataclass
class ProduceOrderDetailRequest(BaseRequest[ProduceOrderDetailResponse]):
    order_sn: str

    @property
    def response_class(self) -> Type[ProduceOrderDetailResponse]:
        return ProduceOrderDetailResponse

    @property
    def api_url(self) -> str:
        return "api/open/order/produce/get"

    def get_request_type(self) -> str:
        return "GET" 