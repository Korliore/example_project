import enum
from typing import Any

async def clear_data(dict_: dict, clear_arg: Any = None) -> dict:
    """Ф-ия для очистки полученных данных из запроса"""
    cleaned_dict = {key: value for key, value in dict_.items() if value is not clear_arg}
    for key, value in cleaned_dict.items():
        if isinstance(value, enum.Enum):
            cleaned_dict[key] = value.value
    return cleaned_dict