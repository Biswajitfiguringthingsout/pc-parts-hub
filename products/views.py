from django.shortcuts import render, get_object_or_404
from .models import Product,Brand,Build,BuildItem
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.db.models import Sum
def product_list(request):
    products = Product.objects.all()
    brands = Brand.objects.all()
    
    query = request.GET.get('q', '').strip()

    if query:
        products = products.filter(name__icontains=query)

    brand_id = request.GET.get('brand')

    if brand_id:
        products = products.filter(brand_id=brand_id)

    sort = request.GET.get('sort', '')

    if sort == 'price_low':
        products = products.order_by('price')

    elif sort == 'price_high':
        products = products.order_by('-price')

    elif sort == 'name_asc':
        products = products.order_by('name')

    elif sort == 'name_desc':
        products = products.order_by('-name')
        
    paginator = Paginator(products, 10)

    page_number = request.GET.get('page')

    products = paginator.get_page(page_number)
    query = request.GET.get('q', '').strip()
    
    return render(
        request,
        'products/product_list.html',
        {
            'products': products,
            'brands': brands,
            'query': query,
            'sort': sort,
            'brand_id': brand_id,
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
    brands = Brand.objects.all()

    query = request.GET.get('q', '').strip()

    if query:
        products = products.filter(name__icontains=query)

    brand_id = request.GET.get('brand')

    if brand_id:
        products = products.filter(brand_id=brand_id)

    sort = request.GET.get('sort', '')

    if sort == 'price_low':
        products = products.order_by('price')

    elif sort == 'price_high':
        products = products.order_by('-price')

    elif sort == 'name_asc':
        products = products.order_by('name')

    elif sort == 'name_desc':
        products = products.order_by('-name')

    return render(
        request,
        'products/product_list.html',
        {
            'products': products,
            'brands': brands,
            'query': query,
            'sort': sort,
            'brand_id': brand_id,
            'category': category,
        }
    )


def home(request):
    featured_products = Product.objects.all()[:4]

    return render(
        request,
        'products/home.html',
        {
            'featured_products': featured_products
        }
    )
def build_page(request):

    build = Build.objects.first()

    items = BuildItem.objects.filter(build=build)

    total_price = items.aggregate(
    total=Sum('product__price'))['total'] or 0

    return render(
        request,
        'products/build_page.html',
        {
            'build': build,
            'items': items,
            'total_price': total_price,
        }
    )
def add_to_build(request, product_id):

    build = Build.objects.first()
    
    product = get_object_or_404(
        Product,
        id=product_id
    )

    BuildItem.objects.create(
        build=build,
        product=product
    )

    return redirect('build_page')    