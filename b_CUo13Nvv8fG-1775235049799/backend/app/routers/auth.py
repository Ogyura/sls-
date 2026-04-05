from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class VKLoginRequest(BaseModel):
    code: str

@router.post("/auth/login")
async def login(request: LoginRequest):
    # Mock login
    return {
        "access_token": "mock_token_123",
        "token_type": "bearer",
        "user": {
            "id": 1,
            "email": request.email,
            "name": "Тестовый Пользователь",
            "role": "user"
        }
    }

@router.post("/auth/vk")
async def vk_login(request: VKLoginRequest):
    # Mock VK login
    return {
        "access_token": "vk_mock_token_456",
        "token_type": "bearer",
        "user": {
            "id": 2,
            "email": "vk_user@example.com",
            "name": "VK Пользователь",
            "role": "user"
        }
    }

@router.get("/auth/me")
async def get_current_user():
    return {
        "id": 1,
        "email": "user@example.com",
        "name": "Тестовый Пользователь",
        "role": "user"
    }
