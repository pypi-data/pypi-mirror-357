from .render_info import FPS

FOOD = {
    "carrot": 2,
    "mushroom": 1,
    "mushroom stew": 6,
    "rabbit meat": 1,
    "roasted mushroom": 3,
    "roasted rabbit meat": 4,
}
FLOOR = (
    "dirt",
    "ice",
    "mushroom door",
    "mushroom door open",
    "mushroom floor",
    "void",
    "wood door",
    "wood door open",
    "wood floor",
)
FLOOR_TYPE = {
    "dirt": "soil",
    "ice": "block",
    "mushroom door": "door",
    "mushroom door open": "open",
    "void": "block",
    "wood door": "door",
    "wood door open": "open"
}
FLOOR_UNBREAK = (
    "void",
)
GROW_CHANCE = {
    "carrot": 160 * FPS,
    "rabbit child": 200 * FPS,
    "sapling": 80 * FPS,
    "spore": 120 * FPS,
    "treeling": 160 * FPS,
}
GROW_TILES = {
    "carrot": ("carroot", {"carrot": 2}),
    "rabbit child": ("rabbit adult", {"rabbit fur": 1, "rabbit meat": 2}),
    "sapling": ("treeling", {"sapling": 1, "wood": 2}),
    "spore": ("mushroom", {"mushroom": 1, "spore": 2}),
    "treeling": ("tree", {"sapling": 2, "wood": 4}),
}
MULTI_TILES = {
    "big rock": (2, 2),
    "manual press": (2, 1),
    "mushroom hut": (5, 4),
    "obelisk": (1, 2),
    "sawbench": (2, 1),
    "wooden bed": (1, 2),
}
PROCESSING_TIME = {
    "bonsai pot": 40 * FPS,
    "composter": 2 * FPS,
}
ROOMS = {
    "mushroom hut": (
        ("mushroom block", (0, 0), (5, 4), "mushroom floor"),
        (None, (3, 3), (1, 1), "mushroom door"),
        ("mushroom shaper", (1, 1), (1, 1), "mushroom floor"),
    ),
}
STORAGE = {
    "small barrel": (1, 512),
    "small crate": (9, 48),
}
UNBREAK = (
    "glass lock",
    "left",
    "obelisk",
    "rabbit hole",
    "up",
    "wooden door",
)