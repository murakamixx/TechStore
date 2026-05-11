from django.contrib import admin
from .models import Category, Product, Profile, Cart, CartItem, Review, Order, OrderItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'release_year', 'category', 'stock')
    list_filter = ('category', 'release_year') 
    search_fields = ('name', 'description')

admin.site.register(Category)
admin.site.register(Profile)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(OrderItem)