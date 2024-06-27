from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta

from database import SessionLocal, ModelCoefficients, get_db, User
import models
from auth import authenticate_user, create_access_token, get_current_active_user, oauth2_scheme  # Assuming your auth functions are in a separate file named auth.py
import auth
from post_data import post_to_onem2m_w1,post_to_onem2m_w2

app = FastAPI(
    title="Digital Twin API for Callibration",
    description="This layer and API's are used to callibrates the values and post them to the oneM2M",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=models.User)
def create_user(user: models.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.

    Parameters:
    - user (models.UserCreate): The user data.
    - db (Session): The database session.

    Returns:
    - models.User: The created user.
    """
    hashed_password = auth.get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=dict)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Generate an access token for a user based on their username and password.

    Parameters:
    - form_data (OAuth2PasswordRequestForm): The form data containing the username and password.
    - db (Session): The database session.

    Returns:
    - dict: A dictionary containing the access token and token type.

    Raises:
    - HTTPException: If the username or password is incorrect.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Existing endpoints with added authentication

@app.post("/coefficients/", response_model=models.Coefficient)
def create_coefficient(coefficient: models.CoefficientCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    """
    Create a new coefficient.

    Parameters:
    - coefficient (models.CoefficientCreate): The coefficient data.
    - db (Session): The database session.
    - current_user (models.User): The current authenticated user.

    Returns:
    - models.Coefficient: The created coefficient.
    """
    db_coefficient = ModelCoefficients(**coefficient.dict(by_alias=True))
    db.add(db_coefficient)
    db.commit()
    db.refresh(db_coefficient)
    return db_coefficient

@app.get("/coefficients/", response_model=List[models.Coefficient])
def read_coefficients(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    """
    Get a list of coefficients.

    Parameters:
    - skip (int): The number of coefficients to skip.
    - limit (int): The maximum number of coefficients to return.
    - db (Session): The database session.
    - current_user (models.User): The current authenticated user.

    Returns:
    - List[models.Coefficient]: The list of coefficients.
    """
    coefficients = db.query(ModelCoefficients).offset(skip).limit(limit).all()
    return coefficients

@app.get("/coefficients/{model_name}", response_model=models.Coefficient)
def read_coefficient(model_name: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    """
    Get a coefficient by model name.

    Parameters:
    - model_name (str): The name of the model.
    - db (Session): The database session.
    - current_user (models.User): The current authenticated user.

    Returns:
    - models.Coefficient: The coefficient.
    """
    coefficient = db.query(ModelCoefficients).filter(ModelCoefficients.model_name == model_name).first()
    if coefficient is None:
        raise HTTPException(status_code=404, detail="Model not found")
    return coefficient

@app.put("/coefficients/{model_name}", response_model=models.Coefficient)
def update_coefficient(model_name: str, coefficient: models.CoefficientUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    """
    Update a coefficient by model name.

    Parameters:
    - model_name (str): The name of the model.
    - coefficient (models.CoefficientUpdate): The updated coefficient data.
    - db (Session): The database session.
    - current_user (models.User): The current authenticated user.

    Returns:
    - models.Coefficient: The updated coefficient.
    """
    db_coefficient = db.query(ModelCoefficients).filter(ModelCoefficients.model_name == model_name).first()
    if db_coefficient is None:
        raise HTTPException(status_code=404, detail="Model not found")
    for key, value in coefficient.dict().items():
        setattr(db_coefficient, key, value)
    db.commit()
    db.refresh(db_coefficient)
    return db_coefficient

@app.delete("/coefficients/{model_name}", response_model=models.Coefficient)
def delete_coefficient(model_name: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    """
    Delete a coefficient by model name.

    Parameters:
    - model_name (str): The name of the model.
    - db (Session): The database session.
    - current_user (models.User): The current authenticated user.

    Returns:
    - models.Coefficient: The deleted coefficient.
    """
    db_coefficient = db.query(ModelCoefficients).filter(ModelCoefficients.model_name == model_name).first()
    if db_coefficient is None:
        raise HTTPException(status_code=404, detail="Model not found")
    db.delete(db_coefficient)
    db.commit()
    return db_coefficient

@app.post("/post_data/w1/{node_name}")
def post_data(node_name: str, data: dict, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    """
    Post data to OneM2M Water Quality Version 2.

    Parameters:
    - node_name (str): The name of the node.
    - data (dict): The data to be posted.(voltage, temparature, u_tds)
    - db (Session): The database session.
    - current_user (models.User): The current authenticated user.

    Returns:
    - dict: A dictionary containing the response code.
    """
    response_code = post_to_onem2m_w1(node_name, data, db, current_user)
    return {"response_code": response_code}

@app.post("/post_data/w2/{node_name}")
def post_data(node_name: str, data: dict, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    """
    Post data to OneM2M Water Quality Version 2.

    Parameters:
    - node_name (str): The name of the node.
    - data (dict): The data to be posted.(voltage,temparature, u_tds ,ph,turbudity)
    - db (Session): The database session.
    - current_user (models.User): The current authenticated user.

    Returns:
    - dict: A dictionary containing the response code.
    """
    response_code = post_to_onem2m_w2(node_name, data, db, current_user)
    return {"response_code": response_code}

