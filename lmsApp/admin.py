from django.contrib import admin

from .models import Books, Borrow, Category, Students, SubCategory



# Registering the models so they appear in the Django admin panel
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Books)
admin.site.register(Students)
admin.site.register(Borrow)

