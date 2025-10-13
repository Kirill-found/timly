"""
API endpoints для настроек пользователя (HH.ru токен)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import encrypt_hh_token, decrypt_hh_token
from app.models.user import User
from app.schemas.user import HHTokenUpdate
from app.services.hh_client import HHClient
from app.api.auth import get_current_user

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.post("/hh-token")
async def update_hh_token(
    token_data: HHTokenUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Сохранение токена HH.ru
    
    - **hh_token**: Токен доступа к HH.ru API
    
    Токен шифруется перед сохранением в базе данных
    """
    # Проверяем валидность токена
    hh_client = HHClient(token_data.hh_token)
    is_valid = await hh_client.verify_token()
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невалидный токен HH.ru. Проверьте правильность токена."
        )
    
    # Шифруем и сохраняем токен
    encrypted_token = encrypt_hh_token(token_data.hh_token)
    current_user.encrypted_hh_token = encrypted_token
    current_user.token_verified = True
    
    await db.commit()
    
    return {
        "message": "Токен успешно сохранён и проверен",
        "token_verified": True
    }


@router.get("/hh-token/verify")
async def verify_hh_token(
    current_user: User = Depends(get_current_user)
):
    """
    Проверка статуса токена HH.ru
    
    Возвращает информацию о том, настроен ли токен и работает ли он
    """
    if not current_user.encrypted_hh_token:
        return {
            "has_token": False,
            "token_verified": False,
            "message": "Токен HH.ru не настроен"
        }
    
    # Проверяем актуальность токена
    try:
        decrypted_token = decrypt_hh_token(current_user.encrypted_hh_token)
        hh_client = HHClient(decrypted_token)
        is_valid = await hh_client.verify_token()
        
        return {
            "has_token": True,
            "token_verified": is_valid,
            "message": "Токен активен" if is_valid else "Токен недействителен"
        }
    except Exception as e:
        return {
            "has_token": True,
            "token_verified": False,
            "message": f"Ошибка проверки токена: {str(e)}"
        }


@router.delete("/hh-token")
async def delete_hh_token(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Удаление токена HH.ru
    """
    current_user.encrypted_hh_token = None
    current_user.token_verified = False
    
    await db.commit()
    
    return {"message": "Токен успешно удалён"}