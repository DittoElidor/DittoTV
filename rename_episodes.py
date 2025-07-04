import os
import re

# --- Configuration ---
# The script will rename files to this format, e.g., "פרק 1.mp4"
NEW_NAME_PREFIX = "פרק "

# --- Main Script Logic ---

def natural_sort_key(s):
    """
    A key for natural sorting. E.g. 'episode10' comes after 'episode2'.
    Splits the string into text and number chunks.
    """
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def rename_episodes_in_current_folder():
    """
    Finds all video files in the current directory, sorts them,
    and renames them sequentially.
    """
    try:
        current_folder = os.getcwd()
        print(f"\nScanning folder: {current_folder}\n")

        video_files = []
        for filename in os.listdir(current_folder):
            if filename.lower().endswith(('.mp4', '.mkv', '.avi')):
                video_files.append(filename)
        
        if not video_files:
            print("No video files (.mp4, .mkv, .avi) found in this folder.")
            return

        # Sort the files using natural sort to handle numbers correctly
        # This assumes original filenames have some logical order (e.g., S01E01, S01E02)
        video_files.sort(key=natural_sort_key)
        
        print("The following files will be renamed:")
        for i, old_filename in enumerate(video_files):
            _, extension = os.path.splitext(old_filename)
            new_filename = f"{NEW_NAME_PREFIX}{i + 1}{extension}"
            print(f"  '{old_filename}'  ->  '{new_filename}'")
        
        # Confirmation prompt
        confirm = input("\nDo you want to proceed with renaming? (y/n): ").lower()
        
        if confirm == 'y':
            for i, old_filename in enumerate(video_files):
                _, extension = os.path.splitext(old_filename)
                new_filename = f"{NEW_NAME_PREFIX}{i + 1}{extension}"
                
                # Construct full paths for renaming
                old_filepath = os.path.join(current_folder, old_filename)
                new_filepath = os.path.join(current_folder, new_filename)
                
                # Check if the new file name already exists to avoid errors
                if os.path.exists(new_filepath):
                    print(f"SKIPPING: '{new_filename}' already exists.")
                    continue

                try:
                    os.rename(old_filepath, new_filepath)
                    print(f"Renamed '{old_filename}' to '{new_filename}'")
                except Exception as e:
                    print(f"ERROR renaming '{old_filename}': {e}")
            
            print("\n✅ Renaming complete!")
        else:
            print("\n❌ Renaming cancelled.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    rename_episodes_in_current_folder()
    input("\nPress Enter to exit.")

