from ..info import TILE_ATTRIBUTES, DAY_LENGTH, FLOOR_TYPE
from .left_click import recipe, place, storage, machine_storage, unlock
from ..tile_systems.tile_class import Tile

def left_click(
    machine_ui: str,
    grid_position: list[int, int],
    chunks,
    inventory_number: int,
    health: int,
    max_health: int,
    position,
    recipe_number: int,
    location: dict[str],
    inventory: dict[str, int],
    machine_inventory: dict[str, int],
    tick: int,
):
    if machine_ui == "game":
        is_not_tile = (grid_position[1] not in chunks[grid_position[0]])
        if is_not_tile:
            is_kind = True
        else:
            is_kind = isinstance(chunks[grid_position[0]][grid_position[1]].kind, str)
            current_tile = chunks[grid_position[0]][grid_position[1]]
        is_floor = not is_not_tile and not is_kind
        if is_floor and FLOOR_TYPE.get(current_tile.floor) == "door":
            chunks[grid_position[0]][grid_position[1]] = Tile(floor=current_tile.floor + " open", floor_health=current_tile.floor_health, floor_unbreak=current_tile.floor_unbreak)
        elif is_floor and FLOOR_TYPE.get(current_tile.floor) == "open":
            change_floor = current_tile.floor[:-5]
            chunks[grid_position[0]][grid_position[1]] = Tile(floor=change_floor, floor_health=current_tile.floor_health, floor_unbreak=current_tile.floor_unbreak)
        elif is_not_tile or not is_kind:
            chunks = place(inventory, inventory_number, is_not_tile, is_kind, health, max_health, grid_position, location, chunks)
        elif "open" in chunks[grid_position[0]][grid_position[1]].attributes:
            machine_ui = chunks[grid_position[0]][grid_position[1]].kind
            location["opened"] = (grid_position[0], grid_position[1])
            machine_inventory = chunks[grid_position[0]][grid_position[1]].inventory
        elif "sleep" in chunks[grid_position[0]][grid_position[1]].attributes:
            if 9 / 16 <= (tick / DAY_LENGTH) % 1 < 15 / 16:
                tick = (tick // DAY_LENGTH + 9 / 16) * DAY_LENGTH
        elif "lock" in chunks[grid_position[0]][grid_position[1]].attributes:
            chunks = unlock(inventory, inventory_number, chunks, grid_position)
    elif "machine" in TILE_ATTRIBUTES.get(machine_ui, ()):
        chunks = machine_storage(position, chunks, location, inventory, machine_ui)
    elif "store" in TILE_ATTRIBUTES.get(machine_ui, ()):
        chunks = storage(position, chunks, location, inventory, machine_ui)
    elif "craft" in TILE_ATTRIBUTES.get(machine_ui, ()):
        inventory = recipe(machine_ui, recipe_number, inventory)
    return machine_ui, chunks, location, machine_inventory, tick
