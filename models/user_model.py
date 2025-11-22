from bson.objectid import ObjectId


class UserModel:
    """
    Data access layer for the 'users' collection.

    Responsibilities:
        - Find user by email
        - Create new user documents
        - Retrieve user by ID

    This model abstracts MongoDB logic away from controllers.
    """

    def __init__(self, mongo):
        # Connect to the users collection
        self.db = mongo.db.users

    # ---------------------------------------------------------
    # FIND USER BY EMAIL
    #
    # Email is now the unique identifier.
    # Returns:
    #   - user document if found
    #   - None if email is not registered
    # ---------------------------------------------------------
    def find_by_email(self, email):
        """
        Return a user by email address.
        """
        return self.db.find_one({"email": email})

    # ---------------------------------------------------------
    # CREATE NEW USER DOCUMENT
    #
    # Stores the user's email and any additional fields.
    # extra can include:
    #     name, address, role etc.
    #
    # After inserting, returns the complete created user document.
    # ---------------------------------------------------------
    def create(self, email, extra=None):
        """
        Create a new user document.

        extra = optional dict for additional fields:
            name, address, profile info, etc.
        """
        data = {"email": email}

        # Add any additional fields
        if extra and isinstance(extra, dict):
            data.update(extra)

        # Insert into DB and return the newly created user
        result = self.db.insert_one(data)
        return self.get_by_id(result.inserted_id)

    # ---------------------------------------------------------
    # GET USER BY OBJECT ID
    #
    # Accepts string or ObjectId formats.
    # If user_id is invalid → safely returns None.
    # ---------------------------------------------------------
    def get_by_id(self, user_id):
        """
        Fetch user by ObjectId safely.
        """
        try:
            return self.db.find_one({"_id": ObjectId(user_id)})
        except Exception:
            # Invalid ID format
            return None
