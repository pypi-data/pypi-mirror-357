from collections.abc import Callable
from typing import Any, TypeVar

from aiohttp_apigami.typedefs import HandlerType
from aiohttp_apigami.utils import get_or_set_apispec, get_or_set_schemas

T = TypeVar("T", bound=HandlerType)

# OpenAPI type definitions
Parameter = dict[str, Any]
ResponseSpec = dict[str, Any]
ResponsesSpec = dict[int, ResponseSpec]
TagType = str


def docs(
    *,
    tags: list[TagType] | None = None,
    summary: str | None = None,
    description: str | None = None,
    parameters: list[Parameter] | None = None,
    responses: ResponsesSpec | None = None,
    produces: list[str] | None = None,
    consumes: list[str] | None = None,
    deprecated: bool | None = None,
    operation_id: str | None = None,
    security: list[dict[str, list[str]]] | None = None,
    **custom_attrs: Any,
) -> Callable[[T], T]:
    """
    Annotate the decorated view function with the specified OpenAPI/Swagger attributes.

    Args:
        tags: A list of tags for API operation categorization
        summary: A short summary of what the operation does
        description: A verbose explanation of the operation behavior
        parameters: A list of parameters that may be used with the operation
        responses: The responses the API operation may return
        produces: A list of MIME types the operation can produce
        consumes: A list of MIME types the operation can consume
        deprecated: Declares this operation to be deprecated
        operation_id: A unique string used to identify the operation
        security: A declaration of which security mechanisms can be used for this operation
        **custom_attrs: Any additional OpenAPI attributes to apply

    Usage:

    .. code-block:: python

        from aiohttp import web


        @docs(
            tags=["my_tag"],
            summary="Test method summary",
            description="Test method description",
            parameters=[
                {
                    "in": "header",
                    "name": "X-Request-ID",
                    "schema": {"type": "string", "format": "uuid"},
                    "required": "true",
                }
            ],
        )
        async def index(request):
            return web.json_response({"msg": "done", "data": {}})

    """
    # Prepare kwargs dictionary with all provided attributes
    kwargs: dict[str, Any] = {}
    if tags is not None:
        kwargs["tags"] = tags
    if summary is not None:
        kwargs["summary"] = summary
    if description is not None:
        kwargs["description"] = description
    if deprecated is not None:
        kwargs["deprecated"] = deprecated
    if operation_id is not None:
        kwargs["operationId"] = operation_id
    if security is not None:
        kwargs["security"] = security
    if consumes is not None:
        kwargs["consumes"] = consumes
    if produces is not None:
        kwargs["produces"] = produces
    else:
        kwargs["produces"] = ["application/json"]

    # Add custom attributes
    kwargs.update(custom_attrs)

    def wrapper(func: T) -> T:
        func_apispec = get_or_set_apispec(func)
        get_or_set_schemas(func)  # just to make sure schemas are initialized

        extra_parameters = parameters or []
        extra_responses = responses or {}

        # Update the function's apispec attributes
        func_apispec["parameters"].extend(extra_parameters)
        func_apispec["responses"].update(extra_responses)
        func_apispec.update(kwargs)

        return func

    return wrapper
