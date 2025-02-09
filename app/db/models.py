from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, UniqueConstraint, text, TIMESTAMP
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import List, Optional

from sqlalchemy.sql import expression

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=False, nullable=False)
    hashed_password = Column(String)

    links: Mapped[List['Link']] = relationship('Link', back_populates='user')


class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    short_link: Mapped[str] = mapped_column(unique=True, index=True)
    full_link: Mapped[str] = mapped_column(String, unique=False, nullable=False)
    username: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    is_active = Column(Boolean, server_default=expression.true(), default=True)

    user = relationship('User', back_populates='links')
    click_info = relationship('Click', back_populates='link')
    analytics_info = relationship('Analytics', back_populates='link')


class Click(Base):
    __tablename__ = "clicks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    link_id: Mapped[int] = mapped_column(Integer, ForeignKey('links.id'), nullable=False, index=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    referrer: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    link = relationship('Link', back_populates='click_info')


class Analytics(Base):
    __tablename__ = "analytics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    link_id: Mapped[int] = mapped_column(Integer, ForeignKey('links.id'), nullable=False)
    total_clicks: Mapped[int] = mapped_column(default=0, server_default=text("0"))
    unique_users: Mapped[int] = mapped_column(default=0, server_default=text("0"))

    link = relationship('Link', back_populates='analytics_info')

