# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os
import shutil


class VulkanLoaderConan(ConanFile):
    name = "vulkan_loader"
    version = "1.1.106"
    license = "Apache-2.0"
    author = "bincrafters <bincrafters@gmail.com>"
    url = "https://github.com/bincrafters-conan-vulkan_loader"
    homepage = "https://github.com/KhronosGroup/Vulkan-Loader"
    description = "Vulkan Loader"
    topics = ("vulkan", "khronos", "ghraphics", "loader", )
    exports = ["LICENSE.md", ]
    exports_sources = ["CMakeLists.txt", ]
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "wayland": [True, False],
        "xcb": [True, False],
        "xlib": [True, False],
    }
    default_options = {
        "shared": False,
        "wayland": True,
        "xcb": True,
        "xlib": True,
    }
    no_copy_source = True
    generators = "cmake",

    def configure(self):
        if self.settings.os == "Windows":
            del self.options.wayland
            del self.options.xcb
            del self.options.xlib
        else:
            del self.options.shared

    _source_subfolder = "source_subfolder"

    def requirements(self):
        self.requires("vulkan_headers/{}@{}/{}".format(self.version, self.user, self.channel))

    def system_requirements(self):
        if tools.os_info.with_apt or tools.os_info.with_yum:
            if tools.os_info.with_apt:
                wayland_pkgs = ["libwayland-dev", ]
                xcb_pkgs = ["libx11-xcb-dev", ]
                xlib_pkgs = ["libx11-dev", "libxrandr-dev", ]
                arch_lut = {
                    "x86_64": "amd64",
                    "x86": "i386",
                }
                pack_sep = ":"
            elif tools.os_info.with_yum:
                wayland_pkgs = ["wayland-devel", ]
                xcb_pkgs = ["libxcb-devel", ]
                xlib_pkgs = ["libX11-devel", "libXrandr-devel", ]
                arch_lut = {
                    "x86_64": "x86_64",
                    "x86": "i686",
                }
                pack_sep = "."
            packages = []
            if self.options.wayland:
                packages.extend(wayland_pkgs)
            if self.options.xcb:
                packages.extend(xcb_pkgs)
            if self.options.xlib:
                packages.extend(xlib_pkgs)
            installer = tools.SystemPackageTool()
            arch = arch_lut.get(str(self.settings.arch), str(self.settings.arch))
            for package in packages:
                installer.install("{}{}{}".format(package, pack_sep, arch))

    def source(self):
        url = "https://github.com/KhronosGroup/Vulkan-Loader/archive/v{}.tar.gz".format(self.version)
        sha256 = "d48632a5459d21ee5d421cb6ef1611cc263d33cca3ef90d0f598f73d24dfc206"
        tools.get(url, sha256=sha256)

        os.rename("Vulkan-Loader-{}".format(self.version), self._source_subfolder)

        tools.replace_in_file(os.path.join(self._source_subfolder, "loader", "CMakeLists.txt"),
                              'if(${configuration} MATCHES "/MD")',
                              'if(OFF)')

    def build(self):
        cmake = CMake(self)
        cmake_defines = {
            "VULKAN_HEADERS_INSTALL_DIR": self.deps_cpp_info["vulkan_headers"].rootpath,
        }

        if str(self.settings.compiler) in ("gcc", "clang", ):
            cxx_flags_lut = {
                "x86_64": "-m64",
                "x86": "-m32",
            }
            cmake_defines["CMAKE_CXX_FLAGS"] = cxx_flags_lut[str(self.settings.arch)]
        if self.settings.os == "Windows":
            cmake_defines["ENABLE_STATIC_LOADER"] = not self.options.shared
        else:
            cmake_defines.update({
                "BUILD_WSI_WAYLAND_SUPPORT": self.options.wayland,
                "BUILD_WSI_XCB_SUPPORT": self.options.xcb,
                "BUILD_WSI_XLIB_SUPPORT": self.options.xlib,
            })

        cmake_environment = {}
        if self.settings.compiler != "Visual Studio":
            cmake_environment["ASFLAGS"] = "--32" if self.settings.arch == "x86" else "--64"

        with tools.environment_append(cmake_environment):
            cmake.configure(defs=cmake_defines)
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install(build_dir=self.build_folder)
        if tools.os_info.is_linux:
            shutil.rmtree(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.libs.append("cfgmgr32")
