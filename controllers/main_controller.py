from flask import render_template
from models.product_model import ProductModel


class MainController:
    def __init__(self, mongo):
        self.products = ProductModel(mongo)
        self.mongo = mongo

    def home(self):
        """Load featured products for homepage."""
        product_list = []
        if self.mongo:
            product_list = self.products.list_all(limit=8)
        return render_template("index.html", title="Home", products=product_list)

    def search(self, query):
        """Perform search using product model."""
        if not query or not self.mongo:
            return render_template(
                "search_results.html",
                title=f"Search: {query}",
                query=query,
                results=[]
            )

        results = self.products.search(query)
        return render_template(
            "search_results.html",
            title=f"Search: {query}",
            query=query,
            results=results
        )

    def faq(self):
        return render_template("faq.html", title="FAQ")

    def contact(self):
        return render_template("contact.html", title="Contact")

    def policies(self):
        return render_template("policies.html", title="Policies")
