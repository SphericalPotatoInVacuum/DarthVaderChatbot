from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class DialogueEntry(Base):
    __tablename__ = "dialogues"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int]
    entry_id: Mapped[int]
    exchange: Mapped[str]

    def __repr__(self):
        return f'<DialogueEntry id={self.id}, user_id={self.user_id}, entry_id={self.entry_id}>'
