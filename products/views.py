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

    total_price = sum(
        item.product.price
        for item in items
    )

    slots = {
        "CPU": items.filter(product__category="cpu").first(),
        "Motherboard": items.filter(product__category="motherboard").first(),
        "GPU": items.filter(product__category="gpu").first(),

        "RAM": items.filter(product__category="ram"),
        "Storage": items.filter(product__category="storage"),

        "PSU": items.filter(product__category="psu").first(),
        "Case": items.filter(product__category="case").first(),
        "Cooler": items.filter(product__category="cooler").first(),
        "PSU": items.filter(product__category="psu").first(),


        "Monitor": items.filter(product__category="monitor"),
        "Keyboard": items.filter(product__category="keyboard"),
        "Mouse": items.filter(product__category="mouse"),
    }
    compatibility_messages = []

    cpu = slots["CPU"]
    motherboard = slots["Motherboard"]

    ram_queryset = slots["RAM"]
    ram = ram_queryset.first()

    gpu = slots["GPU"]

    # CPU ↔ Motherboard compatibility
    if cpu and motherboard:

        if cpu.product.socket == motherboard.product.socket:

            compatibility_messages.append(
                ("success", "CPU and Motherboard are compatible.")
            )

        else:

            compatibility_messages.append(
                ("error", "CPU socket is incompatible with the selected Motherboard.")
            )

    # RAM ↔ Motherboard compatibility
    if ram and motherboard:

        if ram.product.memory_type == motherboard.product.memory_type:

            compatibility_messages.append(
                ("success", "RAM is compatible with the Motherboard.")
            )

        else:

            compatibility_messages.append(
                ("error", "RAM type is incompatible with the selected Motherboard.")
            )

    # Total Power Draw
    total_power = sum(
        item.product.power_draw or 0
        for item in items
    )

    # Recommended PSU
    recommended_psu = int(total_power * 1.3)
    

    psu_sizes = [450, 550, 650, 750, 850, 1000, 1200]

    for size in psu_sizes:
        if recommended_psu <= size:
            recommended_psu = size
            break
    return render(
        request,
        "products/build_page.html",
       {
            "build": build,
            "slots": slots,
            "total_price": total_price,

            "compatibility_messages": compatibility_messages,
            "total_power": total_power,
            "recommended_psu": recommended_psu,
        },
    )
def add_to_build(request, product_id):

    build = Build.objects.first()

    product = get_object_or_404(
        Product,
        id=product_id
    )

    single_component_categories = [
        'cpu',
        'gpu',
        'motherboard',
        'case',
        'psu',
        'cooler'
    ]

    if product.category.lower() in single_component_categories:

        existing_item = BuildItem.objects.filter(
            build=build,
            product__category=product.category
        ).first()

        if existing_item:
            existing_item.delete()

    BuildItem.objects.create(
        build=build,
        product=product
    )

    return redirect('build_page') 

def remove_build_item(request, item_id):

    item = get_object_or_404(
        BuildItem,
        id=item_id
    )

    item.delete()

    return redirect('build_page')