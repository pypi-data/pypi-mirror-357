from .tile_class import Tile


def generate_room(material: str, location: tuple[int, int], size: tuple[int, int], floor: str = None):
    room = {}
    for x in range(location[0], location[0] + size[0]):
        for y in range(location[1], location[1] + size[1]):
            room[x, y] = Tile(material, floor = floor)
            room[x, y].attributes = (*room[x, y].attributes, "structure")
    for x in range(location[0] + 1, location[0] + size[0] - 1):
        for y in range(location[1] + 1, location[1] + size[1] - 1):
            room[x, y] = Tile(floor = floor)
    return room