from typing import Any, Literal, Type, Union
from aiohttp import ClientSession
from loguru import logger
import sys
from .exceptions import (
    OzonAPIError,
    OzonAPIClientError,
    OzonAPIForbiddenError,
    OzonAPINotFoundError,
    OzonAPIConflictError,
    OzonAPIServerError,
)

logger.remove()
logger.add(sys.stderr, level="INFO")


class OzonAPIBase:
    __client_id: str
    __api_key: str
    __api_url: Union[str, None] = "https://api-seller.ozon.ru"
    __description_category_id: Union[int, None] = None
    __language: Literal["DEFAULT", "RU", "EN", "TR", "ZH_HANS"] = "DEFAULT"
    __type_id: Union[int, None] = None

    @property
    def api_url(self) -> str:
        return self.__api_url

    @api_url.setter
    def api_url(self: Type["OzonAPIBase"], value: str) -> None:
        if not value.startswith("http://") and not value.startswith("https://"):
            raise ValueError("Invalid URL: must start with 'http://' or 'https://'")
        self.__api_url = value

    @property
    def description_category_id(self) -> int:
        return self.__description_category_id

    @description_category_id.setter
    def description_category_id(self: Type["OzonAPIBase"], value: int) -> None:
        self.__description_category_id = value

    @property
    def language(self) -> Literal["DEFAULT", "RU", "EN", "TR", "ZH_HANS"]:
        return self.__language

    @language.setter
    def language(
        self: Type["OzonAPIBase"],
        value: Literal["DEFAULT", "RU", "EN", "TR", "ZH_HANS"],
    ) -> None:
        self.__language = value

    @property
    def type_id(self) -> int:
        return self.__type_id

    @type_id.setter
    def type_id(self: Type["OzonAPIBase"], value: int) -> None:
        self.__type_id = value

    @property
    def client_id(self) -> str:
        return self.__client_id

    @client_id.setter
    def client_id(self: Type["OzonAPIBase"], value: str) -> None:
        self.__client_id = value

    @property
    def api_key(self) -> str:
        return self.__api_key

    @api_key.setter
    def api_key(self: Type["OzonAPIBase"], value: str) -> None:
        self.__api_key = value

    def __init__(self: Type["OzonAPIBase"], client_id: str, api_key: str) -> None:
        self.client_id = client_id
        self.api_key = api_key
        logger.info("Ozon API initialized successfully.")

    async def _request(
        self: Type["OzonAPIBase"],
        method: Literal["post", "get", "put", "delete"] = "post",
        api_version: str = "v1",
        endpoint: str = "",
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.__api_url}/{api_version}/{endpoint}"
        async with ClientSession(
            headers={
                "Client-Id": self.__client_id,
                "Api-Key": self.__api_key,
            }
        ) as session:
            async with getattr(session, method.lower())(url, json=json) as response:
                data = await response.json()
                if response.status >= 400:
                    code = data.get("code", response.status)
                    message = data.get("message", "Unknown error")
                    details = data.get("details", [])
                    error_map = {
                        400: OzonAPIClientError,
                        403: OzonAPIForbiddenError,
                        404: OzonAPINotFoundError,
                        409: OzonAPIConflictError,
                        500: OzonAPIServerError,
                    }
                    exc_class = error_map.get(response.status, OzonAPIError)
                    raise exc_class(code, message, details)
                return data
