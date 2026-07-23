import logging

from app.api.core.request_context import (
    method_ctx,
    path_ctx,
    request_id_ctx,
)

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "request_id=%(request_id)s | "
    "%(method)s | "
    "%(path)s | "
    "%(name)s | "
    "%(message)s"
)


class RequestContextFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_ctx.get("-")
        record.method = method_ctx.get("-")
        record.path = path_ctx.get("-")
        return True


def setup_logging():
    formatter = logging.Formatter(
        fmt=LOG_FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler("app.log", mode="a")

    file_handler.setFormatter(formatter)
    file_handler.addFilter(RequestContextFilter())

    root_logger = logging.getLogger()

    root_logger.handlers.clear()
    root_logger.setLevel(logging.INFO)

    root_logger.addHandler(file_handler)


def get_logger(name: str):
    return logging.getLogger(name)
