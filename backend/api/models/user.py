from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from api.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class FavouriteStop(Base):
    __tablename__ = "favourite_stops"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    stop_id: Mapped[str] = mapped_column(ForeignKey("stops.stop_id"), primary_key=True)


class FavouriteLine(Base):
    __tablename__ = "favourite_lines"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    route_id: Mapped[str] = mapped_column(
        ForeignKey("routes.route_id"), primary_key=True
    )


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    fcm_token: Mapped[str] = mapped_column(String(255))
    notify_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
