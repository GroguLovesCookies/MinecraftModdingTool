import json


def armor_trim_filter(x):
    return "armor_trim" in x

def smithing_template_filter(x):
    return x.endswith("_smithing_template")

def spawn_egg_filter(x):
    return x.endswith("_spawn_egg")

def tools_filter(x):
    return x.endswith("pickaxe") or x.endswith("axe") or x.endswith("shovel") or x.endswith("hoe") or x.endswith("sword")

def armor_filter(x):
    return x.endswith("boots") or x.endswith("leggings") or x.endswith("chestplate") or x.endswith("helmet")

def music_disc_filter(x):
    return x.startswith("music_disc_")

def pottery_sherd_filter(x):
    return x.endswith("_pottery_sherd")

def boats_filter(x):
    return x.endswith("_boat")

def minecarts_filter(x):
    return x.endswith("_minecart")

def buckets_filter(x):
    return x.endswith("_bucket")

def favourites_filter(x):
    FAVOURITES = []
    with open("favourites.json", "r") as f:
        FAVOURITES = json.loads(f.read())["data"]
    return x in FAVOURITES