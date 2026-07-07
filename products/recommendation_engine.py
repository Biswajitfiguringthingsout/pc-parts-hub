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
    installed = {}

    items = BuildItem.objects.filter(build=build)

    for item in items:
        installed[item.product.category] = item.product

    return installed


def get_next_category(installed):

    for category in BUILD_ORDER:
        if category not in installed:
            return category

    return None


def get_candidate_products(installed, next_category):

    products = Product.objects.filter(category=next_category)

    cpu = installed.get("cpu")
    motherboard = installed.get("motherboard")
    ram = installed.get("ram")
    gpu = installed.get("gpu")

    # ----------------------------------------------------
    # Compatibility Filtering
    # ----------------------------------------------------

    if next_category == "motherboard" and cpu:
        products = products.filter(socket=cpu.socket)

    if next_category == "cpu" and motherboard:
        products = products.filter(socket=motherboard.socket)

    if next_category == "ram" and motherboard:
        products = products.filter(
            memory_type=motherboard.memory_type
        )

    recommendations = []

    for product in products:

        score = 0
        reasons = []
        badge = "Recommended"

        # ----------------------------------------------------
        # Gaming Performance
        # ----------------------------------------------------

        score += product.gaming_score * 3

        if product.gaming_score >= 90:
            reasons.append("Excellent gaming")
            badge = "Gaming Beast"

        elif product.gaming_score >= 75:
            reasons.append("Strong gaming")
            badge = "Great Gaming"

        elif product.gaming_score >= 60:
            reasons.append("Good gaming")

        # ----------------------------------------------------
        # Productivity
        # ----------------------------------------------------

        score += product.productivity_score * 2

        if product.productivity_score >= 85:
            reasons.append("Excellent productivity")

        elif product.productivity_score >= 70:
            reasons.append("Great productivity")

        # ----------------------------------------------------
        # Efficiency
        # ----------------------------------------------------

        score += product.efficiency_score

        if product.efficiency_score >= 85:
            reasons.append("Power efficient")

        # ----------------------------------------------------
        # Release Year
        # ----------------------------------------------------

        if product.release_year:

            score += max(product.release_year - 2020, 0) * 5

            if product.release_year >= 2024:
                reasons.append("Latest generation")

            elif product.release_year >= 2022:
                reasons.append("Modern platform")

        # ----------------------------------------------------
        # Tier Bonus
        # ----------------------------------------------------

        tier_bonus = {
            "Entry": 5,
            "Budget": 10,
            "Mid Range": 20,
            "High End": 35,
            "Flagship": 45,
        }

        score += tier_bonus.get(product.tier, 0)

        # ----------------------------------------------------
        # Value Bonus
        # ----------------------------------------------------

        if product.price:

            if product.price < 10000:
                score += 30
                reasons.append("Excellent value")

                if badge == "Recommended":
                    badge = "Best Value"

            elif product.price < 20000:
                score += 20
                reasons.append("Great value")

                if badge == "Recommended":
                    badge = "Budget Pick"

            elif product.price < 40000:
                score += 10

        # ----------------------------------------------------
        # CPU <-> GPU Balance
        # ----------------------------------------------------

        if next_category == "gpu" and cpu:

            difference = abs(
                cpu.gaming_score - product.gaming_score
            )

            if difference <= 10:
                score += 25
                reasons.append("Perfect CPU pairing")

            elif difference <= 20:
                score += 15
                reasons.append("Balanced with your CPU")

        if next_category == "cpu" and gpu:

            difference = abs(
                gpu.gaming_score - product.gaming_score
            )

            if difference <= 10:
                score += 25
                reasons.append("Perfect GPU pairing")

            elif difference <= 20:
                score += 15
                reasons.append("Balanced with your GPU")

        # ----------------------------------------------------
        # Remove duplicate reasons
        # ----------------------------------------------------

        reasons = list(dict.fromkeys(reasons))

        recommendations.append(
        {
            "product": product,
            "score": score,
            "reasons": reasons,
            "badge": badge,
        }
        )

    recommendations.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    return recommendations[:5]