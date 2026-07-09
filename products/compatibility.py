from .models import BuildItem


def check_compatibility(build):
    items = BuildItem.objects.filter(build=build)

    slots = {
        "CPU": items.filter(product__category="cpu").first(),
        "Motherboard": items.filter(product__category="motherboard").first(),
        "GPU": items.filter(product__category="gpu").first(),
        "RAM": items.filter(product__category="ram").first(),
        "Storage": items.filter(product__category="storage").first(),
        "PSU": items.filter(product__category="psu").first(),
        "Case": items.filter(product__category="case").first(),
        "Cooler": items.filter(product__category="cooler").first(),
    }

    cpu = slots["CPU"]
    motherboard = slots["Motherboard"]
    gpu = slots["GPU"]
    ram = slots["RAM"]
    storage = slots["Storage"]
    psu = slots["PSU"]
    case = slots["Case"]
    cooler = slots["Cooler"]

    compatibility_messages = []

    # ===============================
    # GPU ↔ CASE
    # ===============================

    if gpu and case:
        if gpu.product.gpu_length and case.product.max_gpu_length:

            if gpu.product.gpu_length <= case.product.max_gpu_length:
                compatibility_messages.append(
                    ("success", "GPU fits inside the selected case.")
                )
            else:
                compatibility_messages.append(
                    ("error", "GPU is too long for the selected case.")
                )

    # ===============================
    # COOLER ↔ CASE
    # ===============================

    if cooler and case:
        if cooler.product.cooler_height and case.product.max_cooler_height:

            if cooler.product.cooler_height <= case.product.max_cooler_height:
                compatibility_messages.append(
                    ("success", "CPU Cooler fits inside the selected case.")
                )
            else:
                compatibility_messages.append(
                    ("error", "CPU Cooler is too tall for the selected case.")
                )

    # ===============================
    # CPU ↔ Motherboard
    # ===============================

    if cpu and motherboard:

        if cpu.product.socket == motherboard.product.socket:
            compatibility_messages.append(
                ("success", "CPU and Motherboard are compatible.")
            )
        else:
            compatibility_messages.append(
                ("error", "CPU socket is incompatible with the selected Motherboard.")
            )

    # ===============================
    # RAM ↔ Motherboard
    # ===============================

    if ram and motherboard:

        if ram.product.memory_type == motherboard.product.memory_type:
            compatibility_messages.append(
                ("success", "RAM is compatible with the Motherboard.")
            )
        else:
            compatibility_messages.append(
                ("error", "RAM type is incompatible with the selected Motherboard.")
            )

    # ===============================
    # Motherboard ↔ Case
    # ===============================

    if motherboard and case:

        supported = [
            f.strip().lower()
            for f in (case.product.supported_form_factors or "").split(",")
        ]

        motherboard_ff = (motherboard.product.form_factor or "").lower()

        if motherboard_ff in supported:

            compatibility_messages.append(
                ("success", "Motherboard fits inside the selected case.")
            )

        else:

            compatibility_messages.append(
                ("error", "Motherboard is not supported by the selected case.")
            )

    # ===============================
    # Storage Slots
    # ===============================

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
                ("success", "Enough M.2 slots available.")
            )

        else:

            compatibility_messages.append(
                ("error", "Too many M.2 SSDs for this motherboard.")
            )

        if sata_installed <= (motherboard.product.sata_ports or 0):

            compatibility_messages.append(
                ("success", "Enough SATA ports available.")
            )

        else:

            compatibility_messages.append(
                ("error", "Too many SATA drives for this motherboard.")
            )

    # ===============================
    # POWER DRAW
    # ===============================

    total_power = sum(
        item.product.power_draw or 0
        for item in items
    )

    recommended_psu = int(total_power * 1.3)

    psu_sizes = [450, 550, 650, 750, 850, 1000, 1200]

    for size in psu_sizes:
        if recommended_psu <= size:
            recommended_psu = size
            break

    # ===============================
    # PSU Check
    # ===============================

    if psu:

        psu_rating = psu.product.recommended_psu or 0

        if psu_rating >= recommended_psu:

            compatibility_messages.append(
                ("success", "Selected PSU provides enough power.")
            )

        else:

            compatibility_messages.append(
                (
                    "error",
                    f"Selected PSU ({psu_rating}W) is too weak. Recommended: {recommended_psu}W."
                )
            )

    return {
        "messages": compatibility_messages,
        "total_power": total_power,
        "recommended_psu": recommended_psu,
    }