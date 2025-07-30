import logging
import re
import time
import json
from dataclasses import dataclass, asdict, fields, is_dataclass
from typing import Tuple, TypeVar, Union, get_origin, get_args, List

import requests
from requests.exceptions import Timeout

from .exceptions import OpenException, ErrorCode
from .models import BaseRequest, BaseResponse, ClientTokenRequest, ClientTokenResponse
from .signing import sign_top_request, SIGN_METHOD_HMAC_SHA256

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseResponse)


def _to_snake_case(name: str) -> str:
    """Converts a camelCase string to snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def _to_camel_case(snake_str: str) -> str:
    """Converts a snake_case string to camelCase."""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def _recursively_parse_and_convert_to_snake_case(obj):
    """Recursively converts dict keys to snake_case and parses JSON strings."""
    if isinstance(obj, dict):
        return {_to_snake_case(k): _recursively_parse_and_convert_to_snake_case(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_recursively_parse_and_convert_to_snake_case(v) for v in obj]
    if isinstance(obj, str):
        try:
            # Try to parse string values that might be JSON
            if (obj.startswith('{') and obj.endswith('}')) or \
               (obj.startswith('[') and obj.endswith(']')):
                
                parsed_obj = json.loads(obj)
                # After parsing, recursively process the new object
                return _recursively_parse_and_convert_to_snake_case(parsed_obj)
        except (json.JSONDecodeError, TypeError):
            # Not a JSON string or not a string at all, leave it as is
            pass
    return obj


def _instantiate_dataclass_recursively(cls, data):
    """Recursively instantiates a dataclass from a dictionary."""
    if not is_dataclass(cls) or not isinstance(data, dict):
        return data

    kwargs = {}
    cls_fields = {f.name: f.type for f in fields(cls)}
    for name, value in data.items():
        if name in cls_fields:
            field_type = cls_fields[name]
            is_optional = get_origin(field_type) is Union and type(None) in get_args(field_type)
            if is_optional:
                field_type = get_args(field_type)[0]

            origin = get_origin(field_type)
            if origin in (list, List) and isinstance(value, list):
                item_type = get_args(field_type)[0]
                kwargs[name] = [_instantiate_dataclass_recursively(item_type, item) for item in value]
            elif is_dataclass(field_type) and isinstance(value, dict):
                kwargs[name] = _instantiate_dataclass_recursively(field_type, value)
            else:
                kwargs[name] = value

    return cls(**kwargs)


def _clean_and_convert_dict(d, convert_to_camel=True):
    """Recursively converts dict keys to camelCase and removes None values."""
    if isinstance(d, dict):
        clean_dict = {}
        for k, v in d.items():
            if v is None:
                continue
            cleaned_v = _clean_and_convert_dict(v, convert_to_camel)
            if cleaned_v is not None:
                key = _to_camel_case(k) if convert_to_camel else k
                clean_dict[key] = cleaned_v
        return clean_dict
    elif isinstance(d, list):
        return [_clean_and_convert_dict(item, convert_to_camel) for item in d if item is not None]
    return d


@dataclass
class OpenConfig:
    client_id: str
    client_secret: str
    server_url: str
    connect_timeout: int = 3  # seconds
    read_timeout: int = 10    # seconds
    access_token: str = None


class OpenClient:
    def __init__(self, open_config: OpenConfig):
        self.open_config = open_config
        self.http_session = requests.Session()

    def execute(self, request: BaseRequest[T]) -> Tuple[requests.Request, T]:
        if request.timestamp is None:
            request.timestamp = int(time.time() * 1000)

        if request.is_need_token():
            if not self.open_config.access_token:
                 self.open_config.access_token = self.get_client_token()
            request.access_token = self.open_config.access_token

        params_snake = asdict(request)
        # remove None values and convert keys to camelCase, recursively
        if request.get_api_url() == "api/oauth2/client_token":
            params_camel = _clean_and_convert_dict(params_snake, convert_to_camel=False)
        else:
            params_camel = _clean_and_convert_dict(params_snake)
        
        search_params = {}
        
        sign = sign_top_request(params_camel, self.open_config.client_secret, SIGN_METHOD_HMAC_SHA256)
        search_params["sign"] = sign
        search_params["sign_method"] = SIGN_METHOD_HMAC_SHA256
        if request.access_token:
            search_params["access_token"] = request.access_token
            
        logger.info("Built request params: %s", params_camel)
        logger.info("Generated signature: %s", sign)

        full_url = self.build_request_url(request.get_api_url(), {})
        
        req = requests.Request(
            method=request.get_request_type(),
            url=full_url,
        )

        if request.get_request_type() == "GET":
            # In GET requests, all params go into the query string
            get_params = params_camel.copy()
            get_params.update(search_params)
            req.params = get_params
        elif request.get_request_type() == "POST":
             # In POST requests, only search_params go into query string
             req.params = search_params
             req.json = params_camel


        prepared_request = self.http_session.prepare_request(req)
        logger.info("Full request URL: %s", prepared_request.url)
        
        try:
            http_response = self.http_session.send(
                prepared_request,
                timeout=(self.open_config.connect_timeout, self.open_config.read_timeout)
            )
            http_response.raise_for_status()
            
            response_body = http_response.json()

            snake_case_response_body = _recursively_parse_and_convert_to_snake_case(response_body)
            
            print(snake_case_response_body)
            response_cls = request.response_class()
            response_data = _instantiate_dataclass_recursively(response_cls, snake_case_response_body)
            
            return prepared_request, response_data

        except Timeout:
            raise OpenException(ErrorCode.READ_TIMEOUT)
        except requests.exceptions.ConnectionError:
            raise OpenException(ErrorCode.CONNECT_TIMEOUT)
        except requests.exceptions.RequestException as e:
            logger.error("HTTP request failed: %s", e)
            raise OpenException(ErrorCode.UNKNOWN_ERROR, exception=e)


    def get_client_token(self) -> str:
        token_request = ClientTokenRequest(
            client_id=self.open_config.client_id,
            client_secret=self.open_config.client_secret
        )
        _, response = self.execute(token_request)
        if response.is_success() and response.client_token:
            self.open_config.access_token = response.client_token
            return response.client_token
        else:
            raise OpenException(ErrorCode.INVALID_RESPONSE, exception=response)

    def build_request_url(self, api_method: str, params: dict) -> str:
        base_url = self.open_config.server_url
        url = f"{base_url.rstrip('/')}/{api_method.lstrip('/')}"
        return url