import os
import datetime
import cv2
import json
import argparse
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from time import perf_counter

METADATA_CACHE_FILE = 'video_metadata_cache.json'

def get_video_metadata(video_path, adjust_creation_time):
    try:
        parser = createParser(video_path)
        if not parser:
            print(f"Unable to parse {video_path}")
            return None, None, None

        metadata = extractMetadata(parser)
        if not metadata:
            print(f"Unable to extract metadata from {video_path}")
            return None, None, None

        # Extract duration
        duration = metadata.get('duration').total_seconds() if metadata.has('duration') else None

        # Try to get the most accurate creation time
        creation_time = None
        if metadata.has('creation_date'):
            creation_time = metadata.get('creation_date')
        elif metadata.has('datetime_original'):
            creation_time = metadata.get('datetime_original')
        elif metadata.has('date_time'):
            creation_time = metadata.get('date_time')

        # If creation time is the default invalid value or not found, fall back to file modification time
        if creation_time == datetime.datetime(1904, 1, 1) or creation_time is None:
            creation_time = datetime.datetime.fromtimestamp(os.path.getmtime(video_path))
            if adjust_creation_time and duration:
                creation_time -= datetime.timedelta(seconds=duration)
        
        return creation_time, duration, video_path
    except Exception as e:
        print(f"Error getting metadata for {video_path}: {e}")
        return None, None, None

def find_videos_in_folder(folder_path, adjust_creation_time):
    video_metadata_list = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')):
                video_path = os.path.join(root, file)
                creation_time, duration, video_path = get_video_metadata(video_path, adjust_creation_time)
                if creation_time and duration:
                    video_metadata_list.append({
                        'path': video_path,
                        'creation_time': creation_time.isoformat(),
                        'duration': duration
                    })
    return video_metadata_list

def save_metadata_to_file(metadata_list, filename):
    with open(filename, 'w') as f:
        json.dump(metadata_list, f, indent=4)

def load_metadata_from_file(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, 'r') as f:
        return json.load(f)

def get_frame_at_timestamp(video_path, timestamp, frame_offset=0):
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_number = int(timestamp * fps) + frame_offset
    
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = video.read()
    if ret:
        return frame
    else:
        print("Error retrieving frame.")
        return None

def find_frame_at_datetime(video_metadata_list, target_datetime, frame_offset=0):
    for video in video_metadata_list:
        start_time = datetime.datetime.fromisoformat(video['creation_time'])
        end_time = start_time + datetime.timedelta(seconds=video['duration'])
        
        if start_time <= target_datetime <= end_time:
            elapsed_time = (target_datetime - start_time).total_seconds()
            frame = get_frame_at_timestamp(video['path'], elapsed_time, frame_offset)
            if frame is not None:
                return frame
    print("No video found for the specified datetime.")
    return None

def display_frame(frame):
    if frame is not None:
        cv2.imshow("Frame", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("No frame to display.")

def save_frame_to_png(frame, filename):
    if frame is not None:
        cv2.imwrite(filename, frame)
    else:
        print("No frame to save.")

def main(args):
    # Load cached metadata if available
    stime = perf_counter()
    video_metadata_list = load_metadata_from_file(METADATA_CACHE_FILE)
    if not video_metadata_list:
        stime = perf_counter()
        # If no cache, find videos and save metadata to cache
        video_metadata_list = find_videos_in_folder(args.folder_path, args.adjust_creation_time)
        if args.show_times:
            print(f"Found all videos in {perf_counter() - stime} seconds")
        save_metadata_to_file(video_metadata_list, METADATA_CACHE_FILE)
    else:
        if args.show_times:
            print(f"Loaded metadata in {perf_counter() - stime} seconds")

    # Display loaded metadata if flag is set
    if args.display_metadata:
        for metadata in video_metadata_list:
            print(f"Path: {metadata['path']}, Creation Time: {metadata['creation_time']}, Duration: {metadata['duration']} seconds")

    # Example usage to find and display a frame
    if args.search_for_frame:
        target_datetime = datetime.datetime.strptime(args.target_datetime, '%Y-%m-%d %H:%M:%S')
        frame_offset = args.frame_offset

        stime = perf_counter()
        frame = find_frame_at_datetime(video_metadata_list, target_datetime, frame_offset)
        if args.show_times:
            print(f"Found frame in {perf_counter() - stime} seconds")

        # Display frame if flag is set
        if args.display_frame:
            display_frame(frame)

        # Save frame to PNG if flag is set
        if args.save_frame:
            save_frame_to_png(frame, 'captured_frame.png')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract and manipulate video frames based on metadata.")
    parser.add_argument('-f', '--folder_path', type=str, required=True, help='Path to the folder containing video files.')
    parser.add_argument('-t', '--show_times', action='store_true', help='Show execution times for operations.')
    parser.add_argument('-d', '--display_metadata', action='store_true', help='Display metadata of all videos.')
    parser.add_argument('-s', '--search_for_frame', action='store_true', help='Search for and process a specific frame.')
    parser.add_argument('-T', '--target_datetime', type=str, default='2024-06-19 19:23:50', help='Target datetime to search for (format: YYYY-MM-DD HH:MM:SS).')
    parser.add_argument('-o', '--frame_offset', type=int, default=0, help='Offset in frames to apply when searching.')
    parser.add_argument('-S', '--save_frame', action='store_true', help='Save the found frame to a PNG file.')
    parser.add_argument('-D', '--display_frame', action='store_true', help='Display the found frame in a window.')
    parser.add_argument('-A', '--adjust_creation_time', action='store_true', help='Adjust creation time by subtracting video duration if using last modified time.')


    args = parser.parse_args()

    # If no command-line arguments are provided, show help
    if not any(vars(args).values()):
        parser.print_help()
    else:
        main(args)
