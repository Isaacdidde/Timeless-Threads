from bson.objectid import ObjectId


class ProductModel:
    """
    Model for interacting with the 'products' collection in MongoDB.

    Responsibilities:
        - Fetch products by category
        - Fetch a product by ID
        - Insert new product documents
        - List products with limit
        - Perform keyword-based search

    This model acts as a clean abstraction layer so controllers
    don't directly interact with MongoDB queries.
    """

    def __init__(self, mongo):
        # Bind the model to the 'products' collection
        self.db = mongo.db.products

    # ---------------------------------------------------------
    # GET ALL PRODUCTS IN A CATEGORY
    #
    # Example:
    #     model.get_by_category("shoes")
    # ---------------------------------------------------------
    def get_by_category(self, category_name):
        """
        Fetch all products belonging to a given category.
        Returns a list of documents.
        """
        return list(self.db.find({"category": category_name}))

    # ---------------------------------------------------------
    # GET A SINGLE PRODUCT BY ID
    #
    # Converts string ID to ObjectId safely.
    # Returns None if the ID is invalid.
    # ---------------------------------------------------------
    def get_by_id(self, pid):
        """
        Fetch a single product by its ObjectId.
        """
        try:
            return self.db.find_one({"_id": ObjectId(pid)})
        except Exception:
            # If the ID is not a valid ObjectId or any error occurs
            return None

    # ---------------------------------------------------------
    # LIST ALL PRODUCTS WITH LIMIT
    #
    # Useful for homepage, admin listings, category previews, etc.
    # ---------------------------------------------------------
    def list_all(self, limit=100):
        """
        Return all products up to a limit.
        """
        return list(self.db.find().limit(limit))

    # ---------------------------------------------------------
    # INSERT PRODUCT DOCUMENT
    #
    # product_data should be a dict containing:
    #     name, price, category, image, discount, etc.
    #
    # After insertion, fetch the created product document.
    # ---------------------------------------------------------
    def insert(self, product_data):
        """
        Insert a new product document.
        product_data is a dict with: name, price, image, category, discount, etc.
        """
        result = self.db.insert_one(product_data)
        return self.get_by_id(result.inserted_id)

    # ---------------------------------------------------------
    # SEARCH PRODUCTS BY NAME
    #
    # Case-insensitive search using MongoDB regex.
    # Example:
    #     model.search("shirt")
    #
    # Matches:
    #     "Blue Shirt"
    #     "shirt for men"
    # ---------------------------------------------------------
    def search(self, keyword):
        """
        Perform case-insensitive search on product name.
        """
        return list(
            self.db.find({
                "name": {"$regex": keyword, "$options": "i"}  # "i" → ignore case
            })
        )
