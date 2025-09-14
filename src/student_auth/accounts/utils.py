from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from typing import Tuple, Optional

from .models import Student


class _TokenRecord:
    """Lightweight token record to keep existing API (mark_as_used no-op)."""

    def __init__(self, token: str):
        self.token = token

    def mark_as_used(self) -> None:
        # For stateless tokens, usage is enforced by expiration only.
        return None


class PasswordResetToken:
    SALT = "accounts.PasswordReset"
    AGE_SECONDS = 15 * 60  # 15 minutes

    @classmethod
    def create_token(cls, student: Student) -> Tuple[str, _TokenRecord]:
        signer = TimestampSigner(salt=cls.SALT)
        raw = signer.sign(str(student.id))
        return raw, _TokenRecord(raw)

    @classmethod
    def verify_token(
        cls, token: str
    ) -> Tuple[Optional[Student], Optional[_TokenRecord]]:
        signer = TimestampSigner(salt=cls.SALT)
        try:
            value = signer.unsign(token, max_age=cls.AGE_SECONDS)
            sid = int(value)
            student = Student.objects.filter(id=sid).first()
            if not student:
                return None, None
            return student, _TokenRecord(token)
        except (BadSignature, SignatureExpired, ValueError):
            return None, None
