import random
import string
from typing import Optional

from fastapi import Depends, FastAPI, APIRouter
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from app.db.models import Link, Analytics

from app.db.session import get_db
from app.routers.auth import get_current_user
from app.schemas.schemas import ResponseUser, RequestLinkCreate

router = APIRouter(prefix='', tags=['main'])


def generate_short_link(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


@router.post("/short_link", status_code=status.HTTP_201_CREATED)
async def create_link(original_link: RequestLinkCreate, db: AsyncSession = Depends(get_db),
                      current_user: Optional[ResponseUser] = Depends(get_current_user)):
    while True:  # Цикл для попытки создания новой ссылки
        try:
            async with db.begin():  # Начало транзакции
                short_link = generate_short_link()  # Генерация короткой ссылки
                link = Link(
                    short_link=short_link,
                    full_link=original_link.full_link,
                    expires_at=original_link.expires_at,
                    username=current_user['id'] if current_user else None
                )

                db.add(link)
                await db.flush()  # Необходимо для получения ID сгенерированной записи

                analytics = Analytics(
                    link_id=link.id
                )
                db.add(analytics)

            break  # Если все прошло успешно, выходим из цикла
        except IntegrityError:  # Если произошла ошибка уникальности
            await db.rollback()  # Откат транзакции
            # Генерируем короткую ссылку заново и повторяем попытку

    return {
        'link': link,
        'status_code': status.HTTP_201_CREATED
    }
