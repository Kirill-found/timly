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
    HHTokenUpdate, PasswordChange, RefreshTokenRequest,
    ForgotPasswordRequest, ResetPasswordRequest
)
from app.schemas.base import APIResponse
from app.services.auth_service import AuthService
from app.utils.exceptions import AuthenticationError, ValidationError
from app.utils.response import (
    success, created, bad_request, unauthorized, not_found, internal_error
)

router = APIRouter()
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        auth_service = AuthService(db)
        user = await auth_service.get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "INVALID_CREDENTIALS", "message": "Invalid authentication credentials"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "AUTHENTICATION_ERROR", "message": str(e)},
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/register", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegistration, db: Session = Depends(get_db)):
    try:
        auth_service = AuthService(db)
        user = await auth_service.register_user(user_data)
        return created(data=user.to_dict())
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "VALIDATION_ERROR", "message": str(e)})
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": "INTERNAL_SERVER_ERROR", "message": "Error registering user"})


@router.post("/login", response_model=APIResponse)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    try:
        auth_service = AuthService(db)
        token_data = await auth_service.authenticate_user(login_data.email, login_data.password)
        return success(data=token_data)
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"error": "INVALID_CREDENTIALS", "message": str(e)}, headers={"WWW-Authenticate": "Bearer"})
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": "INTERNAL_SERVER_ERROR", "message": "Error authenticating"})


@router.get("/me", response_model=APIResponse)
async def get_current_user_profile(current_user = Depends(get_current_user)):
    return success(data=current_user.to_dict())


@router.put("/profile", response_model=APIResponse)
async def update_profile(profile_data: dict, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    return success(data={"status": "TODO", "message": "Profile update will be implemented"})


@router.post("/hh-token", response_model=APIResponse)
async def update_hh_token(token_data: HHTokenUpdate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        auth_service = AuthService(db)
        result = await auth_service.update_hh_token(current_user.id, token_data.hh_token)
        return success(data=result)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "VALIDATION_ERROR", "message": str(e)})
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": "INTERNAL_SERVER_ERROR", "message": "Error updating HH token"})


@router.delete("/hh-token", response_model=APIResponse)
async def delete_hh_token(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        auth_service = AuthService(db)
        result = await auth_service.delete_hh_token(current_user.id)
        return success(data=result)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": "INTERNAL_SERVER_ERROR", "message": "Error deleting HH token"})


@router.post("/change-password", response_model=APIResponse)
async def change_password(password_data: PasswordChange, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        auth_service = AuthService(db)
        result = await auth_service.change_password(current_user.id, password_data.current_password, password_data.new_password)
        return success(data=result)
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"error": "AUTHENTICATION_ERROR", "message": str(e)})
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "VALIDATION_ERROR", "message": str(e)})
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": "INTERNAL_SERVER_ERROR", "message": "Error changing password"})


@router.post("/refresh", response_model=APIResponse)
async def refresh_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        auth_service = AuthService(db)
        token_data = await auth_service.refresh_access_token(refresh_data.refresh_token)
        return success(data=token_data)
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"error": "INVALID_REFRESH_TOKEN", "message": str(e)}, headers={"WWW-Authenticate": "Bearer"})
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": "INTERNAL_SERVER_ERROR", "message": "Error refreshing token"})


@router.post("/logout", response_model=APIResponse)
async def logout(current_user = Depends(get_current_user)):
    return success(data={"message": "Logout successful", "status": "success"})


@router.post("/forgot-password", response_model=APIResponse)
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    import random
    import string
    import logging
    from datetime import datetime, timedelta
    from app.models.user import User
    from app.models.password_reset import PasswordResetCode

    try:
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            return success(data={"message": "If email is registered, reset code will be sent"})

        db.query(PasswordResetCode).filter(
            PasswordResetCode.user_id == user.id,
            PasswordResetCode.is_used == False
        ).delete()

        code = "".join(random.choices(string.digits, k=6))
        reset_code = PasswordResetCode(
            user_id=user.id,
            code=code,
            expires_at=datetime.utcnow() + timedelta(minutes=15)
        )
        db.add(reset_code)
        db.commit()

        try:
            from app.services.telegram_service import send_admin_notification
            msg = "Password reset request\n\nEmail: " + user.email + "\nCode: " + code + "\nValid for 15 minutes"
            await send_admin_notification(msg)
        except Exception as e:
            logging.error(f"Failed to send Telegram notification: {e}")

        return success(data={"message": "Reset code sent to email"})
    except Exception as e:
        logging.error(f"Error in forgot password: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": "INTERNAL_SERVER_ERROR", "message": "Error requesting password reset"})


@router.post("/reset-password", response_model=APIResponse)
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    import logging
    from datetime import datetime
    from app.models.user import User
    from app.models.password_reset import PasswordResetCode

    try:
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "INVALID_CODE", "message": "Invalid or expired code"})

        reset_code = db.query(PasswordResetCode).filter(
            PasswordResetCode.user_id == user.id,
            PasswordResetCode.code == request.code,
            PasswordResetCode.is_used == False,
            PasswordResetCode.expires_at > datetime.utcnow()
        ).first()

        if not reset_code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "INVALID_CODE", "message": "Invalid or expired code"})

        reset_code.is_used = True
        auth_service = AuthService(db)
        user.password_hash = await auth_service._hash_password(request.new_password)
        db.commit()

        try:
            from app.services.telegram_service import send_admin_notification
            msg = "Password changed successfully\n\nEmail: " + user.email
            await send_admin_notification(msg)
        except Exception:
            pass

        logging.info(f"Password reset for user: {user.email}")
        return success(data={"message": "Password changed successfully"})
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error resetting password: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": "INTERNAL_SERVER_ERROR", "message": "Error resetting password"})
