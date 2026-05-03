from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import CartItem, Category, Product


def catalog_view(request):
    products = Product.objects.select_related("category").all()
    categories = Category.objects.all().order_by("name")

    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    sort = request.GET.get("sort", "-release_year")

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


def cart_view(request):
    cart_items = []
    total_price = 0

    if request.user.is_authenticated:
        cart_items = (
            CartItem.objects.select_related("product")
            .filter(cart__user=request.user)
            .order_by("id")
        )
        total_price = sum(item.get_cost() for item in cart_items)

    return render(
        request,
        "main/cart.html",
        {"cart_items": cart_items, "total_price": total_price},
    )


def login_view(request):
    return render(request, "main/login.html")


def register_view(request):
    return render(request, "main/register.html")


def profile_view(request):
    return render(request, "main/profile.html")
