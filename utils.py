from typing import Any, Optional


def get_text_from_element_or_none(element: Any) -> Optional[str]:
    return element.text if element is not None else None

