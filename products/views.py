from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
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

    builds = Build.objects.all()

    build_id = request.GET.get("build")

    if build_id:
        build = get_object_or_404(Build, id=build_id)
    else:
        build = builds.first()

    items = BuildItem.objects.filter(build=build)
    cpus = Product.objects.filter(category="cpu")
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
    builds = Build.objects.all()
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
            "cpus": cpus,
            "builds": builds,
        },
    )


def add_to_build(request, product_id):

    build_id = request.GET.get("build")
    build = get_object_or_404(Build, id=build_id)

    if build_id:
        build = get_object_or_404(Build, id=build_id)
    else:
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

    return redirect(f"/products/build/?build={build.id}")


def remove_build_item(request, item_id):

    build_id = request.GET.get("build")

    item = get_object_or_404(BuildItem, id=item_id)
    item.delete()

    return redirect(f"/products/build/?build={build_id}")

def compare_gpus(request):

    gpu1_id = request.GET.get("gpu1")
    gpu2_id = request.GET.get("gpu2")

    gpu1 = Product.objects.get(id=gpu1_id)
    gpu2 = Product.objects.get(id=gpu2_id)

    gpu1_benchmarks = Benchmark.objects.filter(gpu=gpu1)
    gpu2_benchmarks = Benchmark.objects.filter(gpu=gpu2)
    gpu1_total_fps = 0
    gpu2_total_fps = 0
    benchmark_count = 0


    benchmarks = {}

    for bench1 in gpu1_benchmarks:

        bench2 = gpu2_benchmarks.filter(
            game=bench1.game,
            resolution=bench1.resolution
        ).first()
        if bench2:
            gpu1_total_fps += bench1.fps
            gpu2_total_fps += bench2.fps
            benchmark_count += 1

        if bench1.game not in benchmarks:
            benchmarks[bench1.game] = []

        benchmarks[bench1.game].append({

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
    avg_gpu1 = round(gpu1_total_fps / benchmark_count) if benchmark_count else 0
    avg_gpu2 = round(gpu2_total_fps / benchmark_count) if benchmark_count else 0

    overall_winner = gpu1.name if avg_gpu1 > avg_gpu2 else gpu2.name

    performance_difference = 0

    if avg_gpu1 and avg_gpu2:

        if avg_gpu1 > avg_gpu2:
            performance_difference = round(
                ((avg_gpu1 - avg_gpu2) / avg_gpu2) * 100
            )
        else:
            performance_difference = round(
                ((avg_gpu2 - avg_gpu1) / avg_gpu1) * 100
            )

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
        "average_fps": {
            "gpu1": avg_gpu1,
            "gpu2": avg_gpu2,
        },
        "overall_winner": overall_winner,
        "performance_difference": performance_difference,
    })
def compare_cpus(request):

    cpu1_id = request.GET.get("cpu1")
    cpu2_id = request.GET.get("cpu2")

    cpu1 = Product.objects.get(id=cpu1_id)
    cpu2 = Product.objects.get(id=cpu2_id)

    winner = {
    "price": (
        cpu1.name if cpu1.price < cpu2.price
        else cpu2.name if cpu2.price < cpu1.price
        else "Tie"
    ),

    "gaming_score": (
        cpu1.name if cpu1.gaming_score > cpu2.gaming_score
        else cpu2.name if cpu2.gaming_score > cpu1.gaming_score
        else "Tie"
    ),

    "productivity_score": (
        cpu1.name if cpu1.productivity_score > cpu2.productivity_score
        else cpu2.name if cpu2.productivity_score > cpu1.productivity_score
        else "Tie"
    ),

    "power_draw": (
        cpu1.name if cpu1.power_draw < cpu2.power_draw
        else cpu2.name if cpu2.power_draw < cpu1.power_draw
        else "Tie"
    ),

    "release_year": (
        cpu1.name if cpu1.release_year > cpu2.release_year
        else cpu2.name if cpu2.release_year > cpu1.release_year
        else "Tie"
    ),
    }

    return JsonResponse({

        "cpu1":{

            "name":cpu1.name,
            "price":float(cpu1.price),
            "gaming_score":cpu1.gaming_score,
            "productivity_score":cpu1.productivity_score,
            "power_draw":cpu1.power_draw,
            "release_year":cpu1.release_year,
            "tier":cpu1.tier,

        },

        "cpu2":{

            "name":cpu2.name,
            "price":float(cpu2.price),
            "gaming_score":cpu2.gaming_score,
            "productivity_score":cpu2.productivity_score,
            "power_draw":cpu2.power_draw,
            "release_year":cpu2.release_year,
            "tier":cpu2.tier,

        },

        "winner":winner,

    })
def compare_builds(request):

    build1 = get_object_or_404(Build, id=request.GET.get("build1"))
    build2 = get_object_or_404(Build, id=request.GET.get("build2"))

    stats1 = calculate_build_stats(build1)
    stats2 = calculate_build_stats(build2)

    

    build1_points = 0
    build2_points = 0

    if stats1["gaming"] > stats2["gaming"]:
        build1_points += 1
    else:
        build2_points += 1

    if stats1["productivity"] > stats2["productivity"]:
        build1_points += 1
    else:
        build2_points += 1

    if stats1["power"] < stats2["power"]:
        build1_points += 1
    else:
        build2_points += 1

    if stats1["price"] < stats2["price"]:
        build1_points += 1
    else:
        build2_points += 1

    overall = "Build A" if build1_points >= build2_points else "Build B"
    winner = {
    "gaming": build1.name if stats1["gaming"] > stats2["gaming"] else build2.name,
    "productivity": build1.name if stats1["productivity"] > stats2["productivity"] else build2.name,
    "power": build1.name if stats1["power"] < stats2["power"] else build2.name,
    "price": build1.name if stats1["price"] < stats2["price"] else build2.name,
}

    overall = build1.name if build1_points >= build2_points else build2.name
    return JsonResponse({
        "build1_name": build1.name,
        "build2_name": build2.name,
        "build1": stats1,
        "build2": stats2,
        "winner": winner,
        "overall": overall,
    })
    
def calculate_build_stats(build):
    items = BuildItem.objects.filter(build=build)

    stats = {
        "gaming": 0,
        "productivity": 0,
        "power": 0,
        "price": 0,
    }

    cpu = None
    gpu = None
    ram = None
    storage = None

    for item in items:
        product = item.product

        stats["power"] += product.power_draw or 0
        stats["price"] += float(product.price)

        if product.category == "cpu":
            cpu = product

        elif product.category == "gpu":
            gpu = product

        elif product.category == "ram":
            ram = product

        elif product.category == "storage":
            storage = product

    gaming = 0
    productivity = 0

    if cpu:
        gaming += cpu.gaming_score * 0.35
        productivity += cpu.productivity_score * 0.60

    if gpu:
        gaming += gpu.gaming_score * 0.55

    if ram:
        gaming += ram.gaming_score * 0.10
        productivity += ram.productivity_score * 0.20

    if storage:
        productivity += storage.productivity_score * 0.20

    stats["gaming"] = round(gaming)
    stats["productivity"] = round(productivity)

    return stats