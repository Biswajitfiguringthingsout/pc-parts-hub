from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.db.models import Sum
from django.http import JsonResponse

from .models import Product, Brand, Build, BuildItem, Benchmark
from .ai import analyze_build
from .performance import estimate_performance
from .compatibility import check_compatibility
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
            'featured_products': featured_products,
        },
    )


def build_page(request):

    build = Build.objects.first()

    items = BuildItem.objects.filter(build=build)

    installed = get_installed_components(build)
    build_analysis = analyze_build(installed)
    next_category = get_next_category(installed)
    performance = estimate_performance(installed)
    recommended_products = get_candidate_products(
        installed,
        next_category,
    )

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

    gpu_item = slots["GPU"]
    benchmarks = {}

    if gpu_item:
        benchmark_queryset = Benchmark.objects.filter(
            gpu=gpu_item.product
        )

        for benchmark in benchmark_queryset:
            if benchmark.game not in benchmarks:
                benchmarks[benchmark.game] = []

            benchmarks[benchmark.game].append(benchmark)

    # ==========================================
    # Compatibility Engine
    # ==========================================
    compatibility = check_compatibility(build)

    compatibility_messages = compatibility["messages"]
    total_power = compatibility["total_power"]
    recommended_psu = compatibility["recommended_psu"]

    # ==========================================
    # Build Statistics
    # ==========================================
    component_count = items.count()

    estimated_monthly_power_cost = round(
        (total_power * 4 * 30 / 1000) * 8
    )

    gpus = Product.objects.filter(category="gpu")

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
            "build_analysis": build_analysis,
            "performance": performance,
            "benchmarks": benchmarks,
            "gpus": gpus,
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
def compare_gpus(request):

    gpu1_id = request.GET.get("gpu1")
    gpu2_id = request.GET.get("gpu2")

    gpu1 = Product.objects.get(id=gpu1_id)
    gpu2 = Product.objects.get(id=gpu2_id)
    gpu1_benchmarks = Benchmark.objects.filter(gpu=gpu1)
    gpu2_benchmarks = Benchmark.objects.filter(gpu=gpu2)

    benchmarks = []

    for bench1 in gpu1_benchmarks:

        bench2 = gpu2_benchmarks.filter(game=bench1.game,resolution=bench1.resolution).first()

    benchmarks.append({

        "game": bench1.game,
        "resolution": bench1.resolution,
        "gpu1_fps": bench1.fps,
        "gpu2_fps": bench2.fps if bench2 else "-",

        "winner": (
            gpu1.name
            if not bench2 or bench1.fps > bench2.fps
            else gpu2.name
        )

    })
    winner = {
    "price": gpu1.name if gpu1.price < gpu2.price else gpu2.name,
    "gaming_score": gpu1.name if gpu1.gaming_score > gpu2.gaming_score else gpu2.name,
    "power_draw": gpu1.name if gpu1.power_draw < gpu2.power_draw else gpu2.name,
}

    return JsonResponse({

    "gpu1": {
        "name": gpu1.name,
        "price": float(gpu1.price),
        "gaming_score": gpu1.gaming_score,
        "power_draw": gpu1.power_draw,
    },

    "gpu2": {
        "name": gpu2.name,
        "price": float(gpu2.price),
        "gaming_score": gpu2.gaming_score,
        "power_draw": gpu2.power_draw,
    },

    "winner": winner,
    "benchmarks": benchmarks,

})