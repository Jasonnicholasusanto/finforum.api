from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, func

from app.crud.base import CRUDBase
from app.models.user_profile import UserProfile
from app.schemas.user_profile import UserProfileCreate, UserProfileUpdate


class CRUDUserProfile(CRUDBase[UserProfile, UserProfileCreate, UserProfileUpdate]):
    # ---- Reads ----
    def get(self, session: Session, *, id: uuid.UUID) -> Optional[UserProfile]:
        return session.get(UserProfile, id)

    def get_by_auth_id(
        self, session: Session, *, auth_id: uuid.UUID
    ) -> Optional[UserProfile]:
        return session.exec(
            select(UserProfile).where(UserProfile.auth_id == auth_id)
        ).one_or_none()

    def get_by_username(
        self, session: Session, *, username: str
    ) -> Optional[UserProfile]:
        return session.exec(
            select(UserProfile).where(UserProfile.username == username)
        ).one_or_none()

    def get_by_email_lower(
        self, session: Session, *, email: str
    ) -> Optional[UserProfile]:
        """Lookup by case-insensitive email (compares on LOWER(email_address))."""
        return session.exec(
            select(UserProfile).where(
                func.lower(UserProfile.email_address) == email.strip().lower()
            )
        ).one_or_none()

    # ---- Writes ----
    def create(
        self,
        session: Session,
        *,
        obj_in: UserProfileCreate,
        auth_id: uuid.UUID,
    ) -> UserProfile:
        payload_auth = getattr(obj_in, "auth_id", None)
        if payload_auth and payload_auth != auth_id:
            raise ValueError("auth_id in payload disagrees with provided auth_id")

        try:
            return super().create(session, obj_in=obj_in, auth_id=auth_id)
        except IntegrityError:
            session.rollback()
            # e.g., if you later add UNIQUE(username) or UNIQUE(email_address)
            raise

    def update(
        self,
        session: Session,
        *,
        id: uuid.UUID,
        obj_in: UserProfileUpdate,
    ) -> Optional[UserProfile]:
        # Defensive: make it impossible to modify auth_id even if it appears in schema later
        if hasattr(obj_in, "auth_id") and getattr(obj_in, "auth_id") is not None:
            raise ValueError("auth_id cannot be modified.")
        try:
            return super().update(session, id=id, obj_in=obj_in)
        except IntegrityError:
            session.rollback()
            raise

    # ---- Domain-specific helpers ----
    def soft_delete(self, session: Session, *, id: uuid.UUID) -> Optional[UserProfile]:
        """
        Soft-delete by setting is_active = False and stamping deactivated_at (if present).
        Idempotent.
        """
        obj = self.get(session, id=id)
        if not obj:
            return None
        if obj.is_active is False:
            return obj

        obj.is_active = False
        if hasattr(obj, "deactivated_at"):
            obj.deactivated_at = datetime.now(timezone.utc)

        session.add(obj)
        try:
            session.commit()
        except Exception:
            session.rollback()
            raise
        session.refresh(obj)
        return obj

    def reactivate(self, session: Session, *, id: uuid.UUID) -> Optional[UserProfile]:
        """
        Reactivate: sets is_active = True and clears deactivated_at (if present).
        Idempotent.
        """
        obj = self.get(session, id=id)
        if not obj:
            return None
        if obj.is_active is True:
            return obj

        obj.is_active = True
        if hasattr(obj, "deactivated_at"):
            obj.deactivated_at = None

        session.add(obj)
        try:
            session.commit()
        except Exception:
            session.rollback()
            raise
        session.refresh(obj)
        return obj


user_profile = CRUDUserProfile(UserProfile)
