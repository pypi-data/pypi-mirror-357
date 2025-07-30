from .base import OzonAPIBase
from .methods.category import OzonCategoryAPI
from .methods.product_import import OzonProductImportAPI
from .methods.product_pictures import OzonProductPicturesAPI
from .methods.product_list import OzonProductListAPI
from .methods.product_rating import OzonProductRatingAPI
from .methods.product_update_offer_id import OzonProductUpdateOfferIdAPI
from .methods.product_archive import OzonProductArchiveAPI
from .methods.product_subscription import OzonProductSubscriptionAPI
from .methods.product_related_sku import OzonProductRelatedSkuAPI
from .methods.product_pictures_info import OzonProductPicturesInfoAPI
from .methods.product_barcode_add import OzonProductBarcodeAddAPI


class OzonAPI(
    OzonCategoryAPI,
    OzonProductImportAPI,
    OzonProductPicturesAPI,
    OzonProductListAPI,
    OzonProductRatingAPI,
    OzonProductUpdateOfferIdAPI,
    OzonProductArchiveAPI,
    OzonProductSubscriptionAPI,
    OzonProductRelatedSkuAPI,
    OzonProductPicturesInfoAPI,
    OzonProductBarcodeAddAPI,
):
    pass


__all__ = ["OzonAPI", "OzonAPIBase"]

# Импортируйте здесь бизнес-методы и собирайте публичный API
