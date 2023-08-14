from datetime import datetime
from typing import Annotated

from sqlalchemy import String, ForeignKey, func
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship

from api.blacklist.blacklist_schemas import BlockedLevelSchema, BlacklistRead

timestamp = Annotated[
    datetime,
    mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP()),
]


class Base(DeclarativeBase):
    pass


class BlockedLevel(Base):
    __tablename__ = "blocked_level"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    unblocked_after: Mapped[int] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(String(length=100), nullable=True)
    blacklists: Mapped[list["Blacklist"]] = relationship(back_populates="blocked_level")

    def to_read_model(self) -> BlockedLevelSchema:
        return BlockedLevelSchema(
            id=self.id,
            unblocked_after=self.unblocked_after
        )


class Blacklist(Base):
    __tablename__ = "blacklist"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    blocking_level: Mapped[int] = mapped_column(ForeignKey("blocked_level.id"), nullable=False)
    blocked_at: Mapped[timestamp]
    blocked_level: Mapped["BlockedLevel"] = relationship(back_populates="blacklists")

    def to_read_model(self) -> BlacklistRead:
        return BlacklistRead(
            id=self.id,
            user_id=self.user_id,
            blocking_level=self.blocking_level
        )
