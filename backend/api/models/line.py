from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from api.models.base import Base


class Line(Base):
    __tablename__ = "lines"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(10))
    name: Mapped[str] = mapped_column(String(120))
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
