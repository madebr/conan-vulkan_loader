# -*- coding: utf-8 -*-

from bincrafters import build_shared
from conans import tools

if __name__ == "__main__":
    builder = build_shared.get_builder()
    builder.add_common_builds(dll_with_static_runtime=True, shared_option_name=None if tools.os_info.is_windows else False)
    builder.run()
