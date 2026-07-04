from .models import BuildItem
from .models import Product

BUILD_ORDER = [
    "case",
    "motherboard",
    "cpu",
    "cooler",
    "ram",
    "storage",
    "gpu",
    "psu",
]


def get_installed_components(build):
    """Returns installed components as a dictionary.

    Example:
    {
        "cpu": cpu_product,
        "gpu": gpu_product,
        ...
    }
    """

    installed = {}

    items = BuildItem.objects.filter(build=build)

    for item in items:
        installed[item.product.category] = item.product

    return installed


def get_next_category(installed):
    """Returns the next component the user should install based on
    the recommended PC building order.
    """

    for category in BUILD_ORDER:
        if category not in installed:
            return category

    # Everything has been installed
    return None


def get_candidate_products(installed, next_category):
    products = Product.objects.filter(category=next_category)

    cpu = installed.get("cpu")
    motherboard = installed.get("motherboard")
    ram = installed.get("ram")

    if next_category == "motherboard" and cpu:
        products = products.filter(socket=cpu.socket)

    if next_category == "cpu" and motherboard:
        products = products.filter(socket=motherboard.socket)

    if next_category == "ram" and motherboard:
        products = products.filter(memory_type=motherboard.memory_type)

    recommendations = []

    for product in products:
        score = 0
        reason = []

        # -------------------
        # Release Year
        # -------------------
        if product.release_year:
            score += product.release_year

            if product.release_year >= 2024:
                reason.append("Newest generation")
            elif product.release_year >= 2022:
                reason.append("Modern platform")

        # -------------------
        # Gaming
        # -------------------
        if product.gaming_score:
            score += product.gaming_score * 2

            if product.gaming_score >= 90:
                reason.append("Elite gaming")
            elif product.gaming_score >= 75:
                reason.append("Excellent gaming")
            elif product.gaming_score >= 60:
                reason.append("Great gaming")

        # -------------------
        # Productivity
        # -------------------
        if product.productivity_score:
            score += product.productivity_score

            if product.productivity_score >= 80:
                reason.append("Excellent productivity")
            elif product.productivity_score >= 60:
                reason.append("Good productivity")

        # -------------------
        # Value Bonus
        # -------------------
        if product.price:
            if product.price < 10000:
                score += 25
                reason.append("Budget Friendly")
            elif product.price < 20000:
                score += 15
                reason.append("Great Value")

        recommendations.append(
            {
                "product": product,
                "score": score,
                "reason": ", ".join(reason),
            }
        )

    recommendations.sort(key=lambda x: x["score"], reverse=True)

    return recommendations[:5]

