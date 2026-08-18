from datetime import datetime, timezone

from models.session import SessionModel
from sqlalchemy.orm import Session


class SessionRepository:
    def __init__(self, db: Session):
        self.db = db

    async def revoke_refresh_token(self, session: SessionModel) -> None:
        session.refresh_revoked_at = datetime.now(timezone.utc)
        self.db.commit()

    async def create(
        self,
        user_id: int,
        access_token_jti: str,
        refresh_token_jti: str,
        access_expires_at: datetime,
        refresh_expires_at: datetime,
    ) -> SessionModel:

        session = SessionModel(
            user_id=user_id,
            access_token_jti=access_token_jti,
            refresh_token_jti=refresh_token_jti,
            access_expires_at=access_expires_at,
            refresh_expires_at=refresh_expires_at,
        )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session

    async def get_by_access_token_jti(
        self,
        jti: str,
    ) -> SessionModel | None:
        return self.db.query(SessionModel).filter_by(access_token_jti=jti).first()

    async def get_by_refresh_token_jti(
        self,
        jti: str,
    ) -> SessionModel | None:
        return self.db.query(SessionModel).filter_by(refresh_token_jti=jti).first()

    async def revoke_access_token(
        self,
        session: SessionModel,
    ) -> None:
        session.access_revoked_at = datetime.now(timezone.utc)
        self.db.commit()
