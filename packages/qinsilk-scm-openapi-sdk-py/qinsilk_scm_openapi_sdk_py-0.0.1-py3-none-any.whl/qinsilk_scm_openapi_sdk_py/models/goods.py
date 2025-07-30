from dataclasses import dataclass
from typing import Type, Optional, List
from decimal import Decimal
from datetime import datetime

from .base import BaseRequest, BaseResponse, PageRequest, PageResponse

# #################################################################
# Goods Base
# #################################################################


@dataclass
class GoodsPrice:
    type: Optional[str] = None
    price: Optional[Decimal] = None


@dataclass
class SkuDetail:
    sku_id: Optional[int] = None
    color_id: Optional[int] = None
    size_id: Optional[int] = None
    sku_bar_code: Optional[str] = None


@dataclass
class GoodsDetail:
    id: Optional[int] = None
    goods_name: Optional[str] = None
    design_sn: Optional[str] = None
    sex: Optional[int] = None
    style_id: Optional[int] = None
    season_id: Optional[int] = None
    year: Optional[str] = None
    month: Optional[int] = None
    ranges_id: Optional[int] = None
    silhouette: Optional[str] = None
    designer: Optional[int] = None
    pattern_maker_id: Optional[int] = None
    remark: Optional[str] = None
    price_list: Optional[List[GoodsPrice]] = None
    sku_list: Optional[List[SkuDetail]] = None


@dataclass
class GoodsListDetail:
    id: Optional[int] = None
    goods_name: Optional[str] = None
    design_sn: Optional[str] = None
    sex: Optional[int] = None
    style_id: Optional[int] = None
    season_id: Optional[int] = None
    year: Optional[str] = None
    month: Optional[int] = None
    ranges_id: Optional[int] = None
    silhouette: Optional[str] = None
    designer: Optional[int] = None
    pattern_maker_id: Optional[int] = None
    remark: Optional[str] = None


@dataclass
class GoodsListResponse(PageResponse):
    data: Optional[List[GoodsListDetail]] = None


@dataclass
class GoodsListRequest(PageRequest[GoodsListResponse]):
    goods_sn: Optional[str] = None
    design_sn: Optional[str] = None
    custom_design_sn: Optional[str] = None

    def response_class(self) -> Type[GoodsListResponse]:
        return GoodsListResponse

    def get_api_url(self) -> str:
        return "api/open/goods/base/list"

    def get_request_type(self) -> str:
        return "GET"


@dataclass
class GoodsDetailResponse(BaseResponse):
    data: Optional[GoodsDetail] = None


@dataclass
class GoodsDetailRequest(BaseRequest[GoodsDetailResponse]):
    goods_id: Optional[int] = None

    def response_class(self) -> Type[GoodsDetailResponse]:
        return GoodsDetailResponse

    def get_api_url(self) -> str:
        return "api/open/goods/base/get"

    def get_request_type(self) -> str:
        return "GET"


@dataclass
class GoodsSkuDTO:
    color_id: int
    size_id: int
    sku_bar_code: Optional[str] = None
    is_disable: Optional[int] = None
    enable_sku_storage_location: Optional[int] = None
    color_name: Optional[str] = None
    sex_name: Optional[str] = None
    size_name: Optional[str] = None
    color_show_order: Optional[int] = None
    size_show_order: Optional[int] = None
    cost_price: Optional[Decimal] = None
    goods_name: Optional[str] = None
    goods_sn: Optional[str] = None
    goods_img_url: Optional[str] = None
    stored_number: Optional[int] = None
    win_number: Optional[int] = None
    wout_number: Optional[int] = None
    available_number: Optional[int] = None
    produce_in_number: Optional[Decimal] = None
    tag_price: Optional[Decimal] = None
    retail_price_area: Optional[Decimal] = None
    retail_price_factory: Optional[Decimal] = None
    trade_price: Optional[Decimal] = None
    is_on_sale: Optional[int] = None
    year: Optional[str] = None
    category_name: Optional[str] = None
    bland_name: Optional[str] = None
    season_name: Optional[str] = None
    ranges_name: Optional[str] = None
    designer_name: Optional[str] = None
    style_name: Optional[str] = None
    create_by: Optional[str] = None
    update_by: Optional[str] = None
    handler_name: Optional[str] = None
    last_handler_name: Optional[str] = None
    factory_name: Optional[str] = None
    factory_code: Optional[str] = None
    execute_standard_id: Optional[int] = None
    security_type_id: Optional[int] = None
    security_type_name: Optional[str] = None
    execute_standard_name: Optional[str] = None
    pattern_maker_name: Optional[str] = None
    follower_name: Optional[str] = None
    design_sn: Optional[str] = None
    remark: Optional[str] = None
    sex: Optional[str] = None
    supplier_sn: Optional[str] = None
    dev_time: Optional[datetime] = None
    client_name: Optional[str] = None
    follower_id: Optional[int] = None
    is_sealed_sample: Optional[int] = None
    factory_id: Optional[int] = None
    pattern_maker_id: Optional[int] = None
    designer: Optional[int] = None
    is_binding_jst: Optional[bool] = None
    is_binding_km: Optional[bool] = None
    gram_weight: Optional[Decimal] = None
    composition: Optional[str] = None
    goods_bar_code: Optional[str] = None
    sku_code: Optional[str] = None
    currency_name: Optional[str] = None
    currency_code: Optional[str] = None
    currency_symbol: Optional[str] = None
    currency_price: Optional[Decimal] = None
    size_model_dt_name: Optional[str] = None
    custom_design_sn: Optional[str] = None
    sample_source: Optional[int] = None
    month: Optional[int] = None


@dataclass
class GoodsSaveDTO:
    show_order: int
    is_sealed_sample: Optional[int] = None
    retail_price_area: Optional[Decimal] = None
    trade_price: Optional[Decimal] = None
    goods_sn: Optional[str] = None
    design_sn: Optional[str] = None
    name: Optional[str] = None
    sample_source: Optional[int] = None
    supplier_sn: Optional[str] = None
    dev_time: Optional[datetime] = None
    client_id: Optional[int] = None
    plan_id: Optional[int] = None
    bland_id: Optional[int] = None
    category_id: Optional[int] = None
    execute_standard_id: Optional[int] = None
    security_type_id: Optional[int] = None
    sex: Optional[int] = None
    style_id: Optional[int] = None
    season_id: Optional[int] = None
    year: Optional[str] = None
    ranges_id: Optional[int] = None
    silhouette: Optional[str] = None
    designer: Optional[int] = None
    pattern_maker_id: Optional[int] = None
    is_on_sale: Optional[int] = None
    remark: Optional[str] = None
    tag_price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    retail_price_factory: Optional[Decimal] = None
    bar_code: Optional[str] = None
    img_url: Optional[str] = None
    size_len_display: Optional[int] = None
    handler_id: Optional[int] = None
    follower_id: Optional[int] = None
    enable_sku_bar_code: Optional[int] = None
    enable_sku_storage_location: Optional[int] = None
    gram_weight: Optional[Decimal] = None
    composition: Optional[str] = None
    bom_state: Optional[int] = None
    factory_id: Optional[int] = None
    month: Optional[int] = None
    warn_number_top: Optional[int] = None
    warn_number_low: Optional[int] = None
    tag: Optional[str] = None
    grade: Optional[str] = None
    is_sample: Optional[int] = None
    bulk_goods_state: Optional[int] = None
    make_sample_state: Optional[int] = None
    review_state: Optional[int] = None
    design_order_id: Optional[int] = None


@dataclass
class GoodsSaveRequest(BaseRequest[GoodsDetailResponse]):
    goods_save_dto: Optional['GoodsSaveDTO'] = None

    def response_class(self) -> Type[GoodsDetailResponse]:
        return GoodsDetailResponse

    def get_api_url(self) -> str:
        return "api/open/goods/base/add"

    def get_request_type(self) -> str:
        return "POST" 