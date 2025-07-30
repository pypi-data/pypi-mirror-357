# Примеры использования OzonCategoryAPI (async/await)

## Получить дерево категорий
```python
from ozon_api import OzonAPI
import asyncio

async def main():
    api = OzonAPI(client_id="...", api_key="...")
    result = await api.get_description_category_tree()
    print(result)

asyncio.run(main())
```

## Получить атрибуты категории
```python
async def main():
    api = OzonAPI(client_id="...", api_key="...")
    api.description_category_id = 17027949
    api.type_id = 94765
    result = await api.get_description_category_attribute()
    print(result)

asyncio.run(main())
```

## Получить значения атрибута
```python
async def main():
    api = OzonAPI(client_id="...", api_key="...")
    api.description_category_id = 17027949
    api.type_id = 94765
    result = await api.get_description_category_attribute_values(
        name="Бренд", attribute_id=85, last_value_id=0, limit=5000
    )
    print(result)

asyncio.run(main())
```

## Поиск значения характеристики
```python
async def main():
    api = OzonAPI(client_id="...", api_key="...")
    api.description_category_id = 17027949
    api.type_id = 94765
    result = await api.get_description_category_attribute_values_search(
        attribute_id=85, value="WINDFORCE", limit=100
    )
    print(result)

asyncio.run(main())
```

## Получить полную информацию о категории
```python
async def main():
    api = OzonAPI(client_id="...", api_key="...")
    api.description_category_id = 17027949
    api.type_id = 94765
    result = await api.get_full_category_info()
    print(result)

asyncio.run(main())
``` 