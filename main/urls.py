from django.urls import path

from . import views

urlpatterns = [
    # Каталог и товары
    path("", views.catalog_view, name="catalog"),
    path("product/<int:product_id>/", views.product_detail_view, name="product_detail"),

    # Корзина
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.cart_add_view, name="cart_add"),
    path("cart/update/<int:item_id>/", views.cart_update_view, name="cart_update"),
    path("cart/remove/<int:item_id>/", views.cart_remove_view, name="cart_remove"),

    # Оформление заказа
    path("checkout/", views.checkout_view, name="checkout"),
    path("payment/", views.payment_view, name="payment"),

    # Авторизация
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),

    # Личный кабинет
    path("profile/", views.profile_view, name="profile"),
]
