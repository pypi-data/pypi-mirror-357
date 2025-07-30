# Примеры использования OzonProductListAPI (async/await)

## Получить список товаров
```python
from ozon_api import OzonAPI
import asyncio

async def main():
    api = OzonAPI(client_id="...", api_key="...")
    body = {...}  # параметры фильтрации и пагинации
    result = await api.product_list(body)
    print(result)

asyncio.run(main())
```

## Получить лимиты по товарам
```python
async def main():
    api = OzonAPI(client_id="...", api_key="...")
    result = await api.product_info_limit()
    print(result)

asyncio.run(main()) 