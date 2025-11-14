# store/context_processors.py

# Remove: from .models import Category
# Remove: from django.db.utils import OperationalError 

def categories_processor(request):
    """
    Makes a placeholder empty list for categories available globally.
    Database access is completely removed to prevent OperationalError on Render's free tier.
    """
    # Simply return an empty list. This stops the database lookup.
    return {
        'all_categories': []
    }