import logging
from functools import lru_cache
from typing import Dict, List, Tuple, Union
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

NETBOX_URL = "https://demo.netbox.dev"

# Константы для ключей параметров
MANUFACTURER_KEY = "manufacturer"
ROLE_KEY = "role"
STATUS_KEY = "status"
SITE_KEY = "site"
NAME_KEY = "name"

# Константы для ключей в выходных данных
MANUFACTURER_ID_KEY = "manufacturer_id"
ROLE_ID_KEY = "role_id"
SITE_ID_KEY = "site_id"
BRIEF_KEY = "brief"
LIMIT_KEY = "limit"
NAME_IE_KEY = "name__ie"

# Пример входных данных
EXAMPLE_INPUT_DICT = {
    MANUFACTURER_KEY: ["cisco"],
    ROLE_KEY: ["router", "core-switch", "access-switch"],
    STATUS_KEY: ["active", "offline"],
    SITE_KEY: ["dm-akronsk", "dm-albany", "dm-camden"],
}

# Пример ожидаемого результата
EXAMPLE_RESULT = [
    (MANUFACTURER_ID_KEY, 3),
    (ROLE_ID_KEY, 1),
    (ROLE_ID_KEY, 2),
    (ROLE_ID_KEY, 4),
    (STATUS_KEY, "active"),
    (STATUS_KEY, "offline"),
    (SITE_ID_KEY, 2),
    (SITE_ID_KEY, 3),
    (SITE_ID_KEY, 6),
    (BRIEF_KEY, "true"),
    (LIMIT_KEY, 500),
]


@lru_cache
def _get_site_id(site_slug: str) -> int:
    """Возвращает ID сайта по его slug."""
    site_ids = {
        "dm-akronsk": 2,
        "dm-albany": 3,
        "dm-binghamton": 4,
        "dm-buffalo": 5,
        "dm-camden": 6,
    }
    if site_slug not in site_ids:
        raise ValueError(f"Неизвестный сайт '{site_slug}'")
    return site_ids[site_slug]


@lru_cache
def _get_device_role_id(role_slug: str) -> int:
    """Возвращает ID роли устройства по её slug."""
    role_ids = {
        "router": 1,
        "core-switch": 2,
        "distribution-switch": 3,
        "access-switch": 4,
    }
    if role_slug not in role_ids:
        raise ValueError(f"Неизвестная роль устройства '{role_slug}'")
    return role_ids[role_slug]


@lru_cache
def _get_manufacturer_id(manufacturer_slug: str) -> int:
    """Возвращает ID производителя по его slug."""
    manufacturer_ids = {
        "arista": 1,
        "cisco": 3,
        "juniper": 7,
    }
    if manufacturer_slug not in manufacturer_ids:
        raise ValueError(f"Неизвестный производитель '{manufacturer_slug}'")
    return manufacturer_ids[manufacturer_slug]


ParamTuple = Tuple[str, Union[str, int]]
ParamList = List[ParamTuple]


def craft_nb_query(
    request_params: Dict[str, List[str]],
) -> ParamList:
    """Преобразует параметры запроса в формат NetBox API."""
    if not request_params:
        raise ValueError("Отсутствуют параметры запроса")

    param_handlers = {
        NAME_KEY: lambda name_key: (NAME_IE_KEY, name_key.lower()),
        SITE_KEY: lambda site_id: (SITE_ID_KEY, _get_site_id(site_id)),
        ROLE_KEY: lambda role_id: (ROLE_ID_KEY, _get_device_role_id(role_id)),
        MANUFACTURER_KEY: lambda man_id: (
            MANUFACTURER_ID_KEY,
            _get_manufacturer_id(man_id),
        ),
        STATUS_KEY: lambda status_key: (STATUS_KEY, status_key),
    }

    processed_params = []
    for param_type, nb_items in request_params.items():
        if param_type not in param_handlers:
            raise ValueError(f"Неизвестный тип параметра: '{param_type}'")

        nb_handler = param_handlers[param_type]
        processed_params.extend(nb_handler(nb_item) for nb_item in nb_items)

    processed_params.extend(
        [
            (BRIEF_KEY, "true"),
            (LIMIT_KEY, 500),
        ],
    )

    return processed_params


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    nb_result = craft_nb_query(EXAMPLE_INPUT_DICT)
    assert (
        nb_result == EXAMPLE_RESULT
    ), f"Ожидалось: {EXAMPLE_RESULT}\nПолучено: {nb_result}"
    query_url = f"{NETBOX_URL}/api/dcim/devices/?{urlencode(nb_result)}"
    logger.info("Generated NetBox API URL: %s", query_url)
