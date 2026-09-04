from pydantic import BaseModel


class ReviewActionRequest(BaseModel):
    admin_note: str | None = None