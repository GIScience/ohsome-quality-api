from contextlib import asynccontextmanager
from contextvars import ContextVar
from dataclasses import dataclass

from fastapi import Request


@dataclass
class RequestContext:
    path_parameters: dict


request_context: ContextVar[RequestContext] = ContextVar("request_context")


@asynccontextmanager
async def request_context_manager(path_parameters: dict):
    token = request_context.set(RequestContext(path_parameters=path_parameters))
    try:
        yield
    finally:
        request_context.reset(token)


async def set_request_context(request: Request):
    """Set request context for the duration of a request.

    After leaving the context manager (after the request is processed)
    the request context is reset again.
    """
    async with request_context_manager(request.path_params):
        yield
