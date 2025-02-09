from typing import Annotated

from fastapi import Depends, FastAPI, APIRouter, HTTPException
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


from app.db.models import Link

from app.db.session import get_db
from app.routers.auth import get_current_user

router = APIRouter(prefix='', tags=['main'])


@router.delete('/{short_link}')
async def delete_link(short_link: str, get_user: Annotated[dict, Depends(get_current_user)],
                      db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Link).where(Link.short_link == short_link))
    link = result.scalars().first()

    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    if get_user == None or link.username != get_user['id']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to delete this link!")

    link.is_active = False
    await db.commit()

    return link
