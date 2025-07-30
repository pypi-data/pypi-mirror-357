# Примеры использования OzonProductImportAPI (async/await)

## Импорт товаров
```python
from ozon_api import OzonAPI
import asyncio

async def main():
    api = OzonAPI(client_id="...", api_key="...")
    items = [...]  # список товаров
    result = await api.product_import(items)
    print(result)

asyncio.run(main())
```

## Получить статус задачи импорта
```python
async def main():
    api = OzonAPI(client_id="...", api_key="...")
    result = await api.product_import_info(task=123456)
    print(result)

asyncio.run(main())
```

## Импорт по SKU
```python
async def main():
    api = OzonAPI(client_id="...", api_key="...")
    items = {...}  # данные для импорта по SKU
    result = await api.product_import_by_sku(items)
    print(result)

asyncio.run(main())
```

## Обновление атрибутов товара
```python
async def main():
    api = OzonAPI(client_id="...", api_key="...")
    items = {...}  # данные для обновления атрибутов
    result = await api.product_attributes_update(items)
    print(result)

asyncio.run(main())
``` 