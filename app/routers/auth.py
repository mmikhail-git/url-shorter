from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select, insert
from typing import Annotated, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.db.models import User
from app.schemas.schemas import RequestUserCreate, ResponseUser
from app.db.session import get_db
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError

SECRET_KEY = '76cf9af5c7ce008b1959755a37b2e795c96a77ab543064610d395244c54a8c10'
ALGORITHM = 'HS256'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)
router = APIRouter(prefix='/auth', tags=['auth'])
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


async def get_optional_token(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[str]:
    return token

@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: RequestUserCreate, db: AsyncSession = Depends(get_db)):
    await db.execute(insert(User).values(username=create_user_request.username,
                                         hashed_password=bcrypt_context.hash(create_user_request.password)
                                         ))

    await db.commit()

    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


# async def get_current_user(token: Optional[str] = Depends(get_optional_token)) -> Optional[ResponseUser]:
#     if token is None:
#         print('Token is absent')
#         return None  # Если токен отсутствует, возвращаем None
#
#     try:
#         # Декодируем токен
#         user = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username_jwt: str = user.get('sub')
#         user_id_jwt: int = user.get('id')
#         expire = user.get('exp')
#         print('=', user)
#         # Проверяем, истек ли срок действия токена
#         if expire is not None and datetime.utcnow() > datetime.fromtimestamp(expire):
#             print(1234)
#             return None  # Если токен истек, возвращаем None
#
#         if username_jwt is None or user_id_jwt is None:
#             print(1234)
#             return None  # Если данные пользователя отсутствуют, возвращаем None
#
#         print(username_jwt, user_id_jwt, expire)
#
#         return ResponseUser(username=username_jwt, id=user_id_jwt)
#
#     except JWTError:
#         print('JWTError')
#         return None  # Если токен невалиден, возвращаем None

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    if token is None:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        expire = payload.get('exp')
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate user'
            )
        if expire is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token supplied"
            )
        return {
            'username': username,
            'id': user_id
        }
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired!"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user'
        )

@router.get('/read_current_user')
async def read_current_user(user: dict = Depends(get_current_user)):
    return {'User': user}


async def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def authenticate_user(username: str, password: str, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.username == username))
    if not user or not bcrypt_context.verify(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post('/token')
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(form_data.username, form_data.password, db)

    token = await create_access_token(user.username, user.id,
                                      expires_delta=timedelta(minutes=20))
    return {
        'access_token': token,
        'token_type': 'bearer'
    }
