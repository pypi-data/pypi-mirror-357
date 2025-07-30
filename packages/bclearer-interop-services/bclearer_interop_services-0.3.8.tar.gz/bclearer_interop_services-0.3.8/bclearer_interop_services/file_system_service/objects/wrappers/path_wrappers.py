from pathlib import Path
from typing import Optional


class PathWrappers:

    def __init__(
        self,
        path_string: Optional[
            str | Path
        ],
    ):
        if not path_string:
            self.__path = None
        else:
            self.__path = Path(
                path_string
            )

    @property
    def base_name(self) -> str:
        return str(self.__path.name)

    @property
    def file_stem_name(self) -> str:
        return str(self.__path.stem)

    @property
    def level(self) -> int:
        return len(self.__path.parts)

    @property
    def path_string(self) -> str:
        return str(self.__path)

    @property
    def path(self) -> Path:
        return self.__path

    @property
    def parent(self):
        return self.__path.parent

    # TODO: make path_extension a list??
    def extend_path(
        self, path_extension: str
    ) -> Path:
        extended_path_string = (
            self.__path.joinpath(
                path_extension
            )
        )

        return extended_path_string

    def exists(self) -> bool:
        try:
            exists = (
                self.__path.exists()
            )

        except AttributeError:
            exists = False

        return exists

    def list_of_components(self):
        return self.__path.parts

    def item_count(self) -> int:
        item_count = len(
            self.__path.parts
        )

        return item_count
