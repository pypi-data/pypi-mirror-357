from .utils import engine,python

from dataclasses import dataclass, field
from typing import Any,Optional
import os

import pygame

loaders = {
    "images":lambda path:pygame.image.load(path).convert_alpha(),
    "music": lambda path:path, # pygame.music loads only the last music file
    "sfx":lambda path:pygame.mixer.Sound(path),
    "fonts": lambda path: {size: pygame.font.Font(path, size) for size in
        {1, 2, 4, 8, 10, 12, 14, 16, 18, 24, 32, 48, 64, 72, 96, 128, 144, 192, 256}},
    "scenes": lambda path: python.load_class(path,python.get_filename(path).title().replace(" ", "_")),
    "scripts": lambda path: python.load_class(path,python.get_filename(path).title().replace(" ", "_"))
}
"""@private The loaders dictionary"""

@dataclass
class Data:
    """The Data structure"""
    files: dict[str, dict[str, str]] = field(default_factory=dict)
    images: dict[str, Any] = field(default_factory=dict)
    fonts: dict[str, Any] = field(default_factory=dict)
    scenes: dict[str, Any] = field(default_factory=dict)
    scripts: dict[str, Any] = field(default_factory=dict)
    music: dict[str, Any] = field(default_factory=dict)
    sfx: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f"<Loaded Data | "
            f"images: {len(self.images)}, "
            f"fonts: {len(self.fonts)}, "
            f"scenes: {len(self.scenes)}, "
            f"scripts: {len(self.scripts)}, "
            f"music: {len(self.music)}, "
            f"sfx: {len(self.sfx)}>"
        )

class Assets:
    data = Data()
    """@private The game data"""
    engine = Data()
    """@private The Engine data"""

    @classmethod
    def init(
        cls,
        path_images: str = None,path_fonts: str = None,
        path_scenes: str = None,path_scripts: str = None,
        path_music: str = None,path_sfx: str = None,
        pre_load: bool = True
    ) -> None:
        """
        Initialize the Assets system by loading asset files into the Data structure.

        Args:
            path_images (str, optional): Path to image files.
            path_fonts (str, optional): Path to font files.
            path_scenes (str, optional): Path to scene files.
            path_scripts (str, optional): Path to script files.
            path_music (str, optional): Path to song files.
            path_sfx (str, optional): Path to sound effect files.
            pre_load (bool): Whether to preload the assets immediately. Defaults to True.
        """
        cls._load_engine_files()
        cls.load("engine") # always load the engine data
        cls.engine.fonts.update(cls.__get_default_font()) # add default font to engine

        cls._load_data_files(
            path_images,path_fonts,
            path_scenes,path_scripts,
            path_music,path_sfx
        )
        pre_load and cls.load("data")

    @classmethod
    def get(cls,source: str, *loc) -> Any:
        """
        Safely retrieve a nested value from a source dictionary.

        Args:
            source (str): The data name to retrieve data from.
            *loc (str): A sequence of keys representing the path to the desired value.

        Returns:
            Any: The value at the specified nested location, or None if the path is invalid.

        Example:
            Assets.get("data"images", "player")  # Returns the player Surface if it exists
            Assets.get("engine,"images", "icon")  # Returns the engine icon Surface
        """

        # return None if no location is provided
        # as having direct access to a dynamic attribute sounds scary lol
        if not loc:
            return None

        source = getattr(cls, source)
        target = loc[0]

        data = getattr(source, target, None)
        if data is None:
            return None

        for key in loc[1:]:
            if not isinstance(data, dict):
                return None
            data = data.get(key)

        return data

    @classmethod
    def load(cls, source: "str") -> None:
        """
        Load file paths into the data system

        Args:
            source (str): The data name to retrieve data from.
        """

        data = getattr(cls, source)
        for category, loader in loaders.items():
            file_dict = data.files.get(category)
            if not file_dict:
                continue

            asset_store = getattr(data, category)
            for name, path in file_dict.items():
                asset_store[name] = loader(path)

    @classmethod
    def _load_data_files(cls,
        path_images: str,path_fonts: str ,
        path_scenes: str,path_scripts: str,
        path_music: str,path_sfx: str) -> None:
        """
        This method scans each provided directory path and organizes the discovered files
        into a structured dictionary (e.g., `Data.files`).

        Args:
            path_images (str): Path to image files.
            path_fonts (str): Path to font files.
            path_scenes (str): Path to scene files.
            path_scripts (str): Path to script files.
            path_music (str): Path to music files.
            path_sfx (str): Path to sound effect files.
        """


        paths = {}
        if path_images is not None:
            paths["images"] = cls.__get_full_path(path_images)

        if path_fonts is not None:
            paths["fonts"] = cls.__get_full_path(path_fonts)

        if path_music is not None:
            paths["music"] = cls.__get_full_path(path_music)

        if path_sfx is not None:
            paths["sfx"] = cls.__get_full_path(path_sfx)

        if path_scenes is not None:
            paths["scenes"] = cls.__get_full_path(path_scenes)

        if path_scripts is not None:
            paths["scripts"] = cls.__get_full_path(path_scripts)

        cls.data.files = cls.__get_all_files(paths)

    @classmethod
    def _load_engine_files(cls) -> None:
        """Same as _load_data_files but for engine assets."""
        base = os.path.dirname(__file__)
        path_images = os.path.normpath(os.path.join(base,"data","images"))
        paths = {
            "images": path_images,
            # More in the Future?
            # Like basic build-in scripts to speed up development
        }

        cls.engine.files = cls.__get_all_files(paths)

    @staticmethod
    def __get_default_font() -> dict[str, dict[int, pygame.font.Font]]:
        """
        Loads the default system font in a variety of common sizes.

        Returns:
            dict[str, dict[int, pygame.font.Font]]:
                A dictionary mapping the default font name to another dictionary
                that maps font sizes to `pygame.font.Font` objects.
        """
        name = pygame.font.get_default_font().split(".")[0]
        sizes = {
            size: pygame.font.SysFont(name, size) for size in
            {1, 2, 4, 8, 10, 12, 14, 16, 18, 24, 32, 48, 64, 72, 96, 128, 144, 192, 256}
        }
        return {name: sizes}

    @staticmethod
    def __get_all_files(path,ignore=None) -> dict[str, dict[str, str]]:
        """
        Recursively scan provided directories and build a nested dictionary of file paths.

        Args:
            path (dict[str, str]): A dictionary where each key is an asset type
                                (like "images" or "fonts") and the value is the path to its folder.
            ignore (set[str], optional): A set of folder names to exclude from scanning.
                                        "__pycache__" is always ignored.

        Returns:
            dict[str, dict[str, str]]: A nested dictionary structured like:
                {
                    "images": {
                        "player": "/path/to/images/player.png",
                        "enemy": "/path/to/images/enemy.png"
                    },
                    "fonts": {
                        "main": "/path/to/fonts/arial.ttf"
                    },
                    ...
                }
        """
        if not ignore:
            ignore = set()

        ignore.update({"__pycache__"})

        data = {}
        for key,value in path.items():
            for root, dirs, files in os.walk(value,topdown=False):
                ftype = os.path.basename(root)
                if ftype in ignore: continue
                data[key] = {}
                for file in files:
                    full_path = os.path.join(root, file)
                    name,_ = os.path.splitext(os.path.basename(full_path))
                    data[key][name] = full_path

        return data

    @staticmethod
    def __get_full_path(path):
        """
        Convert a relative path to an absolute normalized path and verify it exists.

        Args:
            path (str): The relative or partial path to validate.

        Returns:
            str: The normalized absolute path.

        Raises:
            OSError: If the resolved path does not exist.
        """
        path = os.path.normpath(os.getcwd()+path)
        if not os.path.exists(path):
            engine.error(OSError(f"The path doesn't exist: {path}"))
            engine.quit()
        return path
