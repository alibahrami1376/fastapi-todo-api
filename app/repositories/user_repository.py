from datetime import datetime, timezone

from sqlalchemy.orm import Session

from models import UserModel


class UserRepository:
    """Repository class for managing user-related database operations."""
    
    def __init__(self, db: Session):
        self.db = db

    async def get_by_email(self, email: str) -> UserModel | None:
        return (
            self.db.query(UserModel)
            .filter_by(email=email)
            .first()
        )

    async def get_by_username(self, username: str) -> UserModel | None:
        return (
            self.db.query(UserModel)
            .filter_by(username=username)
            .first()
        )

    async def get_by_id(self, user_id: int) -> UserModel | None:
        return (
            self.db.query(UserModel)
            .filter_by(id=user_id)
            .first()
        )

    async def create_user(
        self,
        email: str,
        password: str,
    ) -> UserModel:
        user = UserModel(
            email=email,
            username=UserModel.generate_random_username(),
        )
        user.set_password(password)

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    async def update_user(self, user: UserModel) -> UserModel:
        self.db.commit()
        self.db.refresh(user)

        return user

    async def delete_user(self, user: UserModel) -> None:
        user.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(user)