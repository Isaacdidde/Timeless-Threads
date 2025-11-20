from datetime import datetime, timedelta
from bson.objectid import ObjectId


class OTP:
    """
    OTP model that handles creating, validating, and invalidating OTP entries.
    This interacts with the `otps` collection and ensures OTPs:
        - expire after a time limit
        - cannot be reused
        - are associated with a mobile number
    """

    def __init__(self, mongo):
        # Reference to the "otps" collection in MongoDB
        self.db = mongo.db.otps

    # ---------------------------------------------------------
    # CREATE OTP
    #
    # Saves a new OTP document with:
    #   - mobile number
    #   - otp code
    #   - created timestamp
    #   - expiry timestamp
    #   - used flag (initially False)
    #
    # ttl_minutes defines how long the OTP stays valid.
    # ---------------------------------------------------------
    def create(self, mobile, otp, ttl_minutes=5):
        """
        Create a new OTP record and store it in the database.
        """
        # Compute expiration time based on TTL
        expires_at = datetime.utcnow() + timedelta(minutes=ttl_minutes)

        # Construct OTP document
        doc = {
            "mobile": mobile,
            "otp": str(otp),  # Always stored as string for consistency
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "used": False  # Ensures OTP can only be used once
        }

        # Insert into DB and return the inserted document
        result = self.db.insert_one(doc)
        return self.get_by_id(result.inserted_id)

    # ---------------------------------------------------------
    # VERIFY OTP
    #
    # Steps:
    #   1. Find OTP by mobile + otp + unused.
    #   2. Reject if no matching record.
    #   3. Reject if OTP is expired.
    #   4. Mark OTP as used (prevents reuse).
    #   5. Return True if valid.
    #
    # This ensures very strong OTP security.
    # ---------------------------------------------------------
    def verify(self, mobile, otp):
        """
        Check if the OTP is valid, not expired, and not used.
        """
        record = self.db.find_one({
            "mobile": mobile,
            "otp": str(otp),
            "used": False  # Prevents reusing old OTPs
        })

        if not record:
            return False

        # OTP expired
        if record["expires_at"] < datetime.utcnow():
            return False

        # Mark OTP as used so it cannot be used again
        self.db.update_one(
            {"_id": record["_id"]},
            {"$set": {"used": True}}
        )

        return True

    # ---------------------------------------------------------
    # GET BY ID
    #
    # Used mainly after insertion to fetch the exact created OTP.
    # ---------------------------------------------------------
    def get_by_id(self, otp_id):
        """
        Fetch an OTP document by its ID.
        """
        return self.db.find_one({"_id": ObjectId(otp_id)})

    # ---------------------------------------------------------
    # INVALIDATE OTP (Manual)
    #
    # Utility method that allows you to force-disable an OTP,
    # e.g. after suspicious activity or manual resend.
    # ---------------------------------------------------------
    def invalidate(self, otp_id):
        """
        Optional: manually mark an OTP as used.
        """
        return self.db.update_one(
            {"_id": ObjectId(otp_id)},
            {"$set": {"used": True}}
        )
