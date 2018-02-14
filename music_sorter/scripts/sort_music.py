import pandas as pd
import os
import click
import tqdm

from music_sorter.process import find_files_in_subdirs, map_out_directory_structure, backup_files_to_new_directory_structure
from music_sorter.tagging import get_track_info_from_files, remove_duplicate_tracks, validate_artist_names, custom_tag_music

# Add tqdm to pandas apply functions
tqdm.tqdm.pandas(desc="Pandas apply progress")

# There may be a number of songs present that are a particular genre we wish to classify differently
# Set up these searches here, which are placed in a separate folder
TAG_OVERRIDE_DICT = {
'xmas': {
    'foldername': '_Xmas',
    'tagname': 'xmas_songs',
    'searchfields': ['title', 'album'],
    'keywords': ['xmas', 'christmas'],
    'case_sensitive': False,
    },
'comedy': {
    'foldername': '_Comedy',
    'tagname': 'comedy_songs',
    'searchfields': ['title', 'album'],
    'keywords': ['funny', 'comedy'],
    'case_sensitive': False,
    },
}

# Use click to call this from command line together with specification in setuptools
@click.command()
@click.option('-i', '--in-dir', prompt=True,
              type=click.Path(exists=True),
              help="Input music library directory to be processed.")
@click.option('-o', '--out-dir', prompt=True,
              type=click.Path(),
              help="Output directory to back up processed files.")
@click.option('--keep-album', default=False,
              type=bool, show_default=True,
              help="Include album title in output directory structure.")
@click.option('--keep-data', default=True,
              type=bool, show_default=True,
              help="Write information gathered form the files, such as source, target, and tags, to files in output directory.")
@click.option('-f', '--filt', default=[],
              type=click.Choice(TAG_OVERRIDE_DICT.keys()),
              multiple=True, show_default=True,
              help="Apply pre-configured filtering for songs that contain tags suggestive of these categories.")
@click.option('--failure-dirname', default='_Failures',
              type=str, show_default=True,
              help="Sub-directory to store files that could not be processed properly.")
@click.option('--ref-artists-file', default=None,
              type=click.Path(exists=True), show_default=True,
              help="Path to a file that contains reference artists (not required).")
def cli(in_dir, out_dir, keep_album, keep_data, filt, failure_dirname, ref_artists):
    # Make sure paths to files the user has specified become absolute and are no longer relative
    # Directory to scan
    in_dir = os.path.abspath(in_dir)
    # Directory to backup files to that we process
    out_dir = os.path.abspath(out_dir)
    # Select relevant settings
    tag_override = [v for k,v in TAG_OVERRIDE_DICT.items() if k in filt]

    click.echo("Please note that this tool is likely to generate an extensive directory structure from music file tags"+\
    "and this may cause problems with any pre-existing existing directory structure."+\
    "It is recommended that the output directory is empty to start with.")

    # Make sure user understands consequences of continuing, if choice of output directory is potentially poor
    assert in_dir != out_dir, "You must backup your data to a different directory"

    if os.path.isdir(out_dir):
        # User confirmation
        click.echo("\nCAUTION: THE DIRECTORY '{}' ALREADY EXISTS.\n".format(out_dir))
        ok_to_continue = click.confirm(
        "Please confirm that you understand the potential consequences and are happy to carry on backing up music files to '{}'\nContinue?".format(out_dir),
        abort=False)
    else:
        # Output directory does not already exist
        ok_to_continue = True

    if ok_to_continue:
        # Open a list of artist names we can check against (making the assumption
        # that these names are properly capitalised, etc.).
        if ref_artists:
            reference_artists = [x.lower() for x in pd.read_csv("Please pass a path to a file containing names")['name'].values]
        else:
            reference_artists = None

        # Find all music files in a directory/subdirectories
        filepath_dict = find_files_in_subdirs(in_dir)
        # Process files that are present
        df, fails = get_track_info_from_files(filepath_dict)
        # Tag all failures the same, so they eventually end up in the same folder
        fails['approved_name'] = failure_dirname
        # Remove duplicates found among directories
        df = remove_duplicate_tracks(df)

        # See which extracted artists match a reference list, and/or set approved
        # name to artist in each file
        df = validate_artist_names(df, reference_artists)

        # Check if any overriding tag settings have been requested
        if len(tag_override)>0:
            for d in tag_override:
                # There may be a number of songs present that are a particular genre we wish to classify differently
                df = custom_tag_music(df, keywords=d['keywords'], searchfields=d['searchfields'],
                                          tagname=d['tagname'], case_sensitive=d['case_sensitive'])
                # If any of the above conditions are met, we will call the approved_name
                # by the specific tag, which will be the folder these songs are backed up to.
                df['approved_name'] = df.apply(lambda row: d['foldername']
                                               if row[d['tagname']]==True
                                               else row['approved_name'], axis=1)

        # Find out some info
        print("\nTop 10 artists by track count that were found:\n{}".format(df['approved_name'].value_counts().head(10)))
        print("The following filetypes were parsed:\n{}\n".format(df['filetype'].value_counts()))

        # Map out the directory structure that will be followed later, then backup to the new destination
        print("Backing up music that passed checks...")
        df = map_out_directory_structure(df, out_dir, keep_album)
        backup_files_to_new_directory_structure(df)

        # Apply the same process to failures
        print("Backing up failures separately...")
        fails = map_out_directory_structure(fails, out_dir, keep_album)
        backup_files_to_new_directory_structure(fails)

        if keep_data:
            # Save information to file
            df.to_csv(os.path.join(out_dir,'musicFileRecord.csv'))
            fails.to_csv(os.path.join(out_dir,'musicFileRecordFailures.csv'))

    return
