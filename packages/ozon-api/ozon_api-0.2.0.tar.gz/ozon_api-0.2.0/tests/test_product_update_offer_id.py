import os
import pytest
from dotenv import load_dotenv
from ozon_api import OzonAPI
from ozon_api.models.product_update_offer_id import ProductUpdateOfferIdRequest, ProductUpdateOfferIdItem, ProductUpdateOfferIdResponse

load_dotenv()

@pytest.mark.asyncio
async def test_product_update_offer_id():
    api = OzonAPI(
        client_id=os.getenv("OZON_CLIENT_ID"),
        api_key=os.getenv("OZON_CLIENT_SECRET")
    )
    items = [ProductUpdateOfferIdItem(offer_id="ead01360c544e1cb4fae0aefe2b593e8", new_offer_id="ead01360c544e1cb4fae0aefe2b593e8new")]  # Замените на валидные значения
    request = ProductUpdateOfferIdRequest(update_offer_id=items)
    response = await api.product_update_offer_id(request)
    assert isinstance(response, ProductUpdateOfferIdResponse)
    assert hasattr(response, 'errors') 