# add_categories.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_management.settings')
django.setup()

from inventory.models import Category

Category.objects.all().delete()

categories = [
    {'name': 'Electronics', 'description': 'Electronic devices and accessories including computers, phones, and gadgets'},
    {'name': 'Furniture', 'description': 'Home and office furniture including chairs, tables, and storage solutions'},
    {'name': 'Clothing', 'description': 'Apparel and fashion items for men, women, and children'},
    {'name': 'Food & Beverages', 'description': 'Food products, drinks, and culinary ingredients'},
    {'name': 'Office Supplies', 'description': 'Office stationery and supplies for business and personal use'},
    {'name': 'Tools & Hardware', 'description': 'Tools, equipment, and hardware for DIY and professional use'},
    {'name': 'Beauty & Personal Care', 'description': 'Beauty products, cosmetics, and personal care items'},
    {'name': 'Sports & Fitness', 'description': 'Sports equipment, fitness gear, and outdoor recreation items'},
    {'name': 'Books & Stationery', 'description': 'Books, notebooks, and stationery items for reading and writing'}
]

for category_data in categories:
    Category.objects.create(**category_data)

print(f"ok{len(categories)}ok.")