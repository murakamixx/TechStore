from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, RegisterForm
from .models import Cart, CartItem, Category, Order, OrderItem, Product


# ─── Каталог ────────────────────────────────────────────────────────────────

def catalog_view(request):
    products = Product.objects.select_related("category").all()
    categories = Category.objects.all().order_by("name")

    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    sort = request.GET.get("sort", "newest")

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        )

    if category_slug:
        products = products.filter(category__slug=category_slug)

    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            min_price = ""

    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            max_price = ""

    sort_map = {
        "price_asc": "price",
        "price_desc": "-price",
        "name_asc": "name",
        "name_desc": "-name",
        "newest": "-release_year",
        "oldest": "release_year",
    }
    products = products.order_by(sort_map.get(sort, "-release_year"))

    context = {
        "products": products,
        "categories": categories,
        "filters": {
            "q": query,
            "category": category_slug,
            "min_price": min_price,
            "max_price": max_price,
            "sort": sort,
        },
    }
    return render(request, "main/catalog.html", context)


# ─── Карточка товара ─────────────────────────────────────────────────────────

def product_detail_view(request, product_id):
    product = get_object_or_404(Product.objects.select_related("category"), id=product_id)
    related_products = (
        Product.objects.filter(category=product.category)
        .exclude(id=product.id)
        .order_by("-release_year")[:4]
    )
    return render(
        request,
        "main/product_detail.html",
        {"product": product, "related_products": related_products},
    )


# Корзина

@login_required(login_url="login")
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related("product").order_by("id")
    total_price = cart.get_total_cost()
    return render(
        request,
        "main/cart.html",
        {"cart_items": cart_items, "total_price": total_price},
    )


@login_required(login_url="login")
def cart_add_view(request, product_id):
    """Добавить товар в корзину или увеличить количество."""
    if request.method != "POST":
        return redirect("catalog")

    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
        item.save()

    messages.success(request, f"«{product.name}» добавлен в корзину.")
    next_url = request.POST.get("next", "cart")
    return redirect(next_url)


@login_required(login_url="login")
def cart_update_view(request, item_id):
    """Изменить количество позиции в корзине."""
    if request.method != "POST":
        return redirect("cart")

    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    try:
        qty = int(request.POST.get("quantity", 1))
    except ValueError:
        qty = 1

    if qty < 1:
        item.delete()
    else:
        item.quantity = qty
        item.save()

    return redirect("cart")


@login_required(login_url="login")
def cart_remove_view(request, item_id):
    """Удалить позицию из корзины."""
    if request.method != "POST":
        return redirect("cart")

    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect("cart")


# ─── Оплата / оформление заказа ──────────────────────────────────────────────

@login_required(login_url="login")
def checkout_view(request):
    """Страница подтверждения и бутафорской оплаты."""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related("product").order_by("id")
    total_price = cart.get_total_cost()

    if not cart_items.exists():
        messages.warning(request, "Корзина пуста — нечего оплачивать.")
        return redirect("cart")

    return render(
        request,
        "main/checkout.html",
        {"cart_items": cart_items, "total_price": total_price},
    )


@login_required(login_url="login")
def payment_view(request):
    """Обработка бутафорской оплаты — создаём заказ и очищаем корзину."""
    if request.method != "POST":
        return redirect("checkout")

    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related("product").all()

    if not cart_items.exists():
        messages.warning(request, "Корзина пуста.")
        return redirect("cart")

    with transaction.atomic():
        order = Order.objects.create(
            user=request.user,
            status=Order.STATUS_PAID,
            total_price=cart.get_total_cost(),
        )
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                price=item.product.price,
                quantity=item.quantity,
            )
        cart_items.delete()

    messages.success(request, f"Заказ #{order.pk} успешно оплачен!")
    return redirect("profile")


# ─── Авторизация / регистрация ───────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect("catalog")

    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect(request.GET.get("next", "catalog"))

    return render(request, "main/login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("catalog")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Аккаунт создан. Добро пожаловать!")
        return redirect("catalog")

    return render(request, "main/register.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect("catalog")


# ─── Личный кабинет ──────────────────────────────────────────────────────────

@login_required(login_url="login")
def profile_view(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items__product")
    return render(request, "main/profile.html", {"orders": orders})
