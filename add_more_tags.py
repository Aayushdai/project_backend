import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from apps.users.models import ConstraintTag

print("Adding more constraint tags...\n")

# Comprehensive constraint tags
constraint_data = [
    # DIET
    ('Vegetarian', 'diet', 'No meat, fish, or poultry'),
    ('Vegan', 'diet', 'No animal products at all'),
    ('Non-vegetarian', 'diet', 'Eats meat and fish'),
    ('Halal', 'diet', 'Follows Islamic dietary laws'),
    ('Kosher', 'diet', 'Follows Jewish dietary laws'),
    ('Gluten-free', 'diet', 'Cannot eat gluten-containing foods'),
    ('Pescatarian', 'diet', 'Eats fish but not meat'),
    ('Dairy-free', 'diet', 'Avoids dairy products'),
    
    # LIFESTYLE
    ('Non-smoker', 'lifestyle', 'Does not smoke'),
    ('Smoker', 'lifestyle', 'Smokes cigarettes'),
    ('Early Riser', 'lifestyle', 'Prefers early mornings'),
    ('Night Owl', 'lifestyle', 'Prefers late nights'),
    ('Fitness Focused', 'lifestyle', 'Regular exercise and fitness'),
    ('Drinks Alcohol', 'lifestyle', 'Consumes alcoholic beverages'),
    ('Non-drinker', 'lifestyle', 'Does not drink alcohol'),
    ('Party Person', 'lifestyle', 'Enjoys nightlife and social gatherings'),
    ('Quiet & Homebody', 'lifestyle', 'Prefers calm, indoor activities'),
    
    # VALUES & PREFERENCES
    ('Religious/Spiritual', 'values', 'Strong religious or spiritual beliefs'),
    ('Eco-conscious', 'values', 'Environmentally aware and sustainable'),
    ('Budget Conscious', 'values', 'Prioritizes saving money'),
    ('Luxury Lover', 'values', 'Prefers high-end experiences'),
    ('Minimalist', 'values', 'Prefers simple, clutter-free lifestyle'),
    ('Adventure Seeker', 'values', 'Loves extreme sports and risks'),
    ('Child-friendly', 'values', 'Comfortable traveling with children'),
    ('Quiet Traveler', 'values', 'Prefers peaceful environments'),
    ('Social Butterfly', 'values', 'Loves meeting people and socializing'),
    ('Introvert', 'values', 'Prefers small groups and quiet time'),
    ('Extrovert', 'values', 'Energized by social interactions'),
    
    # AGE RANGE (already exist but including for completeness)
    ('18-25', 'age_range', 'Young adult'),
    ('25-35', 'age_range', 'Early career'),
    ('35-50', 'age_range', 'Mid-career'),
    ('50+', 'age_range', 'Mature travelers'),
    
    # GENDER PREFERENCES
    ('Women Only', 'gender', 'Prefer female travel companions'),
    ('Men Only', 'gender', 'Prefer male travel companions'),
    ('Mixed Group', 'gender', 'Comfortable with any gender'),
    
    # RELATIONSHIP STATUS
    ('Single', 'status', 'Currently single'),
    ('Partnered', 'status', 'In a relationship'),
    ('Solo Traveler', 'status', 'Traveling alone'),
]

created_count = 0
for name, category, description in constraint_data:
    obj, created = ConstraintTag.objects.get_or_create(
        name=name,
        category=category,
        defaults={'description': description}
    )
    if created:
        created_count += 1
        print(f'✓ Added: {category.upper()} - {name}')

total_tags = ConstraintTag.objects.count()
print(f"\n✅ Complete!")
print(f'  • New tags added: {created_count}')
print(f'  • Total constraint tags: {total_tags}')

# Group by category
print(f"\nTags by Category:")
for category in ['diet', 'lifestyle', 'values', 'age_range', 'gender', 'status']:
    count = ConstraintTag.objects.filter(category=category).count()
    print(f'  • {category.replace("_", " ").title()}: {count}')
