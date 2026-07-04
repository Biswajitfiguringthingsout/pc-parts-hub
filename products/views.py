from django.shortcuts import render, get_object_or_404
from .models import Product,Brand,Build,BuildItem
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.db.models import Sum
from .recommendation_engine import (
    get_installed_components,
    get_next_category,
    get_candidate_products,
)
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

    installed = get_installed_components(build)

    next_category = get_next_category(installed)

    recommended_products = get_candidate_products(
    installed,
    next_category)
    
    total_price = sum(
    item.product.price
    for item in items
    )
    slots = {
        "CPU": items.filter(product__category="cpu").first(),
        "Motherboard": items.filter(product__category="motherboard").first(),
        "GPU": items.filter(product__category="gpu").first(),
        "RAM": items.filter(product__category="ram").first(),
        "Storage": items.filter(product__category="storage").first(),
        "PSU": items.filter(product__category="psu").first(),
        "Case": items.filter(product__category="case").first(),
        "Cooler": items.filter(product__category="cooler").first(),
        "Monitor": items.filter(product__category="monitor").first(),
        "Keyboard": items.filter(product__category="keyboard").first(),
        "Mouse": items.filter(product__category="mouse").first(),
        "Headset": items.filter(product__category="headset").first(),
    }

    compatibility_messages = []

    cpu = slots["CPU"]
    motherboard = slots["Motherboard"]
    ram = slots["RAM"]
    gpu = slots["GPU"]
    psu = slots["PSU"]
    case = slots["Case"]
    cooler = slots["Cooler"]
    storage = slots["Storage"]
        # ==================================
    # GPU ↔ Case Compatibility
    # ==================================

    if gpu and case:

        if (
            gpu.product.gpu_length
            and case.product.max_gpu_length
        ):

            if gpu.product.gpu_length <= case.product.max_gpu_length:

                compatibility_messages.append(
                    (
                        "success",
                        "GPU fits inside the selected case."
                    )
                )

            else:

                compatibility_messages.append(
                    (
                        "error",
                        "GPU is too long for the selected case."
                    )
                )

    # ==================================
    # Cooler ↔ Case Compatibility
    # ==================================

    if cooler and case:

        if (
            cooler.product.cooler_height
            and case.product.max_cooler_height
        ):

            if cooler.product.cooler_height <= case.product.max_cooler_height:

                compatibility_messages.append(
                    (
                        "success",
                        "CPU Cooler fits inside the selected case."
                    )
                )

            else:

                compatibility_messages.append(
                    (
                        "error",
                        "CPU Cooler is too tall for the selected case."
                    )
                )

    # ==========================================
    # CPU ↔ Motherboard
    # ==========================================

    if cpu and motherboard:

        if cpu.product.socket == motherboard.product.socket:

            compatibility_messages.append(
                ("success", "CPU and Motherboard are compatible.")
            )

        else:

            compatibility_messages.append(
                ("error", "CPU socket is incompatible with the selected Motherboard.")
            )

    # ==========================================
    # RAM ↔ Motherboard
    # ==========================================

    if ram and motherboard:

        if ram.product.memory_type == motherboard.product.memory_type:

            compatibility_messages.append(
                ("success", "RAM is compatible with the Motherboard.")
            )

        else:

            compatibility_messages.append(
                ("error", "RAM type is incompatible with the selected Motherboard.")
            )

    # ==========================================
    # Motherboard ↔ Case
    # ==========================================

    if motherboard and case:

        supported = [
            factor.strip().lower()
            for factor in (case.product.supported_form_factors or "").split(",")
        ]

        motherboard_form_factor = (
            motherboard.product.form_factor or ""
        ).lower()

        if motherboard_form_factor in supported:

            compatibility_messages.append(
                (
                    "success",
                    "Motherboard fits inside the selected case."
                )
            )

        else:

            compatibility_messages.append(
                (
                    "error",
                    "Selected motherboard is not supported by this case."
                )
            )

    # ==================================
    # Storage Slot Validation
    # ==================================

    if motherboard:

        m2_installed = items.filter(
            product__category="storage",
            product__storage_interface="M.2"
        ).count()

        sata_installed = items.filter(
            product__category="storage",
            product__storage_interface="SATA"
        ).count()

        if m2_installed <= (motherboard.product.m2_slots or 0):

            compatibility_messages.append(
                (
                    "success",
                    "Enough M.2 slots available."
                )
            )

        else:

            compatibility_messages.append(
                (
                    "error",
                    "Too many M.2 SSDs for the selected motherboard."
                )
            )

        if sata_installed <= (motherboard.product.sata_ports or 0):

            compatibility_messages.append(
                (
                    "success",
                    "Enough SATA ports available."
                )
            )

        else:

            compatibility_messages.append(
                (
                    "error",
                    "Too many SATA drives for the selected motherboard."
                )
            )

    # ==========================================
    # Total Power Draw
    # ==========================================

    total_power = sum(
        item.product.power_draw or 0
        for item in items
    )

    # ==========================================
    # Recommended PSU
    # ==========================================

    recommended_psu = int(total_power * 1.3)

    psu_sizes = [450, 550, 650, 750, 850, 1000, 1200]

    for size in psu_sizes:

        if recommended_psu <= size:

            recommended_psu = size
            break

    # ==========================================
    # PSU Compatibility
    # ==========================================

    if psu:

        psu_rating = psu.product.recommended_psu or 0

        if psu_rating >= recommended_psu:

            compatibility_messages.append(
                (
                    "success",
                    "Selected PSU provides enough power."
                )
            )

        else:

            compatibility_messages.append(
                (
                    "error",
                    f"Selected PSU ({psu_rating}W) is too weak. Recommended: {recommended_psu}W."
                )
            )

    # ==========================================
    # Build Statistics
    # ==========================================

    component_count = items.count()

    estimated_monthly_power_cost = round(
        (total_power * 4 * 30 / 1000) * 8
    )

    return render(
        request,
        "products/build_page.html",
        {
            "build": build,
            "slots": slots,
            "total_price": total_price,
            "component_count": component_count,
            "estimated_monthly_power_cost": estimated_monthly_power_cost,
            "compatibility_messages": compatibility_messages,
            "total_power": total_power,
            "recommended_psu": recommended_psu,
            "next_category": next_category,
            "recommended_products": recommended_products,
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