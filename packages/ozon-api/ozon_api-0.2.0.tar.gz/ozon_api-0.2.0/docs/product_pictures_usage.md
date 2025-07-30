# Примеры использования OzonProductPicturesAPI (async/await)

## Импорт изображений товаров
```python
from ozon_api import OzonAPI
import asyncio

async def main():
    api = OzonAPI(client_id="...", api_key="...")
    items = {...}  # данные для загрузки изображений
    result = await api.product_pictures_import(items)
    print(result)

asyncio.run(main())
```

## Получить статус обработки изображений
```python
async def main():
    api = OzonAPI(client_id="...", api_key="...")
    product_ids = [12345, 67890]
    result = await api.product_pictures_info(product_ids)
    print(result)

asyncio.run(main()) 