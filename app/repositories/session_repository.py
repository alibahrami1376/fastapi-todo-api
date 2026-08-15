from datetime import datetime, timezone

from sqlalchemy.orm import Session

from models.session import SessionModel


class SessionRepository:
    
    def __init__(self, db: Session):
        self.db = db

    def revoke_refresh_token(self, session: SessionModel) -> None:
        session.refresh_revoked_at = datetime.now(timezone.utc)
        self.db.commit()

    def create(
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

    def get_by_access_token_jti(
        self,
        jti: str,
    ) -> SessionModel | None:
        return (
            self.db.query(SessionModel)
            .filter_by(access_token_jti=jti)
            .first()
        )

    def get_by_refresh_token_jti(
        self,
        jti: str,
    ) -> SessionModel | None:
        return (
            self.db.query(SessionModel)
            .filter_by(refresh_token_jti=jti)
            .first()
        )

    def revoke_access_token(
        self,
        session: SessionModel,
    ) -> None:
        session.access_revoked_at = datetime.now(timezone.utc)
        self.db.commit()
