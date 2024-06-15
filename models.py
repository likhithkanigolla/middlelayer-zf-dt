from pydantic import BaseModel, Field

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
        from_attributes = True  # Replaces orm_mode in Pydantic v2
        protected_namespaces = ()  # Resolves the field name conflict warning
