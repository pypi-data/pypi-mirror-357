import os
import pytest
from dotenv import load_dotenv
from ozon_api import OzonAPI
from ozon_api.models.product_rating import ProductRatingRequest, ProductRatingResponse

load_dotenv()

@pytest.mark.asyncio
async def test_product_rating_by_sku():
    api = OzonAPI(
        client_id=os.getenv("OZON_CLIENT_ID"),
        api_key=os.getenv("OZON_CLIENT_SECRET")
    )
    request = ProductRatingRequest(skus=[2275512533, 2275511816])  # Замените на реальные SKU
    response = await api.product_rating_by_sku(request)
    assert isinstance(response, ProductRatingResponse)
    assert hasattr(response, 'products')
    for product in response.products:
        assert hasattr(product, 'sku')
        assert hasattr(product, 'rating')
        assert hasattr(product, 'groups') 