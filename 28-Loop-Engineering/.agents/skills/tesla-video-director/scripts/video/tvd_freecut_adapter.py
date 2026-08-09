#!/usr/bin/env python3
import os
import sys
import json
import logging
import subprocess
import tempfile
import time
from pathlib import Path
from pydantic import BaseModel, Field

# Ensure standard logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("tvd_freecut")

try:
    from google import genai
    from google.genai import types
except ImportError:
    logger.error("google-genai is not installed. Please install it.")
    sys.exit(1)

class CutSegment(BaseModel):
    start_time: float = Field(..., description="Start time of the cut in seconds")
    end_time: float = Field(..., description="End time of the cut in seconds")
    description: str = Field(..., description="Brief description of the action or speech")

class CutList(BaseModel):
    cuts: list[CutSegment] = Field(
        default_factory=list,
        description="List of cut segments. Return an empty list [] if the requested subject is not detected."
    )

class FreeCutAdapter:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required.")
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-2.5-flash"  # Flash is good for large audio tasks
    
    def get_audio_duration(self, file_path: Path) -> float:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(file_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())

    def extract_audio_chunks(self, input_video: Path, output_dir: Path, chunk_duration: int = 600) -> list[tuple[Path, float]]:
        """Extracts low quality audio chunks from the video."""
        logger.info(f"Extracting audio chunks from {input_video} into {output_dir}")
        output_pattern = output_dir / "audio_chunk_%03d.m4a"
        cmd = [
            "ffmpeg", "-y", "-i", str(input_video),
            "-f", "segment", "-segment_time", str(chunk_duration),
            "-c:a", "aac", "-b:a", "64k", "-ar", "16000", "-ac", "1",
            "-vn", str(output_pattern)
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        chunks = []
        for p in sorted(output_dir.glob("audio_chunk_*.m4a")):
            duration = self.get_audio_duration(p)
            chunks.append((p, duration))
        
        logger.info(f"Generated {len(chunks)} chunks.")
        return chunks

    def validate_timecodes(self, cuts: list[CutSegment], chunk_duration: float) -> bool:
        """Level 2 QA for timecodes."""
        for cut in cuts:
            if cut.end_time <= cut.start_time:
                raise ValueError(f"Invalid cut: end_time ({cut.end_time}) <= start_time ({cut.start_time})")
            if cut.start_time < 0 or cut.end_time < 0:
                raise ValueError(f"Invalid cut: negative time in ({cut.start_time}, {cut.end_time})")
            if cut.start_time > chunk_duration + 5.0: # 5 seconds margin
                raise ValueError(f"Invalid cut: start_time ({cut.start_time}) > chunk duration ({chunk_duration})")
            # We don't strictly fail if end_time is slightly over, but we log it
        return True

    def get_cuts_from_gemini(self, audio_chunk: Path, chunk_duration: float, prompt: str) -> list[CutSegment]:
        logger.info(f"Uploading {audio_chunk} to Gemini...")
        uploaded_file = self.client.files.upload(file=str(audio_chunk))
        
        if not uploaded_file.name:
            raise RuntimeError("Uploaded file name is missing")
        file_name: str = uploaded_file.name
        
        try:
            # Wait for processing if needed
            while uploaded_file.state and uploaded_file.state.name == "PROCESSING":
                time.sleep(2)
                uploaded_file = self.client.files.get(name=file_name)
            
            logger.info("Generating cuts...")
            
            # [R-01 & R-02] Inject dynamic duration and empty cut rule
            enhanced_prompt = (
                f"{prompt}\n\n"
                f"CRITICAL: The media is exactly {chunk_duration:.2f} seconds long. "
                f"DO NOT output any timestamp > {chunk_duration:.2f}. "
                "If the requested subject is not detected in this media chunk, you MUST return an empty list [] for cuts."
            )
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    uploaded_file,
                    enhanced_prompt
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=CutList,
                )
            )
            
            if not response.text:
                raise ValueError("Empty response from Gemini")
            data = json.loads(response.text)
            cuts = [CutSegment(**c) for c in data.get("cuts", [])]
            
            # QA Validation
            logger.info("Validating timecodes...")
            self.validate_timecodes(cuts, chunk_duration)
            return cuts
            
        finally:
            logger.info(f"Cleaning up file {file_name}")
            self.client.files.delete(name=file_name)

    def generate_ffconcat(self, input_video: Path, all_cuts: list[CutSegment], output_path: Path):
        logger.info(f"Generating ffconcat file at {output_path}")
        with open(output_path, "w") as f:
            f.write("ffconcat version 1.0\n")
            for cut in all_cuts:
                f.write(f"file '{input_video.resolve()}'\n")
                f.write(f"inpoint {cut.start_time:.3f}\n")
                f.write(f"outpoint {cut.end_time:.3f}\n")

    def render_final_video(self, ffconcat_path: Path, output_video: Path):
        logger.info(f"Rendering final video to {output_video}")
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(ffconcat_path),
            "-c:v", "libx264", "-c:a", "aac",
            str(output_video)
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info("Rendering complete.")

    def run(self, input_video: Path, output_video: Path, prompt: str):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            chunks = self.extract_audio_chunks(input_video, tmp_path)
            
            all_cuts = []
            current_time_offset = 0.0
            
            for i, (chunk_path, duration) in enumerate(chunks):
                logger.info(f"Processing chunk {i+1}/{len(chunks)} (Duration: {duration:.2f}s)")
                
                max_retries = 3
                success = False
                
                for attempt in range(max_retries):
                    try:
                        cuts = self.get_cuts_from_gemini(chunk_path, duration, prompt)
                        # Offset the cuts
                        for c in cuts:
                            c.start_time += current_time_offset
                            c.end_time += current_time_offset
                        all_cuts.extend(cuts)
                        success = True
                        break
                    except Exception as e:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}")
                        time.sleep(2)
                
                if not success:
                    raise RuntimeError(f"Failed to process chunk {chunk_path} after {max_retries} attempts.")
                
                current_time_offset += duration
            
            ffconcat_path = tmp_path / "cuts.ffconcat"
            self.generate_ffconcat(input_video, all_cuts, ffconcat_path)
            
            self.render_final_video(ffconcat_path, output_video)
            
            final_duration = self.get_audio_duration(output_video)
            logger.info(f"Final video generated: {output_video} (Duration: {final_duration:.2f}s)")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="FreeCut Hybrid Adapter (TVD NextLevel)")
    parser.add_argument("-i", "--input", required=True, help="Input video file")
    parser.add_argument("-o", "--output", required=True, help="Output video file")
    parser.add_argument("-p", "--prompt", required=True, help="Prompt for Gemini describing what to keep/cut")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        logger.error(f"Input file {input_path} does not exist.")
        sys.exit(1)
        
    adapter = FreeCutAdapter()
    try:
        adapter.run(input_path, output_path, args.prompt)
    except Exception as e:
        logger.error(f"Execution failed: {e}")
        sys.exit(1)
