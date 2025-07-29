#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Time: 2024-12-22 10:34:03

from __future__ import annotations

import os
import subprocess

from setuptools import Extension, find_packages, setup
from setuptools.command.build_ext import build_ext


class CMakeExtension(Extension):
    def __init__(self, name, source_dir = ''):
        Extension.__init__(self, name, sources = [])
        self.source_dir = os.path.abspath(source_dir)


class CMakeBuild(build_ext):
    def run(self):
        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext: CMakeExtension):
        home_directory = os.path.expanduser('~')
        if not home_directory.endswith('/'):
            home_directory += '/'
        ext_dir = home_directory + ".gmssl_3.1.1_install/"
        cmake_args = ['-DCMAKE_INSTALL_PREFIX=' + ext_dir, '-DBUILD_SHARED_LIBS=ON']

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        subprocess.check_call(['cmake', ext.source_dir] + cmake_args, cwd = self.build_temp)
        subprocess.check_call(['cmake', '--build', '.', '--target', 'install'] + build_args, cwd = self.build_temp)


setup(
    name = 'easy_gmssl',
    version = '1.3.0',
    description = 'easy gmssl for python',
    long_description = open('./easy_gmssl/README.md').read(),
    long_description_content_type = 'text/markdown',
    author = 'bowenerchen',
    author_email = 'bowenerchen@foxmail.com',
    url = 'https://cloud.tencent.com/developer/user/1371154/articles',
    packages = find_packages(),
    classifiers = [
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
    ],
    python_requires = '>=3.10',
    # install_requires = [
    #     'cmake >= 3.0'
    # ],
    ext_modules = [CMakeExtension('GmSSL', 'easy_gmssl/Core/GmSSL-3.1.1')],
    cmdclass = dict(build_ext = CMakeBuild),
    zip_safe = False,
)
