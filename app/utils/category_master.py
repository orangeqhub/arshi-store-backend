# Arshi Naturals food categories — aligned with ARSHI-STORE frontend

CATEGORY_MASTER = [
    {"name": "Pickles", "icon": "🥭", "description": "Traditional Andhra pickles & homemade recipes", "accent": "#E8F5E9"},
    {"name": "Snacks", "icon": "🍘", "description": "Murukulu, Chekkalu & crispy delights", "accent": "#FFF3E0"},
    {"name": "Sweets", "icon": "🍬", "description": "Ariselu, Laddu, Sunnundalu & more", "accent": "#FCE4EC"},
    {"name": "Spice Powders", "icon": "🌶️", "description": "Idli podi, karam podi & masalas", "accent": "#FFEBEE"},
    {"name": "Combo Packs", "icon": "🎁", "description": "Family combos & festival specials", "accent": "#F3E5F5"},
    {"name": "Premium Collections", "icon": "🏺", "description": "Exclusive handcrafted products", "accent": "#FFF8E1"},
    {"name": "Best Sellers", "icon": "⭐", "description": "Customer favorite products", "accent": "#E8F5E9"},
    {"name": "New Arrivals", "icon": "🔥", "description": "Freshly launched products", "accent": "#FFF3E0"},
    {"name": "Organic Specials", "icon": "🌱", "description": "100% natural ingredients", "accent": "#E8F5E9"},
    {"name": "Festival Specials", "icon": "🎉", "description": "Seasonal festive collections", "accent": "#FCE4EC"},
    {"name": "Spicy Specials", "icon": "🌶️", "description": "Extra spicy pickle collections", "accent": "#FFEBEE"},
    {"name": "Garlic Delights", "icon": "🧄", "description": "Garlic-based pickles and specialties", "accent": "#F3E5F5"},
    {"name": "Lemon Collection", "icon": "🍋", "description": "Fresh lemon and citrus pickles", "accent": "#FFFDE7"},
    {"name": "Tomato Specials", "icon": "🍅", "description": "Tomato-based traditional pickles", "accent": "#FFEBEE"},
    {"name": "Gongura Favorites", "icon": "🌿", "description": "Authentic Andhra Gongura varieties", "accent": "#E8F5E9"},
]

CATEGORY_MASTER_BY_NAME = {
    item["name"].lower(): item for item in CATEGORY_MASTER
}


def get_category_meta(name: str | None) -> dict:
    if not name:
        return {"icon": "🌿", "description": None, "accent": "#E8F5E9"}
    return CATEGORY_MASTER_BY_NAME.get(
        name.lower(),
        {"icon": "🌿", "description": None, "accent": "#E8F5E9"},
    )
