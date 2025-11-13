from .models import Category
from django.db.utils import OperationalError # <-- NEW IMPORT

def categories_processor(request):
    """
    Makes all categories available in the context of every request.
    
    Includes try/except to gracefully handle OperationalError (no such table)
    caused by ephemeral SQLite databases in production environments like Render.
    """
    try: # <-- ADDED TRY BLOCK
        return {
            'all_categories': Category.objects.all()
        }
    except OperationalError: # <-- ADDED EXCEPTION HANDLING
        # This occurs if the database file is not present or has been reset.
        # Return an empty list to allow the template to render without crashing.
        return {
            'all_categories': []
        }