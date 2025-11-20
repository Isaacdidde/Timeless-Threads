import random
import time


class OTPService:
    """
    A lightweight, in-memory OTP (One-Time Password) manager.

    The OTPs are stored in a simple dictionary structure:
        {
            "<mobile_number>": {
                "otp": "<6-digit string>",
                "expiry": <unix timestamp when OTP expires>
            }
        }

    NOTE:
    - This is NOT persistent storage; data resets when the server restarts.
    - Ideal for demos, prototypes, or low-security local flows.
    """

    def __init__(self):
        # Internal storage for OTP data
        # Keys: mobile numbers (strings)
        # Values: {"otp": str, "expiry": float}
        self._store = {}

    def generate_otp(self, mobile: str, ttl_seconds: int = 300) -> str:
        """
        Generate a 6-digit OTP and store it with an expiry timestamp.

        :param mobile: Mobile number as a string
        :param ttl_seconds: Time-to-live for OTP (default: 300s = 5 minutes)
        :return: The generated OTP as a string
        """

        # Create a random 6-digit OTP.
        otp = f"{random.randint(100000, 999999)}"

        # Compute expiry time as current timestamp + TTL.
        expiry = time.time() + ttl_seconds

        # Save OTP record in memory.
        self._store[mobile] = {
            "otp": otp,
            "expiry": expiry
        }

        return otp

    def verify_otp(self, mobile: str, otp: str) -> bool:
        """
        Validate the OTP submitted by the user.

        Conditions for success:
        - OTP exists for the given mobile number
        - OTP is not expired
        - OTP matches the stored one

        :param mobile: Mobile number as string
        :param otp: OTP entered by the user
        :return: True if OTP is valid and used, False otherwise
        """

        # Fetch OTP record for this mobile number.
        record = self._store.get(mobile)

        # If no OTP exists → invalid attempt.
        if not record:
            return False

        # If current time has passed expiry → delete & reject.
        if time.time() > record["expiry"]:
            del self._store[mobile]  # cleanup expired code
            return False

        # If OTP matches → delete (single-use) and accept.
        if record["otp"] == str(otp):
            del self._store[mobile]
            return True

        # OTP did not match → invalid.
        return False


# -----------------------------------------------------------
# Singleton instance
# Use otp_service.generate_otp() and otp_service.verify_otp()
# across your application for consistent OTP handling.
# -----------------------------------------------------------
otp_service = OTPService()
