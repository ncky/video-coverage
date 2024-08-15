# video-coverage

Detect what time periods you have video footage saved. Extracts frames from video files based on metadata, allowing you to find frames from videos captured at a given time in the specified directory.

## Features

- Extracts video metadata (creation time and duration).
- Finds and processes frames from videos based on a target datetime.
- Allows saving the extracted frame to a PNG file.
- Optionally displays the extracted frame in a window.
- Displays metadata of all videos in the folder.
- Supports adjusting creation time based on video duration.

## Requirements

- Python 3.x
- `opencv-python` for video processing
- `hachoir` for metadata extraction
- `argparse` for command-line argument parsing

You can install the required Python packages using pip:

```bash
pip install opencv-python hachoir
```

## Usage
Run the script from the command line. Here are some common options:

### Display Help
To display the help message with all available options:
```bash
python .\vcov.py -h
```

### Example Commands
1. Find and save a specific frame

To search for a frame at a specific datetime and save it to a PNG file:
```bash
python .\vcov.py --search_for_frame --target_datetime "2024-06-19 19:23:50" --save_frame
```

2. Display metadata of all videos

To display metadata of all video files in the folder:
```bash
python .\vcov.py --display_metadata
```

3. Search for a frame and display it

To search for a frame and display it in a window:
```bash
python .\vcov.py --search_for_frame --target_datetime "2024-06-19 19:23:50" --display_frame
```

Adjust creation time and save a frame

To adjust the creation time by subtracting the video duration if using the last modified time and save the extracted frame:
```bash
python .\vcov.py --search_for_frame --target_datetime "2024-06-19 19:23:50" --save_frame --adjust_creation_time
```

## Command-Line Arguments
    --folder_path: Path to the folder containing video files (required).
    --show_times: Show execution times for operations.
    --display_metadata: Display metadata of all videos.
    --search_for_frame: Search for and process a specific frame.
    --target_datetime: Target datetime to search for in the format YYYY-MM-DD HH:MM:SS (default: 2024-06-19 19:23:50).
    --frame_offset: Offset in frames to apply when searching (default: 0).
    --save_frame: Save the found frame to a PNG file.
    --display_frame: Display the found frame in a window.
    --adjust_creation_time: Adjust creation time by subtracting video duration if using last modified time.
