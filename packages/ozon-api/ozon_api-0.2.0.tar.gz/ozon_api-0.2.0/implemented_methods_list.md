# Реализованные методы OzonAPI

- get_description_category_tree — POST /v1/description-category/tree — Получение дерева категорий описаний
- get_description_category_attribute — POST /v1/description-category/attribute — Получение атрибутов категории описаний
- get_description_category_attribute_values — POST /v1/description-category/attribute/values — Получение значений атрибутов категории описаний
- get_description_category_attribute_values_search — POST /v1/description-category/attribute/values/search — Поиск значений атрибутов категории описаний
- get_full_category_info — (комбинированный, использует несколько вышеуказанных эндпоинтов) — Получение полной информации о категории (кастомный метод)

- product_import — POST /v3/product/import — Импорт товаров
- product_import_info — POST /v1/product/import/info — Получение статуса задачи импорта товаров
- product_import_by_sku — POST /v1/product/import-by-sku — Импорт товаров по SKU
- product_attributes_update — POST /v1/product/attributes/update — Обновление атрибутов товаров
- products_delete — POST /v2/products/delete — Удаление товаров
- upload_digital_codes — POST /v1/product/upload_digital_codes — Загрузка цифровых кодов
- upload_digital_codes_info — POST /v1/product/upload_digital_codes/info — Получение статуса загрузки цифровых кодов

- product_pictures_import — POST /v1/product/pictures/import — Импорт изображений товаров
- product_pictures_info — POST /v1/product/pictures/info — Получение статуса задачи импорта изображений товаров
- product_pictures_info_v2 — POST /v2/product/pictures/info — Получение статуса задачи импорта изображений товаров (v2)

- product_barcode_add — POST /v1/barcode/add — Добавление штрихкода товара

- product_subscription — POST /v1/product/info/subscription — Подписка на обновления информации о товаре

- product_list — POST /v3/product/list — Получение списка товаров
- product_info_limit — POST /v4/product/info/limit — Получение лимита по товарам

- product_update_offer_id — POST /v1/product/update/offer-id — Обновление offer_id (артикула) товара

- product_archive — POST /v1/product/archive — Перенос товаров в архив по product_id
- product_unarchive — POST /v1/product/unarchive — Восстановление товаров из архива

- product_related_sku — POST /v1/product/related-sku/get — Получение связанных SKU

- product_rating_by_sku — POST /v1/product/rating-by-sku — Получение рейтинга товаров по SKU 