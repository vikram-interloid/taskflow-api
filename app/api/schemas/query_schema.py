from typing import Literal
from uuid import UUID

from pydantic import ConfigDict

from app.api.enums.task_status import TaskStatus
from app.api.schemas.pagination_schema import PaginationParams


class TaskQueryParams(PaginationParams):

    status: TaskStatus | None = None
    created_by: UUID | None = None
    search: str | None = None
    sort_by: str = "created_at"
    order: str = "desc"

    model_config = ConfigDict(extra="forbid")


class UserQueryParams(PaginationParams):

    email: str | None = None
    search: str | None = None
    sort_by: Literal[
        "user_name",
        "email",
        "created_at",
    ] = "created_at"

    order: Literal["asc", "desc"] = "desc"


class RoleQueryParams(PaginationParams):

    search: str | None = None
    sort_by: Literal[
        "role_name",
        "created_at",
    ] = "created_at"

    order: Literal["asc", "desc"] = "desc"


class UserRoleQueryParams(PaginationParams):

    user_id: UUID | None = None
    role_id: UUID | None = None
    assigned_by: UUID | None = None
    sort_by: Literal["assigned_at",] = "assigned_at"

    order: Literal[
        "asc",
        "desc",
    ] = "desc"


class UserTaskQueryParams(PaginationParams):

    user_id: UUID | None = None
    task_id: UUID | None = None
    created_by: UUID | None = None
    status: TaskStatus | None = None
    search: str | None = None
    sort_by: Literal[
        "status",
        "due_at",
        "created_at",
    ] = "created_at"

    order: Literal[
        "asc",
        "desc",
    ] = "desc"
