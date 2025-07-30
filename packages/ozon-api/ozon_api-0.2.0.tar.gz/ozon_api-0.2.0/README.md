# Ozon API Python Client

Асинхронная Python библиотека для работы с Ozon Seller API

[![PyPI version](https://img.shields.io/pypi/v/ozon-api)](https://pypi.org/project/ozon-api/) [![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/) [![Downloads](https://img.shields.io/pypi/dm/ozon-api)](https://pypi.org/project/ozon-api/) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## Установка
```bash
pip install ozon-api
```

## Быстрый старт
```python
import os
from dotenv import load_dotenv
from ozon_api import OzonAPI
import asyncio

load_dotenv()

async def main():
    api = OzonAPI(
        client_id=os.getenv("CLIENT_ID"),
        api_key=os.getenv("API_KEY")
    )
    # пример вызова любого метода
    # result = await api.get_description_category_tree()
    # print(result)

asyncio.run(main())
```

_**Устанавливаем язык ответа:**_
```python
api.language = "RU"
```

## Примеры использования методов
- [Категории и атрибуты (category)](docs/category_usage.md)
- [Импорт и обновление товаров (product_import)](docs/product_import_usage.md)
- [Работа с изображениями (product_pictures)](docs/product_pictures_usage.md)
- [Список и лимиты товаров (product_list)](docs/product_list_usage.md)
- [Рейтинг товаров (product_rating)](docs/product_rating_usage.md)
- [Обновление offer_id (product_update_offer_id)](docs/product_update_offer_id_usage.md)
- [Архивация/разархивация товаров (product_archive)](docs/product_archive_usage.md)

_Все примеры используют синтаксис async/await!_

---

## Вклад в проект

Мы приветствуем любые улучшения и pull request'ы!

**Как внести вклад:**
1. Сделайте форк репозитория
2. Создайте новую ветку для вашей фичи или исправления:  
   `git checkout -b feature/my-feature`
3. Внесите изменения и добавьте тесты
4. Проверьте стиль кода:  
   `black .`
5. Убедитесь, что все тесты проходят успешно
6. Сделайте commit и push:  
   `git commit -m "Add my feature" && git push origin feature/my-feature`
7. Откройте Pull Request

**Best practice:**
- Следуйте [PEP8](https://peps.python.org/pep-0008/) и используйте автоформаттер [Black](https://github.com/psf/black)
- Пишите docstring к публичным методам
- Покрывайте код тестами (unit/integration)
- Не забывайте обновлять usage-примеры и документацию

---
