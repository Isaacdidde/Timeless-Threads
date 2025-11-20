"""
Full seed.py for Timeless Threads
---------------------------------
Enhancements:
 - Automatically generates: image2, image3
 - Adds sizes[] and colors[] (default values if missing)
 - Preserves your original structure
 - Supports new UI features

Run:
    python seed.py
"""

from pymongo import MongoClient
import datetime
import os

# ---------------------------------------------------------
# DB CONNECT
# ---------------------------------------------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["timeless_threads"]

products_col = db["products"]
categories_col = db["categories"]

print("\n⚠ Clearing existing collections...")
products_col.delete_many({})
categories_col.delete_many({})
print("✔ Old data cleared.\n")

# ---------------------------------------------------------
# CATEGORY SEED
# ---------------------------------------------------------
categories = [
    {"name": "ethnic", "display_name": "Ethnic Wear", "image": "ethnic.jpg"},
    {"name": "sarees", "display_name": "Sarees", "image": "saree.jpg"},
    {"name": "casual", "display_name": "Women's Casual Wear", "image": "casual.jpg"},
    {"name": "cosmetics", "display_name": "Cosmetics", "image": "cosmetics.jpg"},
]

categories_col.insert_many(categories)
print("✔ Categories inserted.\n")


# ---------------------------------------------------------
# Helper: Add image2 & image3 based on image
# ---------------------------------------------------------
def add_multi_images(product):
    base = product["image"]          # e.g. "kurti_set.jpg"
    name, ext = os.path.splitext(base)

    product["image2"] = f"{name}_2{ext}"
    product["image3"] = f"{name}_3{ext}"

    return product


# ---------------------------------------------------------
# Helper: Ensure sizes[] and colors[] exist
# ---------------------------------------------------------
DEFAULT_SIZES = ["S", "M", "L", "XL"]
DEFAULT_COLORS = ["Red", "Blue", "Black"]

def add_missing_variants(product):
    if "sizes" not in product:
        product["sizes"] = DEFAULT_SIZES

    if "colors" not in product:
        product["colors"] = DEFAULT_COLORS

    return product


# ---------------------------------------------------------
# ORIGINAL PRODUCT LIST (UNTOUCHED)
# ---------------------------------------------------------
products = [
    # … your entire product list …
      # =========================
    # ETHNIC WEAR
    # =========================
    {
        "name": "Embroidered Kurti Set",
        "category": "ethnic",
        "price": 1499,
        "discount": 10,
        "image": "kurti_set.jpg",
        "description": "Beautiful embroidered kurti with matching palazzo pants.",
        "highlights": [
            "Premium rayon fabric — soft & breathable",
            "Hand-stitched floral embroidery on yoke",
            "Includes matching palazzo pants",
        ],
        "details": {
            "Fabric": "Rayon",
            "Fit": "Regular",
            "Sleeve": "3/4 sleeve",
            "Care": "Hand wash / Gentle machine wash",
            "Occasion": "Casual, Festive"
        }
    },

    {
        "name": "Lehenga Choli",
        "category": "ethnic",
        "price": 3499,
        "discount": 20,
        "image": "lehenga_red.jpg",
        "description": "Traditional lehenga choli set with zari embroidery.",
        "highlights": [
            "Rich zari and gota work",
            "Full flare lehenga with matching dupatta",
            "Ideal for weddings and heavy occasions"
        ],
        "details": {
            "Fabric": "Silk blend",
            "Lining": "Soft cotton lining",
            "Work": "Zari & gota",
            "Wash": "Dry clean",
            "Occasion": "Weddings, Festive"
        }
    },

    {
        "name": "Anarkali Dress",
        "category": "ethnic",
        "price": 2299,
        "discount": 15,
        "image": "anarkali.jpg",
        "description": "Flowy, festive Anarkali dress perfect for celebrations.",
        "highlights": [
            "Floor-length Anarkali silhouette",
            "Lightweight georgette fabric",
            "Embellished neckline for sparkle"
        ],
        "details": {
            "Fabric": "Georgette",
            "Length": "Ankle length",
            "Fit": "Flared",
            "Care": "Dry clean recommended",
            "Occasion": "Parties, Festive"
        }
    },

    {
        "name": "Block print kurti set",
        "category": "ethnic",
        "price": 1299,
        "discount": 21,
        "image": "black_suit.jpg",
        "description": "Hand-block printed kurti with matching bottoms.",
        "highlights": [
            "Traditional block print motifs",
            "Breathable cotton blend",
            "Casual-to-office versatile style"
        ],
        "details": {
            "Fabric": "Cotton blend",
            "Includes": "Kurti + bottom",
            "Fit": "Straight fit",
            "Care": "Machine wash cold",
            "Occasion": "Daily, Office"
        }
    },

    {
        "name": "Mirror Work Kurta",
        "category": "ethnic",
        "price": 1299,
        "discount": 10,
        "image": "mirror_work_kurta.jpg",
        "description": "Hand-stitched mirror work kurta with subtle details.",
        "highlights": [
            "Traditional mirror embellishments",
            "Comfortable breathable fabric",
            "Festive-ready with minimal effort"
        ],
        "details": {
            "Fabric": "Cotton rayon",
            "Work": "Mirror work",
            "Sleeve": "Full sleeve",
            "Care": "Hand wash",
            "Occasion": "Festive, Casual"
        }
    },

    {
        "name": "Embellished Dupatta",
        "category": "ethnic",
        "price": 499,
        "discount": 5,
        "image": "embellished_dupatta.jpg",
        "description": "Lightweight dupatta with shimmering borders.",
        "highlights": [
            "Delicate sequin / zari border",
            "Sheer and flowy — pairs with many suits",
            "Lightweight for layering"
        ],
        "details": {
            "Fabric": "Chiffon / Georgette",
            "Length": "2.2 m approx.",
            "Care": "Gentle hand wash",
            "Occasion": "Festive, Wedding"
        }
    },

    {
        "name": "Thread Embroidery Kurta",
        "category": "ethnic",
        "price": 1599,
        "discount": 12,
        "image": "thread_embroidery_kurta.jpg",
        "description": "Finely embroidered kurta with delicate threadwork.",
        "highlights": [
            "Intricate thread embroidery",
            "Lightweight & breathable",
            "Classic silhouette"
        ],
        "details": {
            "Fabric": "Cotton rayon",
            "Fit": "Regular",
            "Sleeve": "3/4th sleeve",
            "Care": "Hand wash or gentle machine wash",
            "Occasion": "Casual, Festive"
        }
    },

    {
        "name": "Silk Anarkali Gown",
        "category": "ethnic",
        "price": 2799,
        "discount": 15,
        "image": "silk_anarkali_gown.jpg",
        "description": "Luxurious silk Anarkali gown with elegant flair.",
        "highlights": [
            "Rich silk fabric feel",
            "Elegant flare & heavy border",
            "Perfect for evening events"
        ],
        "details": {
            "Fabric": "Silk blend",
            "Length": "Floor length",
            "Work": "Zari border",
            "Care": "Dry clean only",
            "Occasion": "Weddings, Parties"
        }
    },

    {
        "name": "Block Print Kurta Set",
        "category": "ethnic",
        "price": 999,
        "discount": 8,
        "image": "block_print_kurta_set.jpg",
        "description": "Affordable block-printed kurta and bottom set.",
        "highlights": [
            "Hand-block prints",
            "Lightweight everyday wear",
            "Budget-friendly"
        ],
        "details": {
            "Fabric": "Cotton",
            "Includes": "Kurta + bottom",
            "Fit": "Regular",
            "Care": "Machine wash",
            "Occasion": "Daily, Casual"
        }
    },

    {
        "name": "Phulkari Jacket",
        "category": "ethnic",
        "price": 1899,
        "discount": 10,
        "image": "phulkari_jacket.jpg",
        "description": "Colorful Phulkari jacket to layer over kurtis.",
        "highlights": [
            "Traditional Phulkari embroidery",
            "Structured jacket style",
            "Statement ethnic outerwear"
        ],
        "details": {
            "Fabric": "Cotton blend",
            "Work": "Phulkari embroidery",
            "Lining": "Soft cotton",
            "Care": "Dry clean recommended",
            "Occasion": "Festive, Casual"
        }
    },

    {
        "name": "Banarasi Lehenga Peach",
        "category": "ethnic",
        "price": 4599,
        "discount": 20,
        "image": "banarasi_lehenga_peach.jpg",
        "description": "Banarasi lehenga in peach with golden zari work.",
        "highlights": [
            "Classic Banarasi motifs",
            "Luxurious golden zari",
            "Bridal & special occasion ready"
        ],
        "details": {
            "Fabric": "Banarasi silk",
            "Work": "Zari weave",
            "Care": "Dry clean",
            "Occasion": "Weddings, Special Events"
        }
    },

    {
        "name": "Cotton Churidar Set",
        "category": "ethnic",
        "price": 899,
        "discount": 5,
        "image": "cotton_churidar_set.jpg",
        "description": "Comfortable cotton churidar set for daily wear.",
        "highlights": [
            "Soft breathable cotton",
            "Comfortable churidar bottom",
            "Easy daily wear"
        ],
        "details": {
            "Fabric": "Cotton",
            "Fit": "Slim",
            "Care": "Machine wash",
            "Occasion": "Daily, Work"
        }
    },

    {
        "name": "Embroidered Waistcoat",
        "category": "ethnic",
        "price": 699,
        "discount": 0,
        "image": "embroidered_waistcoat.jpg",
        "description": "Ethnic waistcoat to elevate kurta looks.",
        "highlights": [
            "Subtle embroidery",
            "Tailored fit",
            "Multipurpose layering piece"
        ],
        "details": {
            "Fabric": "Cotton blend",
            "Closure": "Button",
            "Care": "Spot clean / Dry clean",
            "Occasion": "Festive, Party"
        }
    },

    {
        "name": "Festive Stole",
        "category": "ethnic",
        "price": 349,
        "discount": 0,
        "image": "festive_stole.jpg",
        "description": "Light festive stole to pair with suits and sarees.",
        "highlights": [
            "Versatile accessory",
            "Soft finish and lightweight",
            "Gives ethnic outfits a polished look"
        ],
        "details": {
            "Fabric": "Viscose",
            "Length": "2.0 m approx.",
            "Care": "Hand wash",
            "Occasion": "Festive, Ethnic"
        }
    },

    # =========================
    # SAREES (ALL YOUR DATA)
    # =========================
    {
        "name": "Banarasi Silk Saree",
        "category": "sarees",
        "price": 1999,
        "discount": 10,
        "image": "banarasi_saree.jpg",
        "description": "Pure silk Banarasi saree with golden zari border.",
        "highlights": [
            "Rich Banarasi texture",
            "Elegant golden zari border",
            "Traditional weaving techniques"
        ],
        "details": {
            "Fabric": "Silk blend",
            "Length": "5.5 m",
            "Work": "Zari border",
            "Care": "Dry clean",
            "Occasion": "Weddings, Festive"
        }
    },

    {
        "name": "Kanjivaram Saree",
        "category": "sarees",
        "price": 3499,
        "discount": 15,
        "image": "kanjivaram.jpg",
        "description": "Handwoven Kanjivaram saree with traditional patterns.",
        "highlights": [
            "Classic Kanjivaram weave",
            "Heavy silk drape",
            "Regal patterns and borders"
        ],
        "details": {
            "Fabric": "Pure silk",
            "Length": "5.5 m",
            "Care": "Dry clean only",
            "Occasion": "Weddings, Ceremonies"
        }
    },

    {
        "name": "Printed Georgette Saree",
        "category": "sarees",
        "price": 1299,
        "discount": 5,
        "image": "georgette_saree.jpg",
        "description": "Soft georgette saree with modern printed design.",
        "highlights": [
            "Lightweight georgette fabric",
            "Contemporary prints for everyday elegance",
            "Easy pleating & drape"
        ],
        "details": {
            "Fabric": "Georgette",
            "Length": "5.5 m",
            "Care": "Hand wash / Dry clean",
            "Occasion": "Parties, Casual"
        }
    },

    {
        "name": "Silk Blend Banarasi",
        "category": "sarees",
        "price": 2199,
        "discount": 10,
        "image": "silk_blend_banarasi.jpg",
        "description": "Silk-blend Banarasi look for a modern budget-friendly touch.",
        "highlights": [
            "Banarasi motifs with silk blend",
            "Good sheen and fall",
            "Great for festive wear"
        ],
        "details": {
            "Fabric": "Silk blend",
            "Length": "5.5 m",
            "Care": "Dry clean",
            "Occasion": "Festive"
        }
    },

    {
        "name": "Cotton Handloom Saree",
        "category": "sarees",
        "price": 1199,
        "discount": 5,
        "image": "cotton_handloom_saree.jpg",
        "description": "Comfortable handloom cotton saree for everyday grace.",
        "highlights": [
            "Handloom texture & subtle stripes",
            "Breathable & comfortable",
            "Perfect for work and daily wear"
        ],
        "details": {
            "Fabric": "Handloom cotton",
            "Length": "5.5 m",
            "Care": "Gentle machine wash",
            "Occasion": "Office, Casual"
        }
    },

    {
        "name": "Chiffon Party Saree",
        "category": "sarees",
        "price": 899,
        "discount": 10,
        "image": "chiffon_party_saree.jpg",
        "description": "Flowy chiffon saree with subtle sequin border.",
        "highlights": [
            "Sheer chiffon drape",
            "Sequin trimmed border for sparkle",
            "Light and easy to style"
        ],
        "details": {
            "Fabric": "Chiffon",
            "Length": "5.5 m",
            "Work": "Sequin border",
            "Care": "Dry clean recommended",
            "Occasion": "Parties"
        }
    },

    {
        "name": "Kota Doria Saree",
        "category": "sarees",
        "price": 1399,
        "discount": 12,
        "image": "kota_doria_saree.jpg",
        "description": "Traditional Kota Doria saree — sheer and comfortable.",
        "highlights": [
            "Lightweight cotton weave",
            "Subtle checks & sheer body",
            "Great for summer events"
        ],
        "details": {
            "Fabric": "Kota Doria cotton",
            "Length": "5.5 m",
            "Care": "Gentle wash",
            "Occasion": "Daytime functions"
        }
    },

    {
        "name": "Designer Georgette Saree",
        "category": "sarees",
        "price": 1699,
        "discount": 15,
        "image": "designer_georgette_saree.jpg",
        "description": "Designer drape with embroidered motifs.",
        "highlights": [
            "Embroidered accents",
            "Rich print & fall",
            "Premium partywear option"
        ],
        "details": {
            "Fabric": "Georgette with embroidery",
            "Length": "5.5 m",
            "Care": "Dry clean",
            "Occasion": "Parties"
        }
    },

    {
        "name": "Silk Printed Saree",
        "category": "sarees",
        "price": 1299,
        "discount": 8,
        "image": "silk_printed_saree.jpg",
        "description": "Printed silk saree with modern motifs.",
        "highlights": [
            "Silk-like sheen with printed design",
            "Great for semi-formal occasions",
            "Elegant & low-maintenance"
        ],
        "details": {
            "Fabric": "Silk blend (printed)",
            "Length": "5.5 m",
            "Care": "Dry clean",
            "Occasion": "Semi-formal"
        }
    },

    {
        "name": "Bandhani Saree",
        "category": "sarees",
        "price": 1499,
        "discount": 10,
        "image": "bandhani_saree.jpg",
        "description": "Traditional Bandhani tie-dye saree with vibrant patterns.",
        "highlights": [
            "Authentic Bandhani patterns",
            "Bold color palettes",
            "Festive & cultural appeal"
        ],
        "details": {
            "Fabric": "Cotton / Silk blend",
            "Length": "5.5 m",
            "Care": "Hand wash",
            "Occasion": "Festivals"
        }
    },

    {
        "name": "Organza Saree",
        "category": "sarees",
        "price": 1899,
        "discount": 18,
        "image": "organza_saree.jpg",
        "description": "Sheer organza saree with delicate border work.",
        "highlights": [
            "Delicate sheer body",
            "Subtle zari border",
            "Lightweight & elegant"
        ],
        "details": {
            "Fabric": "Organza",
            "Length": "5.5 m",
            "Care": "Dry clean",
            "Occasion": "Evening events"
        }
    },

    {
        "name": "Tussar Silk Saree",
        "category": "sarees",
        "price": 2099,
        "discount": 12,
        "image": "tussar_silk_saree.jpg",
        "description": "Tussar silk saree with rustic charm and soft fall.",
        "highlights": [
            "Natural tussar texture",
            "Earthy, rustic tones",
            "Handloom appeal"
        ],
        "details": {
            "Fabric": "Tussar silk",
            "Length": "5.5 m",
            "Care": "Dry clean",
            "Occasion": "Cultural events"
        }
    },

    {
        "name": "Mughal Print Saree",
        "category": "sarees",
        "price": 999,
        "discount": 5,
        "image": "mughal_print_saree.jpg",
        "description": "Mughal-inspired prints in an elegant saree.",
        "highlights": [
            "Classic Mughal prints",
            "Lightweight comfortable fabric",
            "Great for casual parties"
        ],
        "details": {
            "Fabric": "Viscose / Blend",
            "Length": "5.5 m",
            "Care": "Hand wash",
            "Occasion": "Casual & semi-formal"
        }
    },


    # =========================
    # CASUAL (ALL 10)
    # =========================
    {
        "name": "Floral Summer Dress",
        "category": "casual",
        "price": 899,
        "discount": 10,
        "image": "floral_summer_dress.jpg",
        "description": "Breezy floral summer dress for sunny days.",
        "highlights": [
            "Lightweight breathable fabric",
            "Floral print with flattering cut",
            "Easy to style with sandals"
        ],
        "details": {
            "Fabric": "Cotton blend",
            "Fit": "A-line",
            "Length": "Knee length",
            "Care": "Machine wash",
            "Occasion": "Casual, Day out"
        }
    },

    {
        "name": "Denim Jacket Light Wash",
        "category": "casual",
        "price": 1499,
        "discount": 15,
        "image": "denim_jacket_light.jpg",
        "description": "Classic light wash denim jacket with modern fit.",
        "highlights": [
            "Durable denim construction",
            "Light wash for vintage appeal",
            "Pairs with dresses and jeans"
        ],
        "details": {
            "Fabric": "Denim (cotton)",
            "Fit": "Regular",
            "Care": "Machine wash cold",
            "Closure": "Button",
            "Occasion": "Casual"
        }
    },

    {
        "name": "Linen Shirt Dress",
        "category": "casual",
        "price": 1199,
        "discount": 8,
        "image": "linen_shirt_dress.jpg",
        "description": "Relaxed linen shirt dress for effortless style.",
        "highlights": [
            "Breathable linen fabric",
            "Relaxed shirt silhouette",
            "Ideal for warm weather"
        ],
        "details": {
            "Fabric": "Linen blend",
            "Fit": "Relaxed",
            "Length": "Midi",
            "Care": "Hand wash / gentle cycle",
            "Occasion": "Casual, Beach"
        }
    },

    {
        "name": "Casual Wrap Top",
        "category": "casual",
        "price": 549,
        "discount": 5,
        "image": "casual_wrap_top.jpg",
        "description": "Soft wrap top with adjustable tie detail.",
        "highlights": [
            "Wrap-front for adjustable fit",
            "Soft jersey fabric",
            "Great for layering"
        ],
        "details": {
            "Fabric": "Jersey knit",
            "Fit": "Adjustable wrap",
            "Care": "Machine wash",
            "Occasion": "Daily, Office casual"
        }
    },

    {
        "name": "Palazzo Cotton Pants",
        "category": "casual",
        "price": 799,
        "discount": 10,
        "image": "palazzo_cotton_pants.jpg",
        "description": "Wide-leg palazzo pants in soft cotton.",
        "highlights": [
            "Comfortable wide-leg silhouette",
            "Elastic waistband for comfort",
            "Breathable cotton"
        ],
        "details": {
            "Fabric": "Cotton",
            "Waist": "Elastic / drawstring",
            "Fit": "Relaxed",
            "Care": "Machine wash",
            "Occasion": "Casual, Travel"
        }
    },

    {
        "name": "Striped Tee",
        "category": "casual",
        "price": 399,
        "discount": 0,
        "image": "striped_tee.jpg",
        "description": "Classic striped t-shirt for everyday wear.",
        "highlights": [
            "Soft cotton tee",
            "Timeless striped design",
            "Versatile wardrobe staple"
        ],
        "details": {
            "Fabric": "Cotton",
            "Fit": "Regular",
            "Care": "Machine wash",
            "Occasion": "Daily"
        }
    },

    {
        "name": "High Waist Jeans",
        "category": "casual",
        "price": 1599,
        "discount": 12,
        "image": "high_waist_jeans.jpg",
        "description": "Slim-fit high-waist jeans for a flattering silhouette.",
        "highlights": [
            "Stretch denim for comfort",
            "High-rise for shape",
            "Everyday durable style"
        ],
        "details": {
            "Fabric": "Denim with stretch",
            "Fit": "Slim",
            "Closure": "Zip & button",
            "Care": "Machine wash cold",
            "Occasion": "Casual"
        }
    },

    {
        "name": "Casual Maxi Skirt",
        "category": "casual",
        "price": 699,
        "discount": 5,
        "image": "casual_maxi_skirt.jpg",
        "description": "Flowy maxi skirt with comfortable waistband.",
        "highlights": [
            "Soft flowy fabric",
            "Comfortable elastic waist",
            "Pairs well with tees and blouses"
        ],
        "details": {
            "Fabric": "Viscose blend",
            "Length": "Maxi",
            "Waist": "Elastic",
            "Care": "Machine wash",
            "Occasion": "Casual"
        }
    },

    {
        "name": "Printed Kimono",
        "category": "casual",
        "price": 999,
        "discount": 10,
        "image": "printed_kimono.jpg",
        "description": "Light printed kimono jacket — an easy statement piece.",
        "highlights": [
            "Versatile layering piece",
            "Open-front, relaxed fit",
            "Bold prints for interest"
        ],
        "details": {
            "Fabric": "Polyester chiffon",
            "Fit": "Relaxed",
            "Care": "Hand wash",
            "Occasion": "Casual, Resort"
        }
    },

    {
        "name": "Everyday Hoodie",
        "category": "casual",
        "price": 1299,
        "discount": 15,
        "image": "everyday_hoodie.jpg",
        "description": "Cozy hoodie for cooler evenings and casual comfort.",
        "highlights": [
            "Soft fleece lining",
            "Adjustable drawstring hood",
            "Perfect for layering"
        ],
        "details": {
            "Fabric": "Cotton fleece",
            "Fit": "Regular",
            "Care": "Machine wash",
            "Occasion": "Casual"
        }
    },

    # =========================
    # COSMETICS (ALL 13)
    # =========================
    {
        "name": "Matte Lipstick Set",
        "category": "cosmetics",
        "price": 599,
        "discount": 5,
        "image": "lipstick_set.jpg",
        "description": "Pack of 6 matte long-lasting lipsticks.",
        "highlights": [
            "6 versatile matte shades",
            "Long-wear formula",
            "Creamy application, non-drying"
        ],
        "details": {
            "Type": "Matte lipstick set",
            "Net wt": "6 x 3.5 g",
            "Finish": "Matte",
            "Cruelty-free": True,
            "Shelf life": "24 months"
        }
    },

    {
        "name": "Waterproof Kajal",
        "category": "cosmetics",
        "price": 199,
        "discount": 10,
        "image": "kajal.jpg",
        "description": "24-hour waterproof kajal stick.",
        "highlights": [
            "Smudge-proof and long-lasting",
            "Intense black pigment",
            "Easy glide applicator"
        ],
        "details": {
            "Type": "Kajal stick",
            "Net wt": "1.5 g",
            "Waterproof": True,
            "Safe for eyes": True,
            "Shelf life": "36 months"
        }
    },

    {
        "name": "Sandalwood Face Cream",
        "category": "cosmetics",
        "price": 299,
        "discount": 8,
        "image": "face_cream.jpg",
        "description": "Natural sandalwood cream for glowing skin.",
        "highlights": [
            "Sandalwood extract for soothing",
            "Light, non-greasy texture",
            "Everyday hydration"
        ],
        "details": {
            "Type": "Face cream",
            "Net wt": "50 g",
            "Skin type": "All skin types",
            "Paraben-free": True,
            "Shelf life": "24 months"
        }
    },

    {
        "name": "Matte Lipstick - Berry",
        "category": "cosmetics",
        "price": 599,
        "discount": 5,
        "image": "matte_lipstick_berry.jpg",
        "description": "Long-wear matte lipstick in rich berry shade.",
        "highlights": [
            "High pigment payoff",
            "Long-lasting matte finish",
            "Comfortable wear"
        ],
        "details": {
            "Shade": "Berry",
            "Net wt": "3.5 g",
            "Finish": "Matte",
            "Cruelty-free": True
        }
    },

    {
        "name": "Nude Lipstick",
        "category": "cosmetics",
        "price": 599,
        "discount": 5,
        "image": "nude_lipstick.jpg",
        "description": "Classic nude lipstick for daily elegance.",
        "highlights": [
            "Neutral shade for everyday wear",
            "Hydrating formula",
            "Buildable coverage"
        ],
        "details": {
            "Shade": "Nude",
            "Net wt": "3.5 g",
            "Finish": "Satin",
            "Cruelty-free": True
        }
    },

    {
        "name": "Waterproof Kajal Black",
        "category": "cosmetics",
        "price": 199,
        "discount": 10,
        "image": "waterproof_kajal_black.jpg",
        "description": "Smudge-proof kajal with intense pigmentation.",
        "highlights": [
            "Jet black pigment",
            "Waterproof & long-lasting",
            "Precision tip for lining"
        ],
        "details": {
            "Type": "Kajal",
            "Waterproof": True,
            "Net wt": "1.5 g",
            "Safe for eyes": True
        }
    },

    {
        "name": "Sandalwood Cream 50g",
        "category": "cosmetics",
        "price": 299,
        "discount": 8,
        "image": "sandalwood_face_cream_50g.jpg",
        "description": "Hydrating sandalwood cream for daily glow.",
        "highlights": [
            "Natural sandalwood extracts",
            "Non-greasy daily moisturizer",
            "Gentle scent"
        ],
        "details": {
            "Net wt": "50 g",
            "Skin type": "All",
            "Paraben-free": True
        }
    },

    {
        "name": "Compact Powder",
        "category": "cosmetics",
        "price": 349,
        "discount": 5,
        "image": "compact_powder.jpg",
        "description": "Light matte compact for quick touch-ups.",
        "highlights": [
            "Matte finish",
            "Lightweight & buildable",
            "Travel-friendly compact"
        ],
        "details": {
            "Type": "Compact powder",
            "Net wt": "10 g",
            "Finish": "Matte",
            "Skin type": "All"
        }
    },

    {
        "name": "Eyeshadow Palette Warm",
        "category": "cosmetics",
        "price": 899,
        "discount": 12,
        "image": "eyeshadow_palette_warm.jpg",
        "description": "7-shade warm eyeshadow palette for day-night looks.",
        "highlights": [
            "Mix of mattes and shimmers",
            "Highly pigmented shades",
            "Blendable formula"
        ],
        "details": {
            "Shades": 7,
            "Net wt": "14 g",
            "Finish": "Matte & shimmer",
            "Cruelty-free": True
        }
    },

    {
        "name": "Blush Stick",
        "category": "cosmetics",
        "price": 399,
        "discount": 7,
        "image": "blush_stick.jpg",
        "description": "Cream-to-powder blush stick for a natural flush.",
        "highlights": [
            "Creamy texture that sets to powder",
            "Easy-to-blend",
            "Natural finish"
        ],
        "details": {
            "Type": "Blush stick",
            "Net wt": "8 g",
            "Finish": "Natural",
            "Skin type": "All"
        }
    },

    {
        "name": "Makeup Brush Set",
        "category": "cosmetics",
        "price": 799,
        "discount": 10,
        "image": "makeup_brush_set.jpg",
        "description": "Essential brush set for face and eyes.",
        "highlights": [
            "Set includes face & eye brushes",
            "Soft synthetic bristles",
            "Travel pouch included"
        ],
        "details": {
            "Pieces": 7,
            "Bristle": "Synthetic",
            "Care": "Hand wash bristles",
            "Cruelty-free": True
        }
    },

    {
        "name": "Face Primer",
        "category": "cosmetics",
        "price": 499,
        "discount": 10,
        "image": "face_primer.jpg",
        "description": "Smoothing primer to prep skin for makeup.",
        "highlights": [
            "Smooths pores and fine lines",
            "Creates long-lasting base",
            "Lightweight, non-greasy"
        ],
        "details": {
            "Type": "Primer",
            "Net wt": "30 ml",
            "Skin type": "All",
            "Paraben-free": True
        }
    },

    {
        "name": "Lip Gloss Sheer",
        "category": "cosmetics",
        "price": 299,
        "discount": 5,
        "image": "lip_gloss_sheer.jpg",
        "description": "Sheer glossy finish for everyday shine.",
        "highlights": [
            "Non-sticky glossy finish",
            "Subtle tint for natural shine",
            "Hydrating formula"
        ],
        "details": {
            "Type": "Lip gloss",
            "Net wt": "8 ml",
            "Finish": "Sheer gloss",
            "Cruelty-free": True
        }
    },
]
# (I did not rewrite your long product list here — keep as is.)

# ---------------------------------------------------------
# Enhance each product
# ---------------------------------------------------------
enhanced_products = []
for p in products:
    p = add_multi_images(p)
    p = add_missing_variants(p)

    p["created_at"] = datetime.datetime.utcnow()

    enhanced_products.append(p)

# ---------------------------------------------------------
# INSERT INTO MONGO
# ---------------------------------------------------------
products_col.insert_many(enhanced_products)

print("✔ All products inserted successfully!")
print("✔ Added image2, image3, sizes[], colors[] where missing.")
print("\n🎉 Seeding Completed!\n")
