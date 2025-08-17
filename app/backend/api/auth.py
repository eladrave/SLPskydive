from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from db import session, schemas, models
from core import security, rbac

router = APIRouter()

@router.post("/signup", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def signup(
    *,
    db: Session = Depends(session.get_db),
    user_in: schemas.UserCreateWithProfiles,
):
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )

    hashed_password = security.get_password_hash(user_in.password)

    user_data = user_in.dict(exclude={"password", "mentor_profile", "mentee_profile"})
    db_user = models.User(**user_data, hashed_password=hashed_password)

    if user_in.role == schemas.Role.mentor and user_in.mentor_profile:
        db_user.mentor_profile = models.Mentor(**user_in.mentor_profile.dict())

    if user_in.role == schemas.Role.mentee and user_in.mentee_profile:
        db_user.mentee_profile = models.Mentee(**user_in.mentee_profile.dict())

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=schemas.Token)
def login(
    response: Response,
    db: Session = Depends(session.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = security.get_user(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    access_token = security.create_access_token(data={"sub": user.email, "role": user.role.value})

    response.set_cookie(
        key="access_token", value=f"Bearer {access_token}", httponly=True, samesite="lax", secure=False
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(security.get_current_active_user)):
    return current_user
