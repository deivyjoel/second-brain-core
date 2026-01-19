from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime

from backend.infrastructure.repositories.sql_alchemy.date_reference import get_utc_now


class Base(DeclarativeBase):
    pass


class ThemeModel(Base):
    __tablename__ = 'theme'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_id : Mapped[int | None] = mapped_column(ForeignKey("theme.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            default=get_utc_now
        )
    last_edited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now
    )

    notes = relationship(
        "NoteModel", 
        back_populates="theme", 
        cascade="all, delete-orphan"
    )
    images = relationship(
        "ImageModel", 
        back_populates="theme", 
        cascade="all, delete-orphan"
        )
    parent = relationship("ThemeModel", remote_side=[id], back_populates="children")
    children = relationship("ThemeModel", back_populates="parent", cascade="all, delete-orphan")
    

class NoteModel(Base):
    __tablename__ = "note"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str | None] = mapped_column(nullable=True)
    theme_id: Mapped[int | None] = mapped_column(ForeignKey("theme.id"), nullable = True)
    created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            default=get_utc_now
    )
    last_edited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now
    )

    theme = relationship("ThemeModel", back_populates="notes")
    times = relationship(
        "TimeModel", 
        back_populates="note", 
        cascade="all, delete-orphan"
    )


class TimeModel(Base):
    __tablename__ = 'time'

    id: Mapped[int] = mapped_column(primary_key=True)
    note_id: Mapped[int] = mapped_column(Integer, ForeignKey("note.id"), nullable=False)
    minutes: Mapped[float] = mapped_column(default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now
    )

    note = relationship("NoteModel", back_populates="times")



"""Only saves file paths"""
class ImageModel(Base):
    __tablename__ = "image"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    
    theme_id: Mapped[int | None] = mapped_column(ForeignKey("theme.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)

    theme = relationship("ThemeModel", back_populates="images")