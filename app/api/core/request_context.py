from contextvars import ContextVar

request_id_ctx: ContextVar[str] = ContextVar(
    "request_id",
    default="-",
)

method_ctx: ContextVar[str] = ContextVar(
    "method",
    default="-",
)

path_ctx: ContextVar[str] = ContextVar(
    "path",
    default="-",
)
