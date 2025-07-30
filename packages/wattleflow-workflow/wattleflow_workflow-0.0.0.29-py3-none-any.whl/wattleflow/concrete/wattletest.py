# Module Name: concrete/wattletest.py
# Description: This modul contains concrete unitttest classes.
# Author: (wattleflow@outlook.com)
# Copyright: (c) 2022-2024 WattleFlow
# License: Apache 2 Licence

import gc
import os
import re
import glob
import logging
import tempfile
from abc import ABC
from fnmatch import fnmatch
from os import path, makedirs, walk
from typing import Generator, Optional
from shutil import copy2, copytree, rmtree
from unittest import TestCase
from wattleflow.concrete.attribute import Attribute
from wattleflow.concrete.logger import AuditLogger
from wattleflow.helpers.system import CheckPath, ShellExecutor



TEST_NAME = "test_dir"
TEST_DIR = "{}{}wattleflow".format(tempfile.gettempdir(), os.path.sep)


class WattleflowTestClass(TestCase, Attribute, AuditLogger, ABC):
    # Used instead of __init__
    def setUp(
        self,
        level: int = logging.INFO,
        handler: Optional[logging.Handler] = None,
    ):
        self.cleanup: bool = True
        self._config_path: str = ""
        self._paths: dict = {}

        super().setUp()
        Attribute.__init__(self)
        AuditLogger.__init__(self, level=level, handler=handler)

        # self._config_path: str = ""
        # self._paths: str = {}
        # self.cleanup: bool = True

        self.set_path(TEST_NAME, TEST_DIR)
        for name, folder in self._paths.items():
            if not path.exists(folder):
                self.set_path(name=name, folder=folder)

    def find_by_pattern(self, directory, pattern) -> Generator[str, None, None]:
        for root, _, files in walk(directory):
            for file in files:
                # if glob.fnmatch.fnmatch(file, pattern):
                if fnmatch(file, pattern) or fnmatch(file, pattern.lower()):
                    yield path.join(root, file)

    def copy_file(self, src, dst, normalise=False):
        CheckPath(src, self)

        if normalise:
            dst = path.join(dst, self.normalise_file_name(src))

        if not path.exists(dst):
            copy2(src=src, dst=dst)

    def copy_files(self, src, dst, dirs_exist=True):
        CheckPath(src, self)
        CheckPath(dst, self)
        copytree(src, dst, ignore_dangling_symlinks=True, dirs_exist_ok=dirs_exist)

    def copy_normalised_files(self, src, dst, pattern, max=30):
        CheckPath(src, self)
        CheckPath(dst, self)

        found_files = self.find_by_pattern(src, pattern)

        for src_path in found_files:
            normallisd_name = self.normalise_file_name(filename=src_path, max=max)
            self.copy_file(src_path, path.join(dst, normallisd_name))

    def execute(self, cmd: str, shell=None):
        command = ShellExecutor()
        return command.execute(cmd)

    def make_dir(self, dst, mode=0o666):
        makedirs(dst, mode, exist_ok=True)

    def normalise_file_name(
        self, filename: str, max=20, pattern=r"([\s\_\,-]+)|([-]+)", replacement="-"
    ):
        filename = filename.replace(" ", "-")
        basename = path.basename(filename).strip().lower()
        if len(basename) > max:
            _, ext = basename.rsplit(".", 1)
            basename = f"{basename[:max]}.{ext}"
        return re.sub(pattern, replacement, basename)

    def set_path(self, name, folder, exist_ok=False):
        if name not in self._paths:
            if not path.exists(folder):
                makedirs(name=folder, exist_ok=exist_ok)
            self._paths[name] = folder
            setattr(self, name, folder)

    @classmethod
    def setUpClass(cls):
        pass
        # super().setUpClass(cls)

    @classmethod
    def tearDownClass(cls):
        pass
        # super().tearDownClass(cls)

    def tearDown(self) -> None:
        cleanup =  getattr(self, "cleanup", None)
        if cleanup:
            for folder in self._paths.values():
                if path.exists(folder):
                    rmtree(folder)

        gc.collect()
        return super().tearDown()
