# store/context_processors.py

# Remove: from .models import Category
# Remove: from django.db.utils import OperationalError 

def categories_processor(request):
    """
    Returns an empty list to prevent OperationalError on Render's free tier.
    """
    return {
        'all_categories': []
    }