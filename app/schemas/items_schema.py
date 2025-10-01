from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)


class ItemCreate(ItemBase): ...


class ItemUpdate(ItemBase):
    name: str | None = Field(None, min_length=1, max_length=100)  # type: ignore
    description: str | None = Field(None, max_length=500)


class ItemOut(ItemBase):
    id: int

    model_config = {"from_attributes": True}
