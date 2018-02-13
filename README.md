# music-sorter
A tool that enables sorting a collection of random music files into a more structured form.
```
python download_artist_names.py     # Downloads some artist name data to use as reference from a public GitHub repository.
python sort_music.py                # Processes the content of a user-specified music library.
```
Given a directory of music files (such as MP3, WAV, WMA, MP4, M4A), this tool will scan that directory, extract relevant tag data, and attempt to standardise the artist names according to a reference database of artist names.

The tool then creates a backup of these files into another directory that follows a more structured format: `artist/album/title`, or `artist/title`. Any tracks that cannot be sufficiently identified are likely to be placed in a `_Unknown` directory. Any tracks that could not be processed by the script are placed in `_Fails`.

If the user specifies it, tracks that match a set of keywords can be automatically placed into a user-defined directory.
