from bson.objectid import ObjectId


class UserModel:
    """
    Data access layer for the 'users' collection.

    Responsibilities:
        - Find user by mobile number
        - Create new user documents
        - Retrieve user by ID

    This model provides a clean abstraction so controllers
    do not need to interact directly with MongoDB queries.
    """

    def __init__(self, mongo):
        # Reference to MongoDB 'users' collection
        self.db = mongo.db.users

    # ---------------------------------------------------------
    # FIND USER BY MOBILE NUMBER
    #
    # Mobile numbers act as unique identifiers for login/signup.
    # Returns:
    #   - user document if found
    #   - None if mobile is not registered
    # ---------------------------------------------------------
    def find_by_mobile(self, mobile):
        """
        Return a user by their mobile number.
        """
        return self.db.find_one({"mobile": mobile})

    # ---------------------------------------------------------
    # CREATE NEW USER DOCUMENT
    #
    # Stores the user's mobile number and any additional fields.
    # extra can include:
    #     name, email, address, or other profile info.
    #
    # After inserting, returns the complete created user document.
    # ---------------------------------------------------------
    def create(self, mobile, extra=None):
        """
        Create a new user document.

        extra = optional dict for additional fields:
            name, email, address, etc.
        """
        data = {"mobile": mobile}

        # Merge extra fields only if provided and is a dictionary
        if extra and isinstance(extra, dict):
            data.update(extra)

        # Insert into DB and fetch the new user document
        result = self.db.insert_one(data)
        return self.get_by_id(result.inserted_id)

    # ---------------------------------------------------------
    # GET USER BY OBJECT ID
    #
    # Accepts string or ObjectId formats.
    #
    # If the provided user_id is invalid (not ObjectId), it
    # safely returns None instead of crashing the application.
    # ---------------------------------------------------------
    def get_by_id(self, user_id):
        """
        Fetch user by ObjectId safely.
        """
        try:
            return self.db.find_one({"_id": ObjectId(user_id)})
        except Exception:
            # Invalid user_id → return None instead of raising error
            return None
