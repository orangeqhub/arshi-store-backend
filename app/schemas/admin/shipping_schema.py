from pydantic import BaseModel, Field


class ShipWithBlueDartRequest(BaseModel):

    weight_kg: float = Field(gt=0)
    pieces: int = Field(default=1, ge=1)
