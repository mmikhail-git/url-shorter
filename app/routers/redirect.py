import random
import string
from typing import Optional, Annotated
from fastapi import Depends, FastAPI, APIRouter, HTTPException
from sqlalchemy import func, select, and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse
from app.db.models import Link, Analytics, Click
from app.db.session import get_db
from app.routers.auth import get_current_user
from app.schemas.schemas import ResponseUser, RequestLinkCreate

router = APIRouter(prefix='', tags=['main'])


@router.get('/all')
async def get_all(get_user: Annotated[dict, Depends(get_current_user)],
                  db: AsyncSession = Depends(get_db)):

    if get_user == None:
        return []

    result = await db.execute(
        select(Link, Analytics)
        .join(Analytics, Link.id == Analytics.link_id, isouter=True)  # LEFT OUTER JOIN
        .where(Link.username == get_user['id'])
    )

    links_with_analytics = result.all()

    return [
        {
            "short_link": link.short_link,
            "full_link": link.full_link,
            "expires_at": link.expires_at,
            "is_active": link.is_active,
            "total_clicks": analytics.total_clicks if analytics else 0,
            "unique_clicks": analytics.unique_users if analytics else 0,
            "username": link.username
        }
        for link, analytics in links_with_analytics
    ]


async def get_full_link(short_link: str, db: AsyncSession = Depends(get_db)) -> Link:
    result = await db.execute(
        select(Link).where(
            and_(
                Link.is_active == True,
                Link.short_link == short_link,
                or_(
                    Link.expires_at > func.now(),
                    Link.expires_at == None
                )
            )
        )
    )
    full_link = result.scalars().first()

    if not full_link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short link not found")

    return full_link


async def update_analytics(full_link: Link, click: Click, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(
        select(func.count(func.distinct(Click.ip_address)))
        .filter(Click.link_id == full_link.id)
    )
    total_uniq_users = result.scalar()

    result = await db.execute(
        select(Analytics).where(Analytics.link_id == full_link.id)
    )
    analytics = result.scalars().first()

    analytics.total_clicks += 1
    analytics.unique_users = total_uniq_users

    db.add(click)
    await db.commit()

    return {
        "total_clicks": analytics.total_clicks,
        "uniq_clicks": total_uniq_users
    }


@router.get('/{short_link}')
async def get_link(short_link: str, request: Request, db: AsyncSession = Depends(get_db)):
    full_link = await get_full_link(short_link, db)

    click = Click(
        link_id=full_link.id,
        user_agent=request.headers.get('user-agent'),
        referrer=request.headers.get('referer'),
        ip_address=request.client.host
    )

    analytics = await update_analytics(full_link, click, db)

    return {
        "full_link": full_link.full_link,
        "analytics": analytics
    }


@router.get('/redirect/{short_link}')
async def redirect(short_link: str, request: Request, db: AsyncSession = Depends(get_db)):
    full_link = await get_full_link(short_link, db)

    click = Click(
        link_id=full_link.id,
        user_agent=request.headers.get('user-agent'),
        referrer=request.headers.get('referer'),
        ip_address=request.client.host
    )

    await update_analytics(full_link, click, db)

    return RedirectResponse(full_link.full_link)


