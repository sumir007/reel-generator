import os
import glob
import subprocess
import ffmpeg

def convert_to_reel_ffmpeg(input_path, output_path, background_audio_path=None):
    target_w, target_h = 1080, 1920
    aspect_ratio_threshold = 0.01  # Allow small float error

    # Get video info (width & height)
    probe = ffmpeg.probe(input_path)
    video_stream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    in_w = int(video_stream['width'])
    in_h = int(video_stream['height'])

    # Check if video is already 9:16 (aspect ratio ≈ 0.5625)
    aspect_ratio = in_w / in_h
    is_916 = abs(aspect_ratio - (9 / 16)) < aspect_ratio_threshold

    cmd = ["ffmpeg", "-y", "-i", input_path]

    if background_audio_path and os.path.exists(background_audio_path):
        cmd += ["-i", background_audio_path]

    needs_resize = not is_916

    if needs_resize:
        # Compute scaling factor to fit within 1080x1920
        scale_factor = min(target_w / in_w, target_h / in_h)
        scaled_w = int(in_w * scale_factor)
        scaled_h = int(in_h * scale_factor)

        # FFmpeg requires even dimensions for some codecs
        scaled_w += scaled_w % 2
        scaled_h += scaled_h % 2

        pad_x = (target_w - scaled_w) // 2
        pad_y = (target_h - scaled_h) // 2

        scale_filter = f"scale={scaled_w}:{scaled_h},pad={target_w}:{target_h}:{pad_x}:{pad_y}:white"
    else:
        scale_filter = None

    if background_audio_path and os.path.exists(background_audio_path):
        if scale_filter:
            filter_complex = (
                f"[0:v]{scale_filter}[v];"
                "[0:a]volume=1[a0];"
                "[1:a]volume=0.2[a1];"
                "[a0][a1]amix=inputs=2:duration=first:dropout_transition=2[aout]"
            )
            cmd += [
                "-filter_complex", filter_complex,
                "-map", "[v]",
                "-map", "[aout]",
            ]
        else:
            filter_complex = (
                "[0:a]volume=1[a0];"
                "[1:a]volume=0.2[a1];"
                "[a0][a1]amix=inputs=2:duration=first:dropout_transition=2[aout]"
            )
            cmd += [
                "-filter_complex", filter_complex,
                "-map", "0:v",
                "-map", "[aout]",
            ]
    else:
        if scale_filter:
            cmd += ["-vf", scale_filter]
        else:
            cmd += ["-c:v", "copy"]

        cmd += ["-c:a", "aac"]

    cmd += [
        "-c:v", "libx264",
        "-preset", "fast",
        "-r", "30",
        "-shortest",
        "-movflags", "+faststart",
        output_path
    ]

    subprocess.run(cmd, check=True)

# === Batch processing ===
if __name__ == "__main__":
    base_download_dir = "E:/ReelGenerator/9gag_downloads"
    output_folder = "E:/ReelGenerator/Output"
    background_music = "E:/ReelGenerator/no-copyright-music-lofi-330213.mp3"

    # Select latest run_* folder
    subfolders = [os.path.join(base_download_dir, d) for d in os.listdir(base_download_dir)
                  if os.path.isdir(os.path.join(base_download_dir, d)) and d.startswith("run_")]

    if not subfolders:
        print("❌ No run_* folders found in 9gag_downloader")
        exit(1)

    input_folder = max(subfolders, key=os.path.getmtime)
    print(f"📂 Using latest folder: {input_folder}")

    os.makedirs(output_folder, exist_ok=True)

    video_files = glob.glob(os.path.join(input_folder, "*.mp4")) + glob.glob(os.path.join(input_folder, "*.webm"))
    for file in video_files:
        base = os.path.basename(file)
        output_file = os.path.join(output_folder, f"reel_{os.path.splitext(base)[0]}.mp4")
        print(f"🎬 Processing {base}...")
        try:
            convert_to_reel_ffmpeg(file, output_file, background_music)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error processing {base}: {e}")
        else:
            print(f"✅ Done: {output_file}")

    print("🎉 All videos converted!")
