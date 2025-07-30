# Примеры использования OzonProductRatingAPI (async/await)

## Получить рейтинг товаров по SKU
```python
from ozon_api import OzonAPI
import asyncio

async def main():
    api = OzonAPI(client_id="...", api_key="...")
    sku_list = [123456, 789012]
    result = await api.product_rating_by_sku(sku_list)
    print(result)

asyncio.run(main())
``` 