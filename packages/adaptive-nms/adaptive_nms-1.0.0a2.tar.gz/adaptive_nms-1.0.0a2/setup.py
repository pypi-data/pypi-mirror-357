import os
import platform

from setuptools import setup
from setuptools.extension import Extension

if platform.system() == "Linux":
    cc_flags = ["-O3"]
elif platform.system() == "Windows":
    cc_flags = ["/O2"]
else:
    cc_flags = ["-O3"]

modules = [
    Extension(
        name="adaptivenms.square_covering_adaptive_nms",
        sources=[os.path.join("adaptivenms", "square_covering_adaptive_nms.pyx")],
        extra_compile_args=cc_flags,
        extra_link_args=cc_flags,
    ),
]

setup(ext_modules=modules)
