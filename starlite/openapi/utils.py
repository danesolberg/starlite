import re
from typing import TYPE_CHECKING, List, Optional

from pydantic.fields import ModelField

from starlite.exceptions import ImproperlyConfiguredException
from starlite.handlers.http import HTTPRouteHandler
from starlite.openapi.constants import PYDANTIC_FIELD_SHAPE_MAP
from starlite.openapi.enums import OpenAPIType

if TYPE_CHECKING:  # pragma: no cover
    from typing import Union

    from starlite import Controller, Router, Starlite


CAPITAL_LETTERS_PATTERN = re.compile(r"(?=[A-Z])")


def pascal_case_to_text(s: str) -> str:
    """Given a 'PascalCased' string, return its split form- 'Pascal Cased'"""
    return " ".join(re.split(CAPITAL_LETTERS_PATTERN, s)).strip()


def extract_tags_from_route_handler(route_handler: HTTPRouteHandler) -> Optional[List[str]]:
    """Extracts and combines tags from route_handler and any owners"""
    child_tags = route_handler.tags or []
    parent_tags: List[str] = []
    obj: "Union[HTTPRouteHandler, Controller, Router, Starlite]"
    obj = route_handler
    while hasattr(obj, "owner"):
        if obj.owner is None:
            break
        obj = obj.owner
        parent_tags += getattr(obj, "tags", None) or []
    return list(set(child_tags) | set(parent_tags)) or None


def get_openapi_type_for_complex_type(field: ModelField) -> OpenAPIType:
    """
    We are dealing with complex types in this case.

    The problem here is that the Python typing system is too crude to define OpenAPI objects properly.
    """
    try:
        return PYDANTIC_FIELD_SHAPE_MAP[field.shape]
    except KeyError as e:
        raise ImproperlyConfiguredException(
            f"Parameter '{field.name}' with type '{field.outer_type_}' could not be mapped to an Open API type. "
            f"This can occur if a user-defined generic type is resolved as a parameter. If '{field.name}' should "
            "not be documented as a parameter, annotate it using the `Dependency` function, e.g., "
            f"`{field.name}: ... = Dependency(...)`."
        ) from e
