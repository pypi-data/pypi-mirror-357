from ...tile_systems.world_generation import generate_chunk
from ...tile_systems.tile_class import Tile

def save_creating(state, chunks):
    state.save_file_name = ""
    state.menu_placement = "main_game"
    chunks = {}
    state.location["tile"] = [0, 0, 0, 2]
    state.location["real"] = [0, 0, 0, 2]
    state.noise_offset = generate_chunk(0, 0, chunks)
    for x in range(-4, 5):
        for y in range(-4, 5):
            generate_chunk(state.location["tile"][0] + x, state.location["tile"][1] + y, chunks, state.noise_offset)
    chunks[(0, 0)][(0, 0)] = Tile("obelisk")
    chunks[(0, 0)][(0, 1)] = Tile("up")
    chunks[(0, 0)][(0, 2)] = Tile("player", floor="void")
    state.tick = 0
    return chunks