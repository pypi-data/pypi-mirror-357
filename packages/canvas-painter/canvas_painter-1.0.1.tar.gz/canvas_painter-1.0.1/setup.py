import os
import shutil
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

ext_modules = [
    Extension(
        'canvas_painter',
        sources=['src/bindings.cpp'],
        libraries=['sfml-graphics', 'sfml-window', 'sfml-system'],
        library_dirs=[r'C:\Libraries\SFML-2.5.1\lib'],
        include_dirs=[r'C:\Libraries\SFML-2.5.1\include'],
        language='c++'
    )
]

class CustomBuildExt(build_ext):
    def run(self):
        super().run()
        build_lib = self.build_lib
        dll_folder = os.path.abspath('dlls')
        dll_files = [
            'sfml-window-2.dll',
            'sfml-system-2.dll',
            'sfml-graphics-2.dll',
        ]
        for dll in dll_files:
            src = os.path.join(dll_folder, dll)
            dest = os.path.join(build_lib, dll)
            print(f'Copying {src} to {dest}')
            shutil.copy(src, dest)

setup(
    name='canvas_painter',
    version='1.0.0',
    ext_modules=ext_modules,
    cmdclass={'build_ext': CustomBuildExt},
)
