def analyze_build(installed):
    score = 0

    strengths = []
    warnings = []
    suggestions = []

    cpu = installed.get("cpu")
    gpu = installed.get("gpu")
    ram = installed.get("ram")
    storage = installed.get("storage")
    psu = installed.get("psu")

    # ----------------------------------
    # CPU
    # ----------------------------------

    if cpu:
        score += cpu.gaming_score // 2

        if cpu.gaming_score >= 90:
            strengths.append("Excellent gaming processor.")

        elif cpu.gaming_score >= 75:
            strengths.append("Strong gaming processor.")

        else:
            warnings.append("CPU performance is below modern high-end standards.")
            suggestions.append("Consider upgrading to a faster CPU.")

    else:
        suggestions.append("No CPU installed.")

    # ----------------------------------
    # GPU
    # ----------------------------------

    if gpu:
        score += gpu.gaming_score // 2

        if gpu.gaming_score >= 90:
            strengths.append("Excellent graphics card.")

        elif gpu.gaming_score >= 75:
            strengths.append("Strong graphics performance.")

        else:
            warnings.append("GPU performance may limit gaming.")
            suggestions.append("Upgrade to a more powerful graphics card.")

    else:
        suggestions.append("No GPU installed.")

    # ----------------------------------
    # CPU ↔ GPU Balance
    # ----------------------------------

    if cpu and gpu:

        difference = abs(cpu.gaming_score - gpu.gaming_score)

        if difference <= 10:
            strengths.append("CPU and GPU are perfectly balanced.")

        elif cpu.gaming_score > gpu.gaming_score + 20:
            warnings.append("Your graphics card may bottleneck the CPU.")
            suggestions.append("Upgrade the GPU for better gaming performance.")

        elif gpu.gaming_score > cpu.gaming_score + 20:
            warnings.append("The CPU may bottleneck the graphics card.")
            suggestions.append("Upgrade the CPU to fully utilize the GPU.")

    # ----------------------------------
    # RAM
    # ----------------------------------

    if ram:
        score += 10
        strengths.append("Memory installed.")

        if ram.capacity == "16GB":
            warnings.append("16GB RAM is sufficient today but 32GB is recommended for future games.")
            suggestions.append("Upgrade to 32GB RAM for better multitasking.")

    else:
        suggestions.append("Install system memory.")

    # ----------------------------------
    # Storage
    # ----------------------------------

    if storage:
        score += 10
        strengths.append("Storage installed.")

        if storage.capacity == "512GB":
            warnings.append("512GB storage may fill up quickly.")
            suggestions.append("Consider adding another SSD.")

    else:
        suggestions.append("Add a storage drive.")

    # ----------------------------------
    # PSU
    # ----------------------------------

    if psu:
        strengths.append("Reliable power supply installed.")

    else:
        suggestions.append("Install a power supply.")

    # ----------------------------------
    # Final Score
    # ----------------------------------

    score = min(score, 100)

    # ----------------------------------
    # Rating
    # ----------------------------------

    if score >= 90:
        rating = "Excellent Gaming Build"

    elif score >= 75:
        rating = "High Performance"

    elif score >= 60:
        rating = "Balanced Build"

    else:
        rating = "Entry Level Build"

    # ----------------------------------
    # AI Summary
    # ----------------------------------

    if score >= 90:
        summary = (
            "This build is excellent for modern AAA gaming and should provide outstanding performance for years."
        )

    elif score >= 75:
        summary = (
            "A strong gaming PC with only minor upgrade opportunities."
        )

    elif score >= 60:
        summary = (
            "A balanced PC that performs well but still has room for improvement."
        )

    else:
        summary = (
            "This build works but several upgrades are recommended for modern gaming."
        )

    return {
        "score": score,
        "rating": rating,
        "summary": summary,
        "strengths": strengths,
        "warnings": warnings,
        "suggestions": suggestions,
    }