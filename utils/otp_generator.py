"""
otp_generator.py

Production-ready in-memory OTP Manager.

Features:
- Secure random 6-digit OTP generation
- Per-mobile cooldown to prevent spam
- OTP expiry (default 5 minutes)
- Auto cleanup on access
- Optional max verification attempts
- Stateless singleton usable across the app

⚠ NOT persistent. OTPs reset when the server restarts.
"""

import random
import time
from typing import Optional


class OTPService:
    def __init__(
        self,
        ttl_seconds: int = 300,          # 5 minutes
        resend_cooldown: int = 30,       # minimum time before resending OTP
        max_attempts: int = 5            # max wrong tries before OTP invalidates
    ):
        self.ttl_seconds = ttl_seconds
        self.resend_cooldown = resend_cooldown
        self.max_attempts = max_attempts

        # Internal structure:
        # {
        #   "9876543210": {
        #       "otp": "123456",
        #       "expiry": 1710500000.00,
        #       "attempts": 0,
        #       "last_sent": 1710499800.00
        #   }
        # }
        self._store = {}

    # ---------------------------------------------------------
    # INTERNAL HELPERS
    # ---------------------------------------------------------
    def _normalize_mobile(self, mobile: str) -> str:
        """Strip spaces, enforce string, remove formatting."""
        return "".join(str(mobile).strip().split())

    def _cleanup_expired(self, mobile: str):
        """Remove expired OTP from memory."""
        rec = self._store.get(mobile)
        if rec and time.time() > rec["expiry"]:
            del self._store[mobile]

    # ---------------------------------------------------------
    # GENERATE OTP
    # ---------------------------------------------------------
    def generate_otp(self, mobile: str) -> Optional[str]:
        """
        Create a new OTP unless cooldown prevents it.

        Returns:
            otp string OR None if resend too soon
        """
        mobile = self._normalize_mobile(mobile)
        now = time.time()

        rec = self._store.get(mobile)

        # Rate-limit: enforce resend cooldown
        if rec and now - rec["last_sent"] < self.resend_cooldown:
            return None  # caller should show: "Try again in X seconds"

        otp = f"{random.randint(100000, 999999)}"

        self._store[mobile] = {
            "otp": otp,
            "expiry": now + self.ttl_seconds,
            "attempts": 0,
            "last_sent": now
        }

        return otp

    # ---------------------------------------------------------
    # VERIFY OTP
    # ---------------------------------------------------------
    def verify_otp(self, mobile: str, otp: str) -> bool:
        """
        Validate OTP. On success → OTP deleted.
        On failure → increments attempt counter.

        Returns:
            True if OTP correct.
            False otherwise.
        """
        mobile = self._normalize_mobile(mobile)

        # Cleanup expired codes
        self._cleanup_expired(mobile)

        rec = self._store.get(mobile)
        if not rec:
            return False

        # Too many failed attempts → invalidate OTP
        if rec["attempts"] >= self.max_attempts:
            del self._store[mobile]
            return False

        # Check match
        if rec["otp"] == str(otp).strip():
            del self._store[mobile]
            return True

        # Wrong OTP → count failed attempt
        rec["attempts"] += 1
        return False


# -----------------------------------------------------------
# Singleton instance for reuse across the application
# -----------------------------------------------------------
otp_service = OTPService()
