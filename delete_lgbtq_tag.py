import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from apps.users.models import ConstraintTag

tag_name = "LGBTQ+ Friendly"

try:
    tag = ConstraintTag.objects.get(name=tag_name)
    print(f"Found tag: {tag.get_category_display()}: {tag.name}")
    print(f"Used by {tag.users.count()} user profiles")
    
    # Delete the tag
    tag.delete()
    print(f"✅ Successfully deleted '{tag_name}' from database")
    
    # Show remaining tags in values category
    remaining = ConstraintTag.objects.filter(category='values').count()
    print(f"Total value tags remaining: {remaining}")
except ConstraintTag.DoesNotExist:
    print(f"❌ Tag '{tag_name}' not found")
