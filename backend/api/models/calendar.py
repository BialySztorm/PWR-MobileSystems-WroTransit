from sqlalchemy import Boolean, Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from api.models.base import Base


class Calendar(Base):
    __tablename__ = "calendar"

    service_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    monday: Mapped[bool] = mapped_column(Boolean)
    tuesday: Mapped[bool] = mapped_column(Boolean)
    wednesday: Mapped[bool] = mapped_column(Boolean)
    thursday: Mapped[bool] = mapped_column(Boolean)
    friday: Mapped[bool] = mapped_column(Boolean)
    saturday: Mapped[bool] = mapped_column(Boolean)
    sunday: Mapped[bool] = mapped_column(Boolean)
    start_date: Mapped[str] = mapped_column(Date)
    end_date: Mapped[str] = mapped_column(Date)


class CalendarDate(Base):
    __tablename__ = "calendar_dates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    service_id: Mapped[str] = mapped_column(String(32))
    date: Mapped[str] = mapped_column(Date)
    exception_type: Mapped[int] = mapped_column(Integer)
    """1 = service added for this date, 2 = service removed for this date."""
