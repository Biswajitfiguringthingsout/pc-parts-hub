GPU_BENCHMARKS = {

    "RTX 5060": {

        "Cyberpunk 2077": {
            "1080p": 118,
            "1440p":83,
            "4k":42,
        },

        "Black Myth Wukong": {
            "1080p":82,
            "1440p":57,
            "4k":30,
        },

        "Valorant":{
            "1080p":520,
            "1440p":480,
            "4k":420,
        },

        "CS2":{
            "1080p":380,
            "1440p":330,
            "4k":250,
        },

    },



    "RTX 5080":{

        "Cyberpunk 2077":{
            "1080p":225,
            "1440p":170,
            "4k":110,
        },

        "Black Myth Wukong":{
            "1080p":170,
            "1440p":130,
            "4k":82,
        },

        "Valorant":{
            "1080p":720,
            "1440p":680,
            "4k":610,
        },

    }

}
def get_game_benchmarks(gpu_name):

    gpu_name = gpu_name.lower()

    if "5060" in gpu_name:
        return GPU_BENCHMARKS["RTX 5060"]

    elif "5080" in gpu_name:
        return GPU_BENCHMARKS["RTX 5080"]

    return {}