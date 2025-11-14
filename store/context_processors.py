# store/context_processors.py

# A simple Mock object class to mimic Django's Category model behavior
class MockCategory:
    """Mock object to satisfy template access to cat.name and cat.slug."""
    def __init__(self, name, slug):
        self.name = name
        self.slug = slug

# Hardcoded category data derived from STATIC_PRODUCTS_DATA in views.py
STATIC_CATEGORIES = [
    MockCategory('Clothing', 'clothing'),
    MockCategory('Accessories', 'accessories'),
    MockCategory('Footwear', 'footwear'),
]

def categories_processor(request):
    """
    Returns a list of hardcoded MockCategory objects to populate the navigation menu,
    thereby avoiding the OperationalError that occurs when querying the ephemeral database.
    """
    return {
        'all_categories': STATIC_CATEGORIES
    }