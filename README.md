# music-sorter
A tool that enables sorting a collection of random music files into a more structured form.
```
download_artist_names.py     # Downloads some artist name data to use as reference from a public GitHub repository.
sort_music.py                # Processes the content of a user-specified music library.
```
Given a directory of music files (such as MP3, WAV, WMA, MP4, M4A), this tool will scan that directory, extract relevant tag data, and attempt to standardise the artist names according to a reference database of artist names.

## Usage
```
Usage: sort_music [OPTIONS]

Options:
  -i, --in-dir PATH         Input music library directory to be processed.
  -o, --out-dir PATH        Output directory to back up processed files.
  --keep-album BOOLEAN      Include album title in output directory structure.
                            [default: False]
  --keep-data BOOLEAN       Write information gathered form the files, such as
                            source, target, and tags, to files in output
                            directory.  [default: True]
  -f, --filt [xmas|comedy]  Apply pre-configured filtering for songs that
                            contain tags suggestive of these categories.
                            [default: ]
  --failure-dirname TEXT    Sub-directory to store files that could not be
                            processed properly.  [default: _Failures]
  --help                    Show this message and exit.
```

#### Example
This package uses `click` and `setuptools` to integrate the script into your `virtualenv`, meaning `sort_music` can be called within the virtualenv from anywhere.
```
$ pyenv virtualenv miniconda3-latest myvirtualenv
$ source activate myvirtualenv
$ git clone https://github.com/djm234/music-sorter.git
$ pip install music-sorter/ -r music-sorter/requirements.txt
$ sort_music -i path/to/music/library -o path/to/new/folder -f xmas
```
The tool then creates a backup of these files into another directory that follows a more structured format: `artist/album/title`, or `artist/title`. Any tracks that cannot be sufficiently identified are likely to be placed in a `_Unknown` directory. Any tracks that could not be processed by the script are placed in `_Fails`. After this point, you may decide whether the resulting structure is to your liking.
