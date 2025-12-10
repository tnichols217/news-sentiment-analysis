"""Manager for environment variables such as API keys"""

import os
from typing import TypedDict, cast, get_type_hints

from dotenv import dotenv_values


class TypedConfig(TypedDict):
    """Type of our environment variables"""

    OPENMEDIACLOUD_API_KEY: str
    OPENMEDIACLOUD_SOURCE_NUM: int
    OPENMEDIACLOUD_SOURCE_NUM_LIBERAL: int
    OPENMEDIACLOUD_SOURCE_NUM_CENTER: int
    OPENMEDIACLOUD_SOURCE_NUM_CONSERVATIVE: int


VARS = TypedConfig.__annotations__.keys()


@staticmethod
def getenv() -> TypedConfig:
    """Gets the current environment variables as a typed dicttionary

    Raises:
        ValueError: When an environment variable cannot be found

    Returns:
        A Typed Dictionary of environment variables

    """
    raw = {**dotenv_values(".env"), **os.environ}

    config: dict[str, object] = {}

    annotations = get_type_hints(TypedConfig)

    for key, typ in annotations.items():  # pyright: ignore[reportAny]
        value = raw.get(key)
        if value is None:
            raise ValueError(f"Missing environment variable: {key}")

        if typ is int:
            value = int(value)
        elif typ is float:
            value = float(value)

        config[key] = value

    return cast(TypedConfig, config)  # pyright: ignore[reportInvalidCast]
