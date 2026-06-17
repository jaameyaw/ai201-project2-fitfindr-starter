# tests/test_tools.py

from tools import search_listings, suggest_outfit, create_fit_card

def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_empty_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []   # empty list, no exception

def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=40)
    assert all(item["price"] <= 40 for item in results)

def test_suggest_outfit_happy_path():
    new_item = {
        "title": "Vintage Graphic Tee",
        "description": "A cool faded vintage graphic tee",
        "category": "tops"
    }
    wardrobe = {
        "items": [
            {
                "id": "w_001",
                "name": "Baggy straight-leg jeans, dark wash",
                "category": "bottoms",
                "colors": ["dark blue", "indigo"]
            }
        ]
    }
    suggestion = suggest_outfit(new_item, wardrobe)
    assert isinstance(suggestion, str)
    assert len(suggestion) > 0

def test_suggest_outfit_empty_wardrobe():
    new_item = {
        "title": "Vintage Graphic Tee",
        "description": "A cool faded vintage graphic tee",
        "category": "tops"
    }
    wardrobe = {"items": []}
    suggestion = suggest_outfit(new_item, wardrobe)
    assert isinstance(suggestion, str)
    assert len(suggestion) > 0

def test_create_fit_card_happy_path():
    outfit = "Pair the vintage graphic tee with baggy jeans."
    new_item = {
        "title": "Vintage Graphic Tee",
        "price": 25.0,
        "platform": "depop"
    }
    card = create_fit_card(outfit, new_item)
    assert isinstance(card, str)
    assert len(card) > 0
    assert "Error" not in card

def test_create_fit_card_empty_outfit():
    outfit = "   "
    new_item = {
        "title": "Vintage Graphic Tee",
        "price": 25.0,
        "platform": "depop"
    }
    card = create_fit_card(outfit, new_item)
    assert card == "Error: Cannot generate fit card because outfit data is missing."
