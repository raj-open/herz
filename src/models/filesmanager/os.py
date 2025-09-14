#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from __future__ import annotations

import os
from datetime import datetime
from datetime import timezone
from pathlib import Path

from pydantic import AwareDatetime

from ...models.apis import *
from .traits import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "OSFilesManager",
    "OSFilesManagerFile",
    "OSFilesManagerFolder",
]

# ----------------------------------------------------------------
# CLASSES
# ----------------------------------------------------------------


class OSFilesManager:
    """
    File system for a local operating system
    """

    _timezone: timezone

    def __init__(self, tz: timezone):
        self._timezone = tz
        return

    @staticmethod
    def path_split(path: str) -> tuple[str, str, str]:
        path = path.strip().rstrip(r"\/")
        filename = os.path.basename(path)
        path = os.path.dirname(path) or "."
        basename, ext = os.path.splitext(filename)
        return path, basename, ext

    @staticmethod
    def path_join(*path: str) -> str:
        """
        Static method to combine parts of path
        """
        return os.path.join(*path) or "."

    def get_file(self, *path: str) -> OSFilesManagerFile:
        tz = self._timezone
        path_full = os.path.join(*path) or "."
        path_full = path_full.strip().rstrip(r"\/")
        return OSFilesManagerFile(path=path_full, tz=tz)

    def get_folder(self, *path: str) -> OSFilesManagerFolder:
        tz = self._timezone
        path_full = os.path.join(*path) or "."
        path_full = path_full.strip().rstrip(r"\/")
        return OSFilesManagerFolder(manager=self, path=path_full, tz=tz)

    def create_folder(self, path: str) -> OSFilesManagerFolder:
        """
        Use files manager to create folder by full path.
        First checks if folder already exists.
        """
        path = path.strip().rstrip(r"\/")
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        return self.get_folder(path)

    def create_file(self, path: str, contents: bytes) -> OSFilesManagerFile:
        """
        Use files manager to create file by full path
        """
        path, basename, ext = OSFilesManager.path_split(path)
        filename = f"{basename}{ext}"
        # first ensure folder exists
        folder = self.create_folder(path)
        # next create file within folder
        file = folder.write_bytes(name=filename, contents=contents)
        return file


class OSFilesManagerFile:
    """
    File manager for a local operating system
    """

    _path: str
    _timezone: timezone
    _object: Path

    def __init__(self, path: str, tz: timezone):
        assert path != "", "Path cannot be empty!"
        self._path = path
        self._timezone = tz
        return

    @staticmethod
    def path_split(path: str) -> tuple[str, str, str]:
        return OSFilesManager.path_split(path)

    @property
    def exists(self) -> bool | None:
        """
        Whether or not the file exists (unknown -> `None`)
        """
        try:
            return os.path.exists(self.path)
        except Exception:
            return None

    @property
    def path(self) -> str:
        return self._path

    @property
    def directory(self) -> str:
        """
        Gets basepath of file
        """
        return os.path.dirname(self._path)

    @property
    def filename(self) -> str:
        """
        Gets basename of file (including extension)
        """
        return os.path.basename(self._path)

    @property
    def basename(self) -> str:
        """
        Gets basename of file (including extension)
        """
        basename, _ = os.path.splitext(self.filename)
        return basename

    @property
    def ext(self) -> str:
        """
        Gets file extension
        """
        _, ext = os.path.splitext(self._path)
        return ext

    @property
    def size(self) -> int:
        meta = os.stat(self._path)
        return meta.st_size

    @property
    def date_created(self) -> AwareDatetime | None:
        meta = os.stat(self._path)
        return datetime.fromtimestamp(meta.st_ctime, tz=self._timezone)

    @property
    def date_modified(self) -> AwareDatetime | None:
        meta = os.stat(self._path)
        return datetime.fromtimestamp(meta.st_mtime, tz=self._timezone)

    def get_meta_data(self) -> MetaData:
        """
        Gets bundled meta data associated to file.
        """
        return MetaData(
            path=self.path,
            filename=self.filename,
            basename=self.basename,
            ext=self.ext,
            size=self.size,
            time_created=self.date_created,
            time_updated=self.date_modified,
        )

    def read_as_bytes(self) -> bytes:
        """
        Downloads file contents as bytes
        """
        with open(self._path, "rb") as fp:
            contents = fp.read()
            return contents

    def delete_self(self) -> bool:
        """
        Deletes current file
        """
        if not self.exists:
            return True
        try:
            os.remove(self._path)
            ex = self.exists
            return False if ex is None else not ex

        except Exception:
            return False


class OSFilesManagerFolder:
    """
    Folder manager for a local operating system
    """

    _manager: OSFilesManager
    _path: str
    _timezone: timezone
    _filenames: list[str] | None

    def __init__(self, manager: OSFilesManager, path: str, tz: timezone):
        assert path != "", "Path cannot be empty!"
        self._manager = manager
        self._path = path
        self._timezone = tz
        self._filenames = None
        return

    @property
    def exists(self) -> bool | None:
        """
        Whether or not the folder exists (unknown -> `None`)
        """
        try:
            return os.path.exists(self.path)
        except Exception:
            return None

    @property
    def path(self) -> str:
        return self._path

    @property
    def name(self) -> str:
        return os.path.basename(self._path)

    @property
    def subfolders(self) -> list[OSFilesManagerFolder]:
        tz = self._timezone
        names = os.listdir(self._path)
        paths = [os.path.join(self._path, name) for name in names]
        paths = [path for path in paths if Path(path).is_dir()]
        return [OSFilesManagerFolder(manager=self._manager, path=path, tz=tz) for path in paths]

    def get_subfolder(self, name: str) -> OSFilesManagerFolder:
        return self._manager.get_folder(os.path.join(self._path, name))

    @property
    def files(self) -> list[OSFilesManagerFile]:
        tz = self._timezone
        names = os.listdir(self._path)
        paths = [os.path.join(self._path, name) for name in names]
        paths = [path for path in paths if Path(path).is_file()]
        return [OSFilesManagerFile(path=path, tz=tz) for path in paths]

    @property
    def filenames(self) -> list[str]:
        names = os.listdir(self._path)
        paths = [os.path.join(self.path, name) for name in names]
        self._filenames = [name for name, path in zip(names, paths) if Path(path).is_file()]
        return self._filenames

    def has_file(self, file: OSFilesManagerFile) -> bool:
        return file.filename in self.filenames

    def get_file(self, name: str) -> OSFilesManagerFile:
        return self._manager.get_file(os.path.join(self._path, name))

    def get_files_meta_data(self, as_basename: bool) -> dict[str, MetaData]:
        """
        Gets a dictionary of metadata associated to files
        with keys = basename or filenames,
        values = metadata
        """
        if as_basename:
            return {file.basename: file.get_meta_data() for file in self.files}
        else:
            return {file.filename: file.get_meta_data() for file in self.files}

    def write_bytes(self, name: str, contents: bytes) -> OSFilesManagerFile:
        path = os.path.join(self._path, name)
        with open(path, "wb") as fp:
            fp.write(contents)

        return OSFilesManagerFile(
            path=path,
            tz=self._timezone,
        )

    def add_subfolder(self, name: str) -> OSFilesManagerFolder:
        """
        Adds subfolder and returns a manager for it.
        If subfolder already exists, it will not be created.
        """
        path = os.path.join(self._path, name)
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        return OSFilesManagerFolder(
            manager=self._manager,
            path=path,
            tz=self._timezone,
        )

    def clear_folder(self) -> bool:
        """
        Removes all contents of current folder
        """
        success = True
        for file in self.files:
            success = success and file.delete_self()
        for subfolder in self.subfolders:
            success = success and subfolder.delete_self()
        return success

    def delete_self(self) -> bool:
        """
        Deletes current folder
        """
        if not self.exists:
            return True
        success = self.clear_folder()
        if not success:
            return False
        if not self.exists:
            return True
        os.rmdir(self._path)
        ex = self.exists
        not_ex = False if ex is None else not ex
        return success and not_ex
