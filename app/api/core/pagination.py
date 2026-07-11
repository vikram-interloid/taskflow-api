from fastapi import Query

from app.api.schemas.pagination_schema import PaginationParams


def pagination_params(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
) -> PaginationParams:
    
    return PaginationParams(
        page=page,
        limit=limit,
    )
    
    