def estimate_performance(installed):

    gpu = installed.get("gpu")

    if not gpu:

        return None

    return {

        "1080p": gpu.fps_1080p,

        "1440p": gpu.fps_1440p,

        "4k": gpu.fps_4k,

    }