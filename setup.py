# -*- coding: utf-8 -*-

# A very simple setup script to create a single executable
#
# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the script without Python

from cx_Freeze import setup, Executable

includes = ["pkg_resources"]
excludes = ['tkinter']
packages = []

from pyqode.core.api.syntax_highlighter import get_all_styles

# collect pygments styles
for s in get_all_styles():
    module = 'pygments.styles.%s' % s.replace('-', '_')
    try:
        __import__(module)
    except ImportError:
        pass
    else:
        includes.append(module)
        print('pygment style:', module)


target = Executable(
    script='main.py',
    targetName="dev_window.exe",
    compress=True,
    # icon=None,
)

setup(
    name='dev_window',
    version='0.1',
    author="Ilya Petrash",
    description='dev_window',

    options={
        "build_exe": {
            "includes": includes,
            "excludes": excludes,
            "packages": packages,
            "build_exe": "bin",
            "namespace_packages": ["pyqode"],
        }
    },

    executables=[target]
)
