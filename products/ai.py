def analyze_build(installed):
    score = 0
    strengths = []
    suggestions = []

    cpu = installed.get("cpu")
    gpu = installed.get("gpu")
    ram = installed.get("ram")
    storage = installed.get("storage")

    # CPU
    if cpu:
        score += cpu.gaming_score // 2

    # GPU
    if gpu:
        score += gpu.gaming_score // 2

    # RAM
    if ram:
        score += 10

    # Storage
    if storage:
        score += 10

    score = min(score, 100)

    if score >= 90:
        rating = "Excellent Gaming Build"

    elif score >= 75:
        rating = "High Performance"

    elif score >= 60:
        rating = "Balanced Build"

    else:
        rating = "Entry Level Build"

    return {
        "score": score,
        "rating": rating,
        "strengths": strengths,
        "suggestions": suggestions,
    }