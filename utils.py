from typing import Any


def get_text_from_element_or_default(element: Any, default_value: str) -> str:
    return element.text if element is not None else default_value
