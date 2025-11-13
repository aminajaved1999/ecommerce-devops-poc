from .models import Category

def categories_processor(request):
    """
    Makes all categories available in the context of every request.
    """
    return {
        'all_categories': Category.objects.all()
    }