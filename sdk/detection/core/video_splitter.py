import os
import math
from pathlib import Path
import subprocess

from sdk.app.logger import Logger

class VideoSplitter:
    def __init__(self, input_file, chunk_size_mb=50):
        self.logger = Logger(__name__)
        self.input_file = input_file
        self.chunk_size_mb = chunk_size_mb
        self.ffmpeg_bin_path = r"C:\Users\HP\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1.1-full_build\bin"
        self.ffprobe_path = rf"{self.ffmpeg_bin_path}\ffprobe.exe"
        self.ffmpeg_path = rf"{self.ffmpeg_bin_path}\ffmpeg.exe"

    @property
    def output_folder(self):
        base_name = Path(self.input_file).stem
        folder = Path(self.input_file).parent / base_name / "chunks"
        return folder
    
    def _get_file_size(self):
        return os.path.getsize(self.input_file)

    def _get_video_duration(self):
        cmd = [
            self.ffprobe_path,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            self.input_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        print("FFprobe stdout:", repr(result.stdout))
        print("FFprobe stderr:", repr(result.stderr))
        if result.returncode != 0:
            raise RuntimeError(f"ffprobe failed with code {result.returncode}")
        duration_str = result.stdout.strip()
        if not duration_str:
            raise ValueError("No duration found in ffprobe output")
        return float(duration_str)

    def split(self):
        self.logger.started("Starting video split process")
        
        os.makedirs(self.output_folder, exist_ok=True)

        total_size_bytes = self._get_file_size()
        chunk_size_bytes = self.chunk_size_mb * 1024 * 1024
        num_chunks = math.ceil(total_size_bytes / chunk_size_bytes)

        self.logger.info(f"Total file size: {total_size_bytes / (1024*1024):.2f} MB")
        self.logger.info(f"Chunk size: {self.chunk_size_mb} MB")
        self.logger.info(f"Splitting into {num_chunks} chunks")

        if num_chunks == 0:
            self.logger.info(f"Skipping splitting...")
            return

        duration_sec = self._get_video_duration()
        self.logger.info(f"Video duration: {duration_sec:.2f} seconds")

        duration_per_chunk = duration_sec / num_chunks
        self.logger.info(f"Approximate chunk duration: {duration_per_chunk:.2f} seconds")

        output_pattern = os.path.join(self.output_folder, "chunk_%03d.mp4")

        ffmpeg_cmd = [
            self.ffmpeg_path,
            "-i", self.input_file,
            "-c", "copy",
            "-map", "0",
            "-segment_time", str(duration_per_chunk),
            "-f", "segment",
            "-reset_timestamps", "1",
            output_pattern
        ]

        self.logger.info("Running ffmpeg to split video...")
        subprocess.run(ffmpeg_cmd, check=True)
        self.logger.info(f"Chunks saved to {self.output_folder}")
