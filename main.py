from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal, ModelCoefficients, get_db
import models

app = FastAPI()

# Create a new model coefficient
@app.post("/coefficients/", response_model=models.Coefficient)
def create_coefficient(coefficient: models.CoefficientCreate, db: Session = Depends(get_db)):
    db_coefficient = ModelCoefficients(**coefficient.dict())
    db.add(db_coefficient)
    db.commit()
    db.refresh(db_coefficient)
    return db_coefficient

# Get all coefficients
@app.get("/coefficients/", response_model=List[models.Coefficient])
def read_coefficients(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    coefficients = db.query(ModelCoefficients).offset(skip).limit(limit).all()
    return coefficients

# Get a specific coefficient by model name
@app.get("/coefficients/{model_name}", response_model=models.Coefficient)
def read_coefficient(model_name: str, db: Session = Depends(get_db)):
    coefficient = db.query(ModelCoefficients).filter(ModelCoefficients.model_name == model_name).first()
    if coefficient is None:
        raise HTTPException(status_code=404, detail="Model not found")
    return coefficient

# Update a model coefficient
@app.put("/coefficients/{model_name}", response_model=models.Coefficient)
def update_coefficient(model_name: str, coefficient: models.CoefficientUpdate, db: Session = Depends(get_db)):
    db_coefficient = db.query(ModelCoefficients).filter(ModelCoefficients.model_name == model_name).first()
    if db_coefficient is None:
        raise HTTPException(status_code=404, detail="Model not found")
    for key, value in coefficient.dict().items():
        setattr(db_coefficient, key, value)
    db.commit()
    db.refresh(db_coefficient)
    return db_coefficient

# Delete a model coefficient
@app.delete("/coefficients/{model_name}", response_model=models.Coefficient)
def delete_coefficient(model_name: str, db: Session = Depends(get_db)):
    db_coefficient = db.query(ModelCoefficients).filter(ModelCoefficients.model_name == model_name).first()
    if db_coefficient is None:
        raise HTTPException(status_code=404, detail="Model not found")
    db.delete(db_coefficient)
    db.commit()
    return db_coefficient
