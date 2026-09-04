from uuid import UUID

from pydantic import BaseModel, Field


class CreateReviewRequest(BaseModel):
    product_id: UUID
    rating: int = Field(..., ge=1, le=5)
    review_text: str
    image_url: str | None = None