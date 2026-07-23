from sqlalchemy import Select, asc, desc, or_


class BaseRepository:

    @staticmethod
    def apply_filters(
        stmt: Select,
        filters: dict,
        query,
    ) -> Select:
        """
        {
            "status": Task.status,
            "created_by": Task.created_by,
        }
        """

        for field_name, column in filters.items():
            value = getattr(query, field_name, None)

            if value is not None:
                stmt = stmt.where(column == value)

        return stmt

    @staticmethod
    def apply_search(
        stmt: Select,
        search: str | None,
        columns: list,
    ) -> Select:

        if not search:
            return stmt

        stmt = stmt.where(or_(*[column.ilike(f"%{search}%") for column in columns]))

        return stmt

    @staticmethod
    def apply_sort(
        stmt: Select,
        sortable_columns: dict,
        sort_by: str,
        order: str,
    ) -> Select:

        column = sortable_columns.get(sort_by)

        if column is None:
            return stmt

        if order == "asc":
            return stmt.order_by(asc(column))

        return stmt.order_by(desc(column))

    @staticmethod
    def apply_pagination(
        stmt: Select,
        page: int,
        limit: int,
    ) -> Select:

        offset = (page - 1) * limit

        return stmt.offset(offset).limit(limit)
