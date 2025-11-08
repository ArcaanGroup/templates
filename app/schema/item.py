from pydantic import BaseModel


class ItemBase(BaseModel):
    name: str
    price: float
    is_offer: bool


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    pass


class ItemOut(ItemBase):
    id: int

    class Config:
        from_attributes = True
