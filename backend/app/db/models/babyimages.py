from app.db.database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, TIMESTAMP, func, ForeignKey
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.babies import Baby

class BabyImage(Base):
    __tablename__ = 'babyimages'

    i_id: Mapped[int] = mapped_column(primary_key=True)
    i_save: Mapped[str] = mapped_column(String(255), nullable=False)
    i_origin: Mapped[str] = mapped_column(String(255), nullable=False)
    i_label: Mapped[Optional[str]] = mapped_column(String(100),nullable=True)
    i_date: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    i_image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    b_id: Mapped[int] = mapped_column(ForeignKey('babies.b_id', ondelete="CASCADE"), nullable=False)
    
    baby: Mapped["Baby"] = relationship("Baby", back_populates="images")