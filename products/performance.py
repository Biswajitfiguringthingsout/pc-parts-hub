from .benchmark import get_game_benchmarks


def estimate_performance(installed):

    cpu = installed.get("cpu")
    gpu = installed.get("gpu")

    if not cpu or not gpu:

        return {
            "fps_1080p": "-",
            "fps_1440p": "-",
            "fps_4k": "-",
            "games": {},
            "cpu_bottleneck": 0,
            "gpu_bottleneck": 0,
            "performance_tier": "-",
            "summary": "Install both CPU and GPU to estimate gaming performance."
        }

    cpu_score = cpu.gaming_score
    gpu_score = gpu.gaming_score

    benchmarks = get_game_benchmarks(gpu.name)
    
    # ---------------------------------------
    # Bottleneck Detection
    # ---------------------------------------

    cpu_bottleneck = 0
    gpu_bottleneck = 0

    difference = cpu_score - gpu_score

    if difference >= 15:
        gpu_bottleneck = min(difference, 30)

    elif difference <= -15:
        cpu_bottleneck = min(abs(difference), 30)

    # ---------------------------------------
    # Resolution Scaling
    # ---------------------------------------

    cpu_scale = cpu_score / 100
    gpu_scale = gpu_score / 100

    scale1080 = cpu_scale * 0.65 + gpu_scale * 0.35
    scale1440 = cpu_scale * 0.45 + gpu_scale * 0.55
    scale4k = cpu_scale * 0.20 + gpu_scale * 0.80

    estimated_games = {}

    total1080 = 0
    total1440 = 0
    total4k = 0

    game_count = 0

    for game, fps in benchmarks.items():

        game1080 = int(fps["1080p"] * scale1080)
        game1440 = int(fps["1440p"] * scale1440)
        game4k = int(fps["4k"] * scale4k)

        estimated_games[game] = {
            "1080p": game1080,
            "1440p": game1440,
            "4k": game4k,
        }

        total1080 += game1080
        total1440 += game1440
        total4k += game4k

        game_count += 1

    if game_count:

        fps1080 = total1080 // game_count
        fps1440 = total1440 // game_count
        fps4k = total4k // game_count

    else:

        fps1080 = "-"
        fps1440 = "-"
        fps4k = "-"

    # ---------------------------------------
    # Performance Tier
    # ---------------------------------------

    average_score = (cpu_score + gpu_score) / 2

    if average_score >= 95:
        tier = "Enthusiast"

    elif average_score >= 85:
        tier = "High-End"

    elif average_score >= 70:
        tier = "Mid Range"

    elif average_score >= 50:
        tier = "Budget"

    else:
        tier = "Entry Level"

    # ---------------------------------------
    # Summary
    # ---------------------------------------

    if cpu_bottleneck:

        summary = (
            f"CPU bottleneck detected (~{cpu_bottleneck}%). "
            "Higher refresh-rate gaming at 1080p will be limited by the processor."
        )

    elif gpu_bottleneck:

        summary = (
            f"GPU bottleneck detected (~{gpu_bottleneck}%). "
            "The processor is capable of driving a faster graphics card."
        )

    else:

        summary = (
            "Excellent CPU and GPU balance. "
            "No significant bottleneck detected."
        )

    return {

        "fps_1080p": fps1080,
        "fps_1440p": fps1440,
        "fps_4k": fps4k,

        "games": estimated_games,

        "cpu_bottleneck": cpu_bottleneck,
        "gpu_bottleneck": gpu_bottleneck,

        "performance_tier": tier,

        "summary": summary,
    }