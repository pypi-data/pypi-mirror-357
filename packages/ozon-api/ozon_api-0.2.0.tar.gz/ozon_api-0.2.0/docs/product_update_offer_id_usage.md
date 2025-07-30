# Примеры использования OzonProductUpdateOfferIdAPI (async/await)

## Обновить offer_id товаров
```python
from ozon_api import OzonAPI
import asyncio

async def main():
    api = OzonAPI(client_id="...", api_key="...")
    items = {...}  # данные для обновления offer_id
    result = await api.product_update_offer_id(items)
    print(result)

asyncio.run(main())
``` 