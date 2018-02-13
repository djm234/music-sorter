import shutil
import tqdm
import os

def find_files_in_subdirs(parent_dir, filetypes=['.mp3', '.wav', '.ogg', '.flac', '.wma', '.mp4', '.m4a']):
    filetypes = [i.lower() for i in filetypes]
    filepath_dict = {}
    filecount = 0
    for root, dirs, files in os.walk(parent_dir):
        if len(files) > 0:
            matching_files = [f for f in files if os.path.splitext(f)[1].lower() in filetypes]
            filepath_dict[root] = matching_files
            filecount += len(matching_files)
    print("There were {} files with extension {} found".format(filecount, filetypes))
    return filepath_dict

def sanitise_foldername(s):
    # Strip bad chars for path names
    return ''.join([c for c in s if c not in '?|"<>:;/\\.`\',*'])

def map_out_directory_structure(df, out_dir='sorted_music/', keep_album=False):
    print("Applying directory structure logic:")
    all_target_directories = []
    all_destinations = []
    for i in tqdm.tqdm(range(len(df))):
        # Get row information
        row = df.iloc[i]
        # Use the 'approved' name we found earlier
        artist = row['approved_name']
        source = row['source']
        fname = os.path.basename(source)
        # Append artist name to out directory
        artist = sanitise_foldername(artist)
        target_dir = os.path.join(out_dir, artist)
        # Add album name, if applicable
        if keep_album:
            album = row['album']
            if not pd.isnull(album):
                album = sanitise_foldername(album)
                target_dir = os.path.join(target_dir, album)
        # Add filename
        destination = os.path.join(target_dir, fname)
        # Store
        all_target_directories.append(target_dir)
        all_destinations.append(destination)
    # Add to dataframe
    df['target_dir'] = all_target_directories
    df['destination'] = all_destinations
    return df

def backup_files_to_new_directory_structure(df):
    print("Backup music to destinations:")
    for i in tqdm.tqdm(range(len(df))):
        # Get row information
        row = df.iloc[i]
        target_dir = row['target_dir']
        destination = row['destination']
        source = row['source']
        # Check if the directory exists
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        # Check if file already present before copying
        if not os.path.exists(destination):
            copyfile(source, destination)
    return

def copyfile(source, destination):
    # Only perform copy if necessary
    if not os.path.exists(destination):
        shutil.copy2(source, destination)
    return
