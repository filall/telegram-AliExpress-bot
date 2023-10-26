from typing import Optional

from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.future import select
from sqlalchemy.orm import relationship

from app.database.database import Base, session


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    requests = relationship(
        "UserRequest", back_populates="user", cascade="all, delete", lazy="joined"
    )


class UserRequest(Base):
    __tablename__ = "user_requests"
    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    user = relationship("User", back_populates="requests", lazy="joined")
    command = Column(String, nullable=False)
    keyword = Column(String, nullable=False)
    sort = Column(String)
    min_price = Column(Float)
    max_price = Column(Float)
    quantity = Column(Integer, nullable=False)

    def __str__(self):
        if self.command == "/lucky":
            return "{command}".format(command=self.command)

        self_string = "{command}: «{keyword}», количество: {quantity}".format(
            command=self.command, keyword=self.keyword, quantity=self.quantity
        )
        if self.min_price and self.max_price:
            self_string += ", цена: ${min_price} - ${max_price}".format(
                min_price=self.min_price, max_price=self.max_price
            )
        return self_string

    def __gt__(self, other):
        return self.id > other.id

    def __ge__(self, other):
        return self.id >= other.id

    def __lt__(self, other):
        return self.id < other.id

    def __le__(self, other):
        return self.id <= other.id

    def __eq__(self, other):
        return self.id == other.id


async def create_user(
    user_id: int, username: str, first_name: str, last_name: Optional[str]
) -> bool:
    """
    Попытка создать пользователя

    :return: True если пользователь создан, False если пользователь уже существует
    """
    if await get_user_by_id(user_id):
        return False

    new_user = User(
        user_id=user_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
    )
    session.add(new_user)
    await session.commit()
    return True


async def create_user_request_history(
    user_id: int,
    command: str,
    keyword: str,
    quantity: str,
    sort: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
) -> None:
    new_user_request = UserRequest(
        user_id=user_id,
        command=command,
        keyword=keyword,
        quantity=quantity,
        sort=sort,
        min_price=min_price,
        max_price=max_price,
    )
    session.add(new_user_request)
    await session.commit()


async def get_user_by_id(user_id: int) -> User:
    res = await session.execute(select(User).where(User.user_id == user_id))
    return res.scalar()
