from django.shortcuts import render, get_object_or_404
from .models import Product


def product_list(request):
    products = Product.objects.all()

    query = request.GET.get('q', '').strip()

    if query:
        products = products.filter(name__icontains=query)

    return render(
        request,
        'products/product_list.html',
        {
            'products': products,
            'query': query,
        }
    )


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)

    return render(
        request,
        'products/product_detail.html',
        {'product': product}
    )


def products_by_category(request, category):
    products = Product.objects.filter(category=category)

    query = request.GET.get('q', '').strip()

    if query:
        products = products.filter(name__icontains=query)

    return render(
        request,
        'products/product_list.html',
        {
            'products': products,
            'query': query,
        }
    )