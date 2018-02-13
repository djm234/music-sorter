from setuptools import setup, find_packages
#py_modules=['sort_music'],

setup(
    name='music-sorter',
    version='0.1',
    author='Dan Mason',
    packages=find_packages(),
    description = ("A tool to help sort out a messy library of music files into"
                   "some kind of logical structure, based upon tags."),
    install_requires=[
        'Click',
    ],
    entry_points='''
            [console_scripts]
            sort_music=music_sorter.scripts.sort_music:cli
        ''',
    )
