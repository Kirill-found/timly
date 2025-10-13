"""
API endpoints для аутентификации
Регистрация, логин, профиль пользователя
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import (
    UserRegistration, UserLogin, Token, UserProfile,
    HHTokenUpdate, PasswordChange, RefreshTokenRequest
)
from app.schemas.base import APIResponse
from app.services.auth_service import AuthService
from app.utils.exceptions import AuthenticationError, ValidationError
from app.utils.response import (
    success, created, bad_request, unauthorized, not_found, internal_error
)

router = APIRouter()
security = HTTPBearer()

# Dependency для получения текущего пользователя
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Получение текущего аутентифицированного пользователя
    Используется во всех защищенных endpoints
    """
    try:
        auth_service = AuthService(db)
        user = await auth_service.get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "INVALID_CREDENTIALS",
                    "message": "Invalid authentication credentials"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "AUTHENTICATION_ERROR",
                "message": str(e)
            },
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/register", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegistration,
    db: Session = Depends(get_db)
):
    """
    Регистрация нового пользователя
    Создает аккаунт HR менеджера
    """
    try:
        auth_service = AuthService(db)
        user = await auth_service.register_user(user_data)
        return created(data=user.to_dict())
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "VALIDATION_ERROR",
                "message": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "Ошибка при регистрации пользователя"
            }
        )


@router.post("/login", response_model=APIResponse)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Аутентификация пользователя
    Возвращает JWT токен для доступа к API
    """
    try:
        auth_service = AuthService(db)
        token_data = await auth_service.authenticate_user(
            login_data.email,
            login_data.password
        )
        return success(data=token_data)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "INVALID_CREDENTIALS",
                "message": str(e)
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "Ошибка при аутентификации"
            }
        )


@router.get("/me", response_model=APIResponse)
async def get_current_user_profile(
    current_user = Depends(get_current_user)
):
    """
    Получение профиля текущего пользователя
    Защищенный endpoint, требует аутентификации
    """
    return success(data=current_user.to_dict())


@router.put("/profile", response_model=APIResponse)
async def update_profile(
    profile_data: dict,  # TODO: Создать схему UpdateProfile
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновление профиля пользователя
    TODO: Реализовать обновление company_name и других полей
    """
    # TODO: Реализовать логику обновления профиля
    return success(data={"status": "TODO", "message": "Обновление профиля будет реализовано"})


@router.post("/hh-token", response_model=APIResponse)
async def update_hh_token(
    token_data: HHTokenUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновление HH.ru API токена
    Шифрует и сохраняет токен, проверяет его валидность
    """
    try:
        auth_service = AuthService(db)
        result = await auth_service.update_hh_token(
            current_user.id,
            token_data.hh_token
        )
        return success(data=result)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "VALIDATION_ERROR",
                "message": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "Ошибка при обновлении HH.ru токена"
            }
        )


@router.delete("/hh-token", response_model=APIResponse)
async def delete_hh_token(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Удаление HH.ru токена из системы
    Полностью удаляет зашифрованный токен
    """
    try:
        auth_service = AuthService(db)
        result = await auth_service.delete_hh_token(current_user.id)
        return success(data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "Ошибка при удалении HH.ru токена"
            }
        )


@router.post("/change-password", response_model=APIResponse)
async def change_password(
    password_data: PasswordChange,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Смена пароля пользователя
    Требует текущий пароль для подтверждения
    """
    try:
        auth_service = AuthService(db)
        result = await auth_service.change_password(
            current_user.id,
            password_data.current_password,
            password_data.new_password
        )
        return success(data=result)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "AUTHENTICATION_ERROR",
                "message": str(e)
            }
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "VALIDATION_ERROR",
                "message": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "Ошибка при смене пароля"
            }
        )


@router.post("/refresh", response_model=APIResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Обновление access токена используя refresh токен
    Возвращает новый access токен без необходимости повторного ввода пароля
    """
    try:
        auth_service = AuthService(db)
        token_data = await auth_service.refresh_access_token(refresh_data.refresh_token)
        return success(data=token_data)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "INVALID_REFRESH_TOKEN",
                "message": str(e)
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "Ошибка при обновлении токена"
            }
        )


@router.post("/logout", response_model=APIResponse)
async def logout(
    current_user = Depends(get_current_user)
):
    """
    Выход из системы
    TODO: Реализовать blacklist для JWT токенов
    """
    return success(data={
        "message": "Выход выполнен успешно",
        "status": "success"
    })