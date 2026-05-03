from django.urls import path

from . import views

urlpatterns = [
    path("", views.catalog_view, name="catalog"),
    path("catalog/", views.catalog_view, name="catalog_alt"),
    path("product/<int:product_id>/", views.product_detail_view, name="product_detail"),
    path("cart/", views.cart_view, name="cart"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("profile/", views.profile_view, name="profile"),
]
