import math


def build_pagination(
    page: int,
    page_size: int,
    total_records: int
):

    total_pages = math.ceil(total_records / page_size)

    return {
        "current_page": page,
        "page_size": page_size,
        "total_records": total_records,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1
    }