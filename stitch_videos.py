import os
import sys
import subprocess
import obspython as obs
import threading
import queue
import time
import json
from typing import Optional, Dict, Any, Callable, List


# Global variable to store JSON configuration
config_data = {}

def load_config(config: Optional[Dict[str, Any]] = None) -> None:
    """Load configuration from a JSON file."""
    global config_data

    # If a config dictionary is passed, use it directly
    if config is not None:
        config_data = config

        # This is just a small premature optimization to avoid loading the config file again if it's already provided.
        return

    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as config_file:
                config_data = json.load(config_file)
                obs.script_log(obs.LOG_INFO, f"Configuration loaded: {config_data}")
        except Exception as e:
            obs.script_log(obs.LOG_ERROR, f"Failed to load config.json: {e}")
    else:
        obs.script_log(obs.LOG_WARNING, "config.json not found. Using default settings.")


class StitchManager:
    """Singleton class to manage stitching operations"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(StitchManager, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance
    
    def _initialize(self):
        self.active_stitches: Dict[str, Dict[str, Any]] = {}  # Tracks active stitching processes by compilation name
        self.active_lock = threading.Lock()  # Lock for thread-safe access to active_stitches

    def is_stitching(self, compilation_name: str) -> bool:
        """Check if a compilation is currently being stitched"""
        with self.active_lock:
            return compilation_name in self.active_stitches

    def _register_stitch(self, compilation_name: str, folder_path: str, output_path: str) -> bool:
        """Register a new stitching operation if none is active for this compilation"""
        with self.active_lock:
            if compilation_name in self.active_stitches:
                return False
            self.active_stitches[compilation_name] = {
                'start_time': time.time(),
                'folder_path': folder_path,
                'output_path': output_path,
                'status': 'started'
            }
            return True

    def _unregister_stitch(self, compilation_name: str) -> None:
        """Remove a completed stitching operation"""
        with self.active_lock:
            if compilation_name in self.active_stitches:
                del self.active_stitches[compilation_name]

def stitch_videos_async(
    compilation_name: str,
    folder_path: str,
    output_path: str,
    sort_lambda: Optional[Callable[[str], Any]] = None,
    cleanup_source: bool = True,
    callback: Optional[Callable[[str], None]] = None
) -> Optional[str]:
    """
    Asynchronously stitches video files in a folder into one using FFmpeg.
    Returns immediately while processing continues in background.
    """
    stitch_mgr = StitchManager()
    
    # Skip if already stitching
    if stitch_mgr.is_stitching(compilation_name):
        obs.script_log(obs.LOG_WARNING, f"Already stitching compilation '{compilation_name}'. Skipping request.")
        return None

    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        obs.script_log(obs.LOG_WARNING, f"Invalid folder path: {folder_path}")
        return None

    # Collect video files at registration time to avoid including new ones added during processing
    video_files = [f for f in os.listdir(folder_path) if f.endswith(".mp4")]

    if not video_files:
        obs.script_log(obs.LOG_WARNING, "No video files found to stitch.")
        return None

    # Register this stitching operation
    if not stitch_mgr._register_stitch(compilation_name, folder_path, output_path):
        return None

    # Default sorting (newest to oldest) if no custom function provided
    if sort_lambda is None:
        sort_lambda = lambda f: os.path.getmtime(os.path.join(folder_path, f))

    # Apply sorting
    video_files = sorted(video_files, key=sort_lambda, reverse=False)

    # Logging file order
    obs.script_log(obs.LOG_INFO, f"Stitching videos for '{compilation_name}':")
    for video in video_files:
        obs.script_log(obs.LOG_INFO, f"- {video}")

    def process_videos() -> None:
        try:
            # Create a temporary file list for FFmpeg
            list_file_path = os.path.join(folder_path, f"file_list_{compilation_name}.txt")
            with open(list_file_path, "w") as f:
                for video in video_files:
                    f.write(f"file '{os.path.join(folder_path, video)}'\n")

            # Get ffmpeg configs
            ffmpeg_config = config_data.get("FFMpeg", {})


            # Get ffmpeg path from config
            ffmpeg_path = ffmpeg_config.get("Path", "ffmpeg")
            if not os.path.exists(ffmpeg_path):
                obs.script_log(obs.LOG_ERROR, f"FFmpeg path not found: {ffmpeg_path}. Please check your config.")
                return

            

            # FFmpeg command to concatenate videos
            ffmpeg_cmd = [
                ffmpeg_path,
                "-f", "concat",
                "-safe", "0",
                "-i", list_file_path,
                "-c", "copy"
            ]

            # Append user specified FFmpeg options from config if available
            ffmpeg_cmd.extend(ffmpeg_config.get("Args", []))

            # Set output file path
            ffmpeg_cmd.append(output_path)

            # Run FFmpeg
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, check=True)
            obs.script_log(obs.LOG_INFO, f"Successfully stitched videos into {output_path}")

            # Cleanup source files if requested
            if cleanup_source and not output_path.startswith("_comp_"):
                for video in video_files:
                    try:
                        vid_path = os.path.join(folder_path, video)
                        os.remove(vid_path)
                        obs.script_log(obs.LOG_INFO, f"Deleted source video: {video}")
                    except Exception as e:
                        obs.script_log(obs.LOG_ERROR, f"Failed to delete video {video}: {e}")

            # Cleanup list file
            try:
                os.remove(list_file_path)
            except:
                pass  # Ignore cleanup errors

            # Call the callback if provided
            if callback:
                callback(output_path)

        except subprocess.CalledProcessError as e:
            obs.script_log(obs.LOG_ERROR, f"FFmpeg error: {e.stderr}")
        except Exception as e:
            obs.script_log(obs.LOG_ERROR, f"Error during video stitching: {str(e)}")
        finally:
            # Always unregister when done
            stitch_mgr._unregister_stitch(compilation_name)

    # Start processing in background thread
    threading.Thread(target=process_videos, daemon=True).start()
    
    return output_path  # Return the expected output path immediately

def main() -> None:
    """Main function to run stitch_videos from command line."""
    if len(sys.argv) < 2:
        print("Usage: python stitch_videos.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    output_path = sys.argv[1]  # Can change if different output directory needed
    result = stitch_videos_async("test", folder_path, output_path)

    if result:
        print(f"Stitching videos into {result}")
        print("Process running in background. Check logs for completion.")
    else:
        print("Failed to start video stitching.")

if __name__ == "__main__":
    # Call load_config when the script is executed
    load_config()
    main()
