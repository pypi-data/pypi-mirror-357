import os

from moviepy import VideoFileClip


def create(args):
    if not args.path:
        print("No path provided. Use -p or --path to specify the file path.")
        return
    video_path = args.path
    if not os.path.isfile(video_path):
        print(f"Error: File not found at path '{video_path}'")
        return
    try:
        clip = VideoFileClip(video_path)
        base, _ = os.path.splitext(video_path)
        gif_path = base + ".gif"
        print(f"Converting video to GIF at: {gif_path}")
        clip.write_gif(gif_path, fps=5)
        print("GIF created successfully!")
    except Exception as e:
        print(f"Failed to convert video to GIF: {e}")
