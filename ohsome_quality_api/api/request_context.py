from contextvars import ContextVar
from dataclasses import dataclass

from fastapi import Request


@dataclass
class RequestContext:
    path_parameters: dict


request_context: ContextVar[RequestContext] = ContextVar("request_context")


async def set_request_context(request: Request):
    """Set request context for the duration of a request.

    After leaving the context manager (after the request is processed)
    the request context is reset again.
    """
    token = request_context.set(RequestContext(path_parameters=request.path_params))
    try:
        yield
    finally:
        request_context.reset(token)
