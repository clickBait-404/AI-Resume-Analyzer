"""
Skill model. A canonical taxonomy of known skills with aliases,
so 'JS' and 'Javascript' and 'JavaScript' all resolve to one
canonical skill. This is what makes matching deterministic instead
of naive substring comparison.
"""
from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from database.session import Base


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    canonical_name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    # category: language | framework | database | cloud | tool | soft_skill | concept

    aliases: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    # e.g. canonical_name="JavaScript", aliases=["js", "javascript", "ecmascript"]
