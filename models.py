from pydantic import BaseModel, Field
from typing import Optional

# Existing models remain unchanged
class CoefficientBase(BaseModel):
    model_name: str = Field(..., alias='model_name')
    coefficients: str

class CoefficientCreate(CoefficientBase):
    pass

class CoefficientUpdate(BaseModel):
    coefficients: str

class Coefficient(CoefficientBase):
    id: int

    class Config:
        from_attributes = True
        protected_namespaces = ()


class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
