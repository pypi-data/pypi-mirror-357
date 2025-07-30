# import os
# import pytest
# from dotenv import load_dotenv
# from ozon_api import OzonAPI

# load_dotenv()

# @pytest.mark.asyncio
# async def test_product_pictures_import():
#     api = OzonAPI(
#         client_id=os.getenv("OZON_CLIENT_ID"),
#         api_key=os.getenv("OZON_CLIENT_SECRET")
#     )
#     items = {}  # Заполните валидными данными
#     response = await api.product_pictures_import(items)
#     assert isinstance(response, dict)

# @pytest.mark.asyncio
# async def test_product_pictures_info():
#     api = OzonAPI(
#         client_id=os.getenv("OZON_CLIENT_ID"),
#         api_key=os.getenv("OZON_CLIENT_SECRET")
#     )
#     product_id = ["1"]  # Замените на валидные product_id
#     response = await api.product_pictures_info(product_id)
#     assert isinstance(response, dict) 