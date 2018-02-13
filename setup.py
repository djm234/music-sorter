from setuptools import setup

setup(
    name='Music-Sorter',
    version='0.1',
    author='Dan Mason',
    packages=['music_sorter',],
    description = ("A tool to help sort out a messy music library of files into"
                   "some kind of logical structure."),
    install_requires=[
        'Click',
    ],
    entry_points='''
            [console_scripts]
            sort_music=sort_music:cli
        ''',
    )
