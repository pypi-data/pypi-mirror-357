import os
import sys
import subprocess
import setuptools
import sysconfig
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.install import install
from setuptools.command.develop import develop
from pathlib import Path

class CMakeExtension(Extension):
    """Defines a CMake extension for compiling C++ code."""
    def __init__(self, name, sourcedir=""):
        super().__init__(name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
    """Runs CMake and Make to build the shared library."""
    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        python_include_dir = sysconfig.get_path("include")
        python_library_dir = sysconfig.get_config_var("LIBDIR")

        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
            f"-DPython3_EXECUTABLE={sys.executable}",
            f"-DPython3_INCLUDE_DIR={python_include_dir}",
            f"-DPython3_LIBRARY_DIR={python_library_dir}",
            "-DCMAKE_BUILD_TYPE=Release",
            "-DCMAKE_MAKE_PROGRAM=make",
            f"-DPython3_ROOT_DIR={os.path.dirname(os.path.dirname(sys.executable))}",
        ]


        build_temp = os.path.join(self.build_temp, ext.name)
        os.makedirs(build_temp, exist_ok=True)

        try:
            # Run CMake configuration
            subprocess.run(["cmake", ext.sourcedir] + cmake_args, 
                        cwd=build_temp, 
                        check=True,
                        capture_output=True,  # This captures the output
                        text=True)
            
            # Compile the C++ extension
            subprocess.run(["cmake", "--build", ".", "--config", "Release"],
                        cwd=build_temp,
                        check=True,
                        capture_output=True,  # This captures the output
                        text=True)
        
        except subprocess.CalledProcessError as e:
            print(f"CMake configuration failed with output:\n{e.stdout}\n{e.stderr}")
            raise
        # Explicitly copy the built library to the expected location
        lib_name = f"{ext.name}{sysconfig.get_config_var('EXT_SUFFIX')}"
        src_path = os.path.join(extdir, lib_name)
        dest_path = self.get_ext_fullpath(ext.name)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        if os.path.exists(src_path):
            self.copy_file(src_path, dest_path)

class CustomInstall(install):
    """Ensures the C++ extension is built during pip install."""
    def run(self):
        self.run_command("build_ext")
        install.run(self)

class CustomDevelop(develop):
    """Ensures the C++ extension is built during development install."""
    def run(self):
        self.run_command("build_ext")
        develop.run(self)

#Setup the installation
setup(
    ext_modules=[CMakeExtension("uaibot_cpp_bind", sourcedir="uaibot/c_implementation")],
    cmdclass={
        "build_ext": CMakeBuild,
        "install": CustomInstall,
        "develop": CustomDevelop,
    },
)
