import os
import pytest
from dotenv import load_dotenv
from ozon_api import OzonAPI
from ozon_api.models.product_list import ProductListRequest, ProductListFilter, ProductListResponse, ProductListResult

load_dotenv()

@pytest.mark.asyncio
async def test_product_list():
    api = OzonAPI(
        client_id=os.getenv("OZON_CLIENT_ID"),
        api_key=os.getenv("OZON_CLIENT_SECRET")
    )
    filter = ProductListFilter()  # Заполните фильтр при необходимости
    request = ProductListRequest(filter=filter)
    response = await api.product_list(request)
    print(response)
    assert isinstance(response, ProductListResult)
    assert hasattr(response, 'result')
    assert hasattr(response.result, 'items')
    assert hasattr(response.result, 'total')

@pytest.mark.asyncio
async def test_product_info_limit():
    api = OzonAPI(
        client_id=os.getenv("OZON_CLIENT_ID"),
        api_key=os.getenv("OZON_CLIENT_SECRET")
    )
    response = await api.product_info_limit()
    assert isinstance(response, dict) 