from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import (
    UserRegister, UserLogin, Token, UserResponse,
    TwoFactorSetup, TwoFactorVerify, PasswordChange
)
from app.services.auth_service import AuthService
from app.core.security import verify_2fa_code, get_2fa_qr_code
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    user = AuthService.register_user(db, user_data)
    return user


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Вход в систему"""
    user = AuthService.authenticate_user(db, login_data)
    
    # Если включена 2FA, возвращаем специальный токен
    if user.two_factor_enabled:
        # TODO: Реализовать промежуточный токен для 2FA
        pass
    
    tokens = AuthService.create_tokens(user)
    return tokens


@router.post("/2fa/setup")
def setup_2fa(
    setup_data: TwoFactorSetup,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Настройка двухфакторной аутентификации"""
    if setup_data.enabled:
        secret = AuthService.setup_2fa(db, current_user)
        qr_uri = get_2fa_qr_code(secret, current_user.email)
        return {
            "secret": secret,
            "qr_uri": qr_uri,
            "enabled": True
        }
    else:
        current_user.two_factor_enabled = False
        current_user.two_factor_secret = None
        db.commit()
        return {"enabled": False}


@router.post("/2fa/verify")
def verify_2fa(
    verify_data: TwoFactorVerify,
    current_user: User = Depends(get_current_user)
):
    """Проверка 2FA кода"""
    if not current_user.two_factor_enabled or not current_user.two_factor_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled"
        )
    
    is_valid = verify_2fa_code(current_user.two_factor_secret, verify_data.code)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid 2FA code"
        )
    
    return {"verified": True}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Получить информацию о текущем пользователе"""
    return current_user


@router.post("/logout")
def logout():
    """Выход из системы"""
    # В JWT не нужен серверный logout, просто удаляем токен на клиенте
    return {"message": "Successfully logged out"}


@router.post("/change-password")
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Изменить пароль"""
    from app.core.security import verify_password, get_password_hash
    
    # Проверяем старый пароль
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Устанавливаем новый пароль
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}

