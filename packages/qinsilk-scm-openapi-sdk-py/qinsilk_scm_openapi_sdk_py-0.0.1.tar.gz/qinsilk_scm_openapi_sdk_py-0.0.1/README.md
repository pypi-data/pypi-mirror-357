# Qinsilk SCM OpenAPI SDK (Python)

本项目是 `qinsilk-scm-openapi-sdk` Java 项目的 Python 实现版本，提供了一个用于与 Qinsilk SCM OpenAPI 交互的客户端。

## 安装

您可以通过 pip 直接安装本 SDK：

```bash
pip install qinsilk-scm-openapi-sdk-py
```

## 使用方法

### 初始化客户端

SDK 的核心是 `OpenClient`。您需要使用包含您的凭据的 `OpenConfig` 对象来初始化它。

```python
from qinsilk_scm_openapi_sdk_py import OpenClient, OpenConfig

# 配置您的客户端ID、密钥和服务器地址
config = OpenConfig(
    client_id="your_client_id",
    client_secret="your_client_secret",
    server_url="https://your.api.server/"
)

client = OpenClient(config)
```

> **建议**：您也可以通过环境变量来配置 `OpenConfig`，以避免在代码中硬编码敏感信息。
> `OpenConfig` 会自动从环境变量中读取这些值。
>
> - `SCM_CLIENT_ID`: 您的客户端 ID
> - `SCM_CLIENT_SECRET`: 您的客户端密钥
> - `SCM_SERVER_URL`: 您的 API 服务器地址

### 发起 API 调用

要发起一个 API 调用，您需要创建一个继承自 `BaseRequest` 的请求对象。

例如，要获取商品列表，您可以创建一个 `GetProductListRequest` 类：

```python
from dataclasses import dataclass
from qinsilk_scm_openapi_sdk_py import BaseRequest, BaseResponse, OpenException
from typing import Type, List

@dataclass
class Product:
    id: str
    name: str

@dataclass
class GetProductListResponse(BaseResponse):
    products: List[Product]

@dataclass
class GetProductListRequest(BaseRequest[GetProductListResponse]):
    page: int = 1
    page_size: int = 10

    @property
    def response_class(self) -> Type[GetProductListResponse]:
        return GetProductListResponse

    @property
    def api_url(self) -> str:
        return "api/products/list"

    def get_request_type(self) -> str:
        return "GET"

# 执行请求
try:
    product_request = GetProductListRequest(page=1)
    _, response = client.execute(product_request)

    if response.is_success():
        for product in response.products:
            print(f"商品: {product.name}")

except OpenException as e:
    print(f"发生错误: {e}")

```

`GetProductListRequest` 只是一个示例，您可以根据需要为其他接口扩展 SDK。

## 项目结构

- `qinsilk_scm_openapi_sdk_py/` (项目根目录)
  - `qinsilk_scm_openapi_sdk_py/`: Python 包目录。
    - `client.py`: 包含 `OpenClient` 和 `OpenConfig`。
    - `models/`: 包含 `BaseRequest`, `BaseResponse` 以及其他数据模型。
    - `signing.py`: 处理 API 请求签名。
    - `exceptions.py`: 自定义异常。
  - `examples/`: 用法示例脚本。
  - `README.md`: 本文档。

## 打包命令

```
python -m pip install --upgrade setuptools wheel twine
python setup.py sdist bdist_wheel
```

## 上传命令

```
 twine upload dist/*
```
