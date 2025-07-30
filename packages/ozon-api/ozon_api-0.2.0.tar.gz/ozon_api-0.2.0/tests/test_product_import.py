import os
import pytest
from dotenv import load_dotenv
from ozon_api import OzonAPI
from ozon_api.models.product_import import ProductImport, ProductImport_Item, ProductImport_Item_Attribute
from ozon_api.models.import_by_sku import ImportBySku, ImportBySku_Item
from ozon_api.models.product_import_info import ProductImportInfo
from ozon_api.models.product_attributes_update import ProductAttributesUpdate, ProductAttributesUpdate_Item

load_dotenv()

# @pytest.mark.asyncio
# async def test_product_import():
#     api = OzonAPI(
#         client_id=os.getenv("OZON_CLIENT_ID"),
#         api_key=os.getenv("OZON_CLIENT_SECRET")
#     )
#     items = []
#     request = ProductImport(items=items)
#     response = await api.product_import(request)
#     assert isinstance(response, dict)

# @pytest.mark.asyncio
# async def test_product_import_info():
#     api = OzonAPI(
#         client_id=os.getenv("OZON_CLIENT_ID"),
#         api_key=os.getenv("OZON_CLIENT_SECRET")
#     )
#     request = ProductImportInfo(task_id=1)  # Замените на валидный task_id
#     response = await api.product_import_info(request)
#     assert isinstance(response, dict)

# @pytest.mark.asyncio
# async def test_product_import_by_sku():
#     api = OzonAPI(
#         client_id=os.getenv("OZON_CLIENT_ID"),
#         api_key=os.getenv("OZON_CLIENT_SECRET")
#     )
#     items = [
#         ImportBySku_Item(
#             name="Cordiant 123 test",
#             offer_id="dd23c5d28617c627f0ff7af49d3d5e8atest",
#             old_price="100",
#             price="100",
#             sku=2275512605,
#             vat="0.2",
#             currency_code="RUB",
#         )
#     ]  # Заполните валидными ImportBySku_Item
#     request = ImportBySku(items=items)
#     response = await api.product_import_by_sku(request)
#     assert isinstance(response, dict)

# @pytest.mark.asyncio
# async def test_product_attributes_update():
#     api = OzonAPI(
#         client_id=os.getenv("OZON_CLIENT_ID"),
#         api_key=os.getenv("OZON_CLIENT_SECRET")
#     )
#     items = []  # Заполните валидными ProductAttributesUpdate_Item
#     request = ProductAttributesUpdate(items=items)
#     response = await api.product_attributes_update(request)
#     assert isinstance(response, dict) 