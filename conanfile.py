"""
Conan package definition for the Clustering Library.

This file defines how the Clustering project is built and packaged using Conan.

ADDING NEW DEPENDENCIES:
When adding a new dependency, you MUST update BOTH files:
1. Add to requirements() method in this file (conanfile.py)
2. Add to CONAN_REQUIRES list in CMakeLists.txt

"""

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeConfigDeps, cmake_layout
from conan.tools.files import load
from conan.tools.scm import Git
import os
import os.path
import sys

required_conan_version = ">=2.25.0"

class ClusteringConan(ConanFile):
    """
    Conan package specification for Clustering library.

    Defines package metadata, build options, dependencies, and packaging logic
    for Conan package creation.
    """
    name = "clustering"
    def _get_git_version(self, git):
        try:
            version = git.run("describe --tags --exact-match HEAD").strip().lstrip('v')
            return version
        except Exception:
            tags = git.run('tag --list v[0-9]* --sort=-version:refname').splitlines()
            latest_tag = tags[0].strip().lstrip('v') if tags else ""
            commit_hash = git.get_commit()[:9]
            if not latest_tag:
                latest_tag = self._get_fallback_version()
            version = f"{latest_tag}.dev+{commit_hash}"
            return version

    def _get_fallback_version(self):
        # Fallback to contents in VERSION file
        version_file = os.path.join(self.recipe_folder, "VERSION")
        if os.path.exists(version_file):
            with open(version_file) as f:
                version = f.read().strip().lstrip('v')
                return version
        else:
            # No version source available
            raise Exception(
                "Unable to determine version. Git is unavailable "
                "and VERSION file does not exist."
            )

    def set_version(self):
        try:
            git = Git(self, self.recipe_folder)
            self.version = self.version or self._get_git_version(git)
        except Exception:
            self.version = self._get_fallback_version()


    url = "https://github.com/Lallapallooza/clustering.git"
    description = "Header-only C++20 clustering library with KD-Tree acceleration, AVX2 hot paths, and a thread pool for parallel workloads. Ships DBSCAN, HDBSCAN*, and k-means with a nanobind Python binding."
    settings = "os", "compiler", "build_type", "arch"
    package_type = "header-library"
    options = {
        "CLUSTERING_BUILD_BENCHMARK": [True, False],
        "CLUSTERING_BUILD_TESTS": [True, False],
        "CLUSTERING_BUILD_DOCS": [True, False],
        "CLUSTERING_CREATE_PYTHON_BINDINGS": [True, False],
        "python_version": ["ANY"]
    }
    default_options = {
        "CLUSTERING_BUILD_BENCHMARK": False,
        "CLUSTERING_BUILD_TESTS": False,
        "CLUSTERING_BUILD_DOCS": False,
        "CLUSTERING_CREATE_PYTHON_BINDINGS": False
    }

    # Folder where the source code will be located
    exports_sources = "CMakeLists.txt", "python/*", "apps/*", "app/*", "include/*", "cmake/*", "benchmark/*", "VERSION"

    def requirements(self):
        """
        Defines the runtime dependencies for this package based on enabled options.
        These dependencies will be automatically downloaded and linked when someone
        consumes this package from Artifactory.

        TO ADD NEW DEPENDENCY:
        1. Add self.requires("package/version") here
        2. Also add to CONAN_REQUIRES list in CMakeLists.txt
        """
        # Core dependencies (always required)
        self.requires("citor/0.6.1", transitive_headers=True)

        if self.options.CLUSTERING_CREATE_PYTHON_BINDINGS:
            self.requires("nanobind/2.13.0")

        if self.options.CLUSTERING_BUILD_TESTS:
            self.requires("gtest/1.14.0")
            self.requires("benchmark/1.9.1")

    def configure(self):
        """
        Configure package options and dependencies.
        """
        if self.options.CLUSTERING_CREATE_PYTHON_BINDINGS:
            self.options.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        else:
            del self.options.python_version

    def layout(self):
        """
        Defines the folder structure for the build. cmake_layout() sets up
        standard CMake folder conventions (build/, src/, include/, etc.)
        """
        cmake_layout(self)

        # Define project structure when used in editable mode.
        self.folders.source = "."
        self.folders.build = "build"
        self.folders.generators = os.path.join(self.folders.build, "generators")

        # Used by Clustering when imported in Editable mode.
        self.cpp.source.includedirs = ["include"] # Relative to the source directory
        self.cpp.build.libdirs = [os.path.join("lib", str(self.settings.build_type))] # Relative to build directory
        self.cpp.build.bindirs = [os.path.join("bin", str(self.settings.build_type))] # Relative to build directory

    def generate(self):
        """
        Generates CMake configuration files that tell CMake how to find dependencies
        and configure the build. Creates conan_toolchain.cmake and Find*.cmake files.
        """
        tc = CMakeToolchain(self)

        # Pass all options as CMake variables
        tc.cache_variables["CLUSTERING_BUILD_BENCHMARK"] = self.options.CLUSTERING_BUILD_BENCHMARK
        tc.cache_variables["CLUSTERING_BUILD_TESTS"] = self.options.CLUSTERING_BUILD_TESTS
        tc.cache_variables["CLUSTERING_BUILD_DOCS"] = self.options.CLUSTERING_BUILD_DOCS
        tc.cache_variables["CLUSTERING_CREATE_PYTHON_BINDINGS"] = self.options.CLUSTERING_CREATE_PYTHON_BINDINGS
        tc.variables["CONAN_CREATE"] = True

        tc.user_presets_path = False
        tc.generator = "Ninja Multi-Config"
        tc.generate()

        # Generate CMake dependencies with proper legacy support
        deps = CMakeConfigDeps(self)

        deps.generate()

    def build(self):
        """
        Compiles the source code using CMake.
        """
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        """
        Installs the built artifacts into the package folder.
        """
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        """
        Configure package information for consumers.

        CRITICAL: This method tells Conan NOT to generate CMake files for this package
        and instead rely on the CMake files that DEWM itself installs.
        """

        # Tell Conan that this package provides its own CMake configuration
        # and should not have auto-generated CMake files
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.builddirs = ["cmake"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.set_property("cmake_file_name", "Clustering")
        self.cpp_info.set_property("cmake_target_name", "Clustering::Clustering")

        if self.options.CLUSTERING_CREATE_PYTHON_BINDINGS:
            self.cpp_info.components["pybindings"].libs = ["clustering"]
            self.cpp_info.components["pybindings"].libdirs = ["lib/" + str(self.settings.build_type)]
            self.cpp_info.components["pybindings"].builddirs = ["cmake", "lib", "bin"]
            self.cpp_info.components["pybindings"].includedirs = ["include"]

        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
