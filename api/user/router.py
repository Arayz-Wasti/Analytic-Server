import json

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from starlette.responses import JSONResponse

from backend.api.email_service.email_notification import EmailService
from backend.api.user.schemas.request import CreateUserRequest, LoginRequest
from backend.api.user.schemas.response import TokenResponse
from backend.utils.mongodb import get_db
from backend.utils.password_validation import validate_password
from backend.utils.password_hashing import hash_password, verify_password
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from datetime import datetime
import logging
from backend.utils.jwt import create_access_token, create_refresh_token
from backend.utils.auth import JWTBearer
import json

router = APIRouter()

log = logging.getLogger("analytic_server.user")

def send_notification(email:str, message:""):
    with open("notification.txt", "w") as notification:
        content = {"email": email, "message": message}
        notification.write(json.dumps(content))
        notification.flush()


@router.post("/signup")
async def sign_user(
    user: CreateUserRequest,
    background_tasks: BackgroundTasks,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Register a new user.
    - Validate password
    - Check if email already exists
    - Hash password securely
    - Insert user into MongoDB
    """
    validate_password(user.password)
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        log.warning(f"Signup attempt with existing email: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )
    hashed_password = hash_password(user.password)
    user_doc = {
        "email": user.email,
        "password": hashed_password,
        "username": user.username,
        "is_active": user.is_active,
        "created_at": datetime.utcnow(),
    }
    try:
        result = await db.users.insert_one(user_doc)
        log.info(f"User created with id: {result.inserted_id}")
        background_tasks.add_task(
            EmailService.send_email,
            to_email=user.email,
            subject="Notification",
            message="User has created successfully"
        )
    except Exception as e:
        log.error(f"Error inserting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user",
        )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "id": str(result.inserted_id),
            "email": user.email,
            "message": "User registered successfully"
        },
    )

@router.post("/login")
async def login(
    user: LoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    existing_user = await db.users.find_one({"username": user.username})
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    if  verify_password(user.password, existing_user["password"]):
        access_token = create_access_token(subject=str(existing_user["_id"]))
        refresh_token = create_refresh_token(subject=str(existing_user["_id"]))
        return TokenResponse(
            access_token= access_token,
            refresh_token= refresh_token
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


@router.get("/get_user_profile")
async def get_user_profile(
    token_payload: dict = Depends(JWTBearer()),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = token_payload["sub"]
    user = await db.users.find_one(
        {"_id": ObjectId(user_id)},
        {"password": 0}
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["_id"] = str(user["_id"])
    return user
