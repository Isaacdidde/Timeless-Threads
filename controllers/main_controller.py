# controllers/main_controller.py

from flask import render_template, abort
from database.connection import get_collection
from models.product_model import ProductModel

# Import TT → Dcorp ad fetcher
from utils.ads_client import fetch_ad


# =====================================================================
# CONTEXT PROCESSOR (Inject categories + ads into all templates)
# =====================================================================
def register_context_processors(app):

    @app.context_processor
    def inject_site_data():
        """Inject categories + ads into all Jinja templates.
        Production-safe: no exceptions allowed to bubble up.
        """

        # ---------------------------------------
        # LOAD CATEGORIES (never allowed to fail)
        # ---------------------------------------
        try:
            cat_col = get_collection("categories")
            categories = list(cat_col.find().sort("name", 1))
        except Exception as e:
            print("⚠ WARNING: Failed to load categories:", e)
            categories = []

        # ---------------------------------------
        # LOAD ADS FROM DCORP 
        # ---------------------------------------
        ads = {
            "home_banner": None,
            "featured_banner": None,
            "product_detail_banner": None,
            "product_inline": None,
            "card_small": None,
            "login_page_ad": None,
            "search_banner": None,
        }

        try:
            # Fetch each slot individually so one failure doesn't kill the rest
            for slot in ads.keys():
                try:
                    ads[slot] = fetch_ad(slot)
                except Exception as e:
                    print(f"⚠ WARNING: DCorp ad fetch failed for slot '{slot}':", e)
                    ads[slot] = None
        except Exception:
            pass  # failsafe fallback — do not break templates

        return dict(
            site_categories=categories,
            ads=ads
        )


# =====================================================================
# MAIN CONTROLLER (Homepage, Search, Static Pages)
# =====================================================================
class MainController:
    def __init__(self, mongo):
        try:
            self.mongo = mongo
            self.products = ProductModel(mongo)
        except Exception as e:
            print("❌ ERROR: Failed to initialize ProductModel:", e)
            self.mongo = None
            self.products = None

    # ---------------------------------------------------------------
    # HOMEPAGE
    # ---------------------------------------------------------------
    def home(self):
        """Load featured + latest products for homepage (production-safe)."""

        if not self.mongo or not self.products:
            abort(500, "Database unavailable")

        # Load featured products
        try:
            products_col = get_collection("products")
            featured_products = list(
                products_col.find({"featured": True}).sort("created_at", -1)
            )
        except Exception as e:
            print("⚠ WARNING: Failed to load featured products:", e)
            featured_products = []

        # Load latest products
        try:
            latest_products = self.products.list_all(limit=8)
        except Exception as e:
            print("⚠ WARNING: Failed to load latest products:", e)
            latest_products = []

        # Render homepage safely
        try:
            return render_template(
                "index.html",
                title="Home",
                featured_products=featured_products,
                products=latest_products,
            )
        except Exception as e:
            print("❌ ERROR: Failed to render homepage:", e)
            abort(500, "Rendering error")

    # ---------------------------------------------------------------
    # SEARCH
    # ---------------------------------------------------------------
    def search(self, query):
        """Handle full text search safely."""

        if not self.products:
            abort(500, "Database unavailable")

        clean_query = (query or "").strip()
        if not clean_query:
            return render_template(
                "search_results.html",
                title="Search",
                query=clean_query,
                results=[]
            )

        try:
            results = self.products.search(clean_query)
        except Exception as e:
            print("⚠ WARNING: Search failed:", e)
            results = []

        try:
            return render_template(
                "search_results.html",
                title=f"Search: {clean_query}",
                query=clean_query,
                results=results
            )
        except Exception as e:
            print("❌ ERROR: Failed to render search template:", e)
            abort(500, "Rendering error")

    # ---------------------------------------------------------------
    # FAQ PAGE
    # ---------------------------------------------------------------
    def faq(self):
        try:
            return render_template("faq.html", title="FAQ")
        except Exception as e:
            print("❌ ERROR: Failed to render FAQ page:", e)
            abort(500, "Rendering error")

    # ---------------------------------------------------------------
    # CONTACT PAGE
    # ---------------------------------------------------------------
    def contact(self):
        try:
            return render_template("contact.html", title="Contact")
        except Exception as e:
            print("❌ ERROR: Failed to render Contact page:", e)
            abort(500, "Rendering error")

    # ---------------------------------------------------------------
    # POLICIES PAGE
    # ---------------------------------------------------------------
    def policies(self):
        try:
            return render_template("policies.html", title="Policies")
        except Exception as e:
            print("❌ ERROR: Failed to render Policies page:", e)
            abort(500, "Rendering error")
