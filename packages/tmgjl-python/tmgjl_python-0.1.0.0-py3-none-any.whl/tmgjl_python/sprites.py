from os import listdir
from typing import TYPE_CHECKING, Protocol

from pygame.image import load
from pygame.time import get_ticks

if TYPE_CHECKING:
    from typing import Dict, List, Tuple

    from pygame import Surface


class DrawableEntity(Protocol):
    x: int | float
    y: int | float
    anim_name: str
    idx: int
    anim_tree: Dict[str, List[Surface]]


def load_static_sprite(path: str) -> Surface:
    return load(path)


def load_animated_sprite_frames(path: str) -> List[Surface]:
    return [load(path + "/" + file) for file in listdir(path)]


def load_animation_tree_frames(
    path: str, anim_names: List[str] | Tuple[str]
) -> Dict[str, List[Surface]]:
    return {an: load_animated_sprite_frames(path + "/" + an) for an in anim_names}


def load_animated_sprite_sheet(path: str) -> Surface:
    return load(path)


def load_animation_tree_sheet(
    path: str, path_names: List[str], anim_names: List[str] | Tuple[str]
) -> Dict[str, List[Surface]]:
    assert len(path_names) == len(anim_names)
    return {
        path_names[an]: load_animated_sprite_sheet(path + "/" + anim_names[an])
        for an in range(len(anim_names))
    }


def animate(
    idx: int, anim_list_length: int, anim_time: int, prev_anim_time: int
) -> int:
    if get_ticks() - prev_anim_time >= anim_time:
        (idx + 1) % anim_list_length
    return idx


def draw_frame_tree(
    anim_tree: Dict[str, List[Surface]],
    anim_name: str,
    idx: int,
    x: int | float,
    y: int | float,
    window: Surface,
) -> None:
    window.blit(anim_tree[anim_name][idx], (x, y))


def draw_frame_entity(entity: DrawableEntity, window: Surface) -> None:
    window.blit(entity.anim_tree[entity.anim_name][entity.idx], (entity.x, entity.y))
