# Примеры использования OzonProductArchiveAPI (async/await)

## Архивировать товары
```python
from ozon_api import OzonAPI
import asyncio

async def main():
    api = OzonAPI(client_id="...", api_key="...")
    product_ids = [12345, 67890]
    result = await api.product_archive(product_ids)
    print(result)

asyncio.run(main())
```

## Разархивировать товары
```python
async def main():
    api = OzonAPI(client_id="...", api_key="...")
    product_ids = [12345, 67890]
    result = await api.product_unarchive(product_ids)
    print(result)

asyncio.run(main()) 