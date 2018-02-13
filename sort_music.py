import pandas as pd
import os
import click
import tqdm
# Add tqdm to pandas apply functions
tqdm.tqdm.pandas(desc="Pandas apply progress")

from music_sorter.process import find_files_in_subdirs, map_out_directory_structure, backup_files_to_new_directory_structure
from music_sorter.tagging import get_track_info_from_files, remove_duplicate_tracks, validate_artist_names, custom_tag_music

# Use click to call this from command line together with specification in setuptools
@click.command()
def cli():
    #if __name__ == '__main__':
    ############################
    #         Settings
    ############################
    # Directory to scan
    in_dir = '../mp3/'
    # Directory to copy files to that we process
    out_dir = '../sorted_music/'
    # Should the files be sorted according to album also (if this information is available)?
    include_album_in_path = False
    # Keep a record of the data in the output directory
    store_track_data = True
    # There may be a number of songs present that are a particular genre we wish to classify differently
    # Set up these searches here, which are placed in a separate folder
    tag_override = ['xmas']
    # Store settings that can be called from command line
    tag_override_dict ={
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
    # Select relevant settings
    tag_override = [v for k,v in tag_override_dict.items() if k in tag_override]
    ############################

    # Open a list of artist names we can check against
    reference_artists = pd.read_csv('artist_data/artist_details.csv')
    assert in_dir != out_dir, "You must backup your data to a different directory"

    # Find all .mp3 files in a directory/subdirectories
    filepath_dict = find_files_in_subdirs(in_dir)
    # Process files that are present
    df, fails = get_track_info_from_files(filepath_dict)
    # Remove duplicates found among directories
    df = remove_duplicate_tracks(df)

    # See which extracted artists match a reference list, and/or set approved name to artist in each file
    df = validate_artist_names(df, reference_artists)

    # Check if any overriding tag settings have been requested
    if len(tag_override)>0:
        for d in tag_override:
            # There may be a number of songs present that are a particular genre we wish to classify differently
            df = custom_tag_music(df, keywords=d['keywords'], searchfields=d['searchfields'], tagname=d['tagname'], case_sensitive=d['case_sensitive'])
            # If any of the above conditions are met, we will call the approved_name 'xmas_songs', which will be the folder htese songs are backed up to
            df['approved_name'] = df.apply(lambda row: d['foldername'] if row[d['tagname']]==True else row['approved_name'], axis=1)

    # Tag all failures the same, so they eventually end up int he same folder
    fails['approved_name'] = '_Failures'

    # Find out some info
    print("\nTop 10 artists by track count that were found:\n{}".format(df['approved_name'].value_counts().head(10)))
    print("The following filetypes were parsed:\n{}\n".format(df['filetype'].value_counts()))

    # Map out the directory structure that will be followed later, then backup to the new destination
    print("Backing up music...")
    df = map_out_directory_structure(df, out_dir, include_album_in_path)
    backup_files_to_new_directory_structure(df)

    # Apply the same process to failures
    print("Backing up failures...")
    fails = map_out_directory_structure(fails, out_dir, include_album_in_path)
    backup_files_to_new_directory_structure(fails)

    if store_track_data:
        # Save information to file
        df.to_csv(os.path.join(out_dir,'musicFileRecord.csv'))
        fails.to_csv(os.path.join(out_dir,'musicFileRecordFailures.csv'))








    #
