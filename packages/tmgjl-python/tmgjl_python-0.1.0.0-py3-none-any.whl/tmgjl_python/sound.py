from typing import TYPE_CHECKING

from pygame.mixer import Sound, init

if TYPE_CHECKING:
    from typing import Dict

init()
sound_dict: Dict[str, Sound] = {}
sound_folder: str | None = None


def add_sounds(**kwargs: str) -> None:
    for name, file in kwargs.items():
        sound_dict[name] = (
            Sound(sound_folder + "/" + file)
            if sound_folder is not None
            else Sound(file)
        )
