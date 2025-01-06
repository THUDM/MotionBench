from typing import Union
import random
import os
import time

import numpy as np
import cv2
from moviepy.editor import VideoFileClip
from pathlib import Path
import decord


def get_video_info(video_path: Union[str, Path]):
    if isinstance(video_path, str):
        video_path = Path(video_path)
    assert video_path.exists(), f"Video file {video_path} does not exist."

    # 使用 cv2 获取 FPS 和分辨率
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    # 使用 moviepy 获取视频时长
    video = VideoFileClip(str(video_path))
    duration = video.duration  # 时长以秒为单位
    duration_in_minutes = duration / 60  # 转换为分钟
    video.close()

    return {
        "duration_minutes": duration_in_minutes,
        "fps": fps,
        "resolution": {
            "width": width,
            "height": height
        }
    }


def extract_frames(video_path, fps=1):
    frames = []
    video = cv2.VideoCapture(video_path)

    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_interval = int(video.get(cv2.CAP_PROP_FPS) / fps)

    for i in range(frame_count):
        ret, frame = video.read()
        if not ret:
            break
        if i % frame_interval == 0:
            frames.append(frame)
    print(f'{video_path} 处理完成')
    video.release()
    # convert frames to PIL images
    frames = [Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)) for frame in frames]
    return frames


def gemini_frames(video_path, max_frames=3600):
    video_path = str(video_path)
    frames = extract_frames(video_path, fps=1)
    if len(frames) <= max_frames:
        return frames
    else:
        # 按照顺序平均抽取max_frames帧
        interval = len(frames) // max_frames
        return [frames[i] for i in range(0, len(frames), interval)]

def gemini_video(input_video_file: Union[str, Path], output_video_file: Union[str, Path], max_length: int = 3600,
                 use_gpu: bool = False):

    input_video_file = str(input_video_file)
    output_video_file = str(output_video_file)

    temp_dir = Path(output_video_file).parent / "video_frames" / Path(output_video_file).stem

    st = time.time()
    if not temp_dir.exists():
        temp_dir.mkdir(parents=True, exist_ok=True)

        # 使用ffmpeg提取帧
        if use_gpu:
            os.system(f"ffmpeg -hwaccel nvdec -vsync passthrough -i {input_video_file} -vf fps=1 {temp_dir}/frame_%04d.png")
        else:
            os.system(f"ffmpeg -vsync passthrough -i {input_video_file} -vf fps=1 {temp_dir}/frame_%04d.png")


    # 创建一个新目录用于保存软链接
    sampled_dir = Path(output_video_file).parent / "video_frames_sampled_3600" / Path(output_video_file).stem
    if not sampled_dir.exists():
        sampled_dir.mkdir(parents=True, exist_ok=True)

        # 获取所有提取的帧
        all_frames = sorted(temp_dir.glob("frame_*.png"))
        total_frames = len(all_frames)

        # 如果总帧数多于max_length帧，进行均匀采样
        if total_frames > max_length:
            sampled_indices = np.linspace(0, total_frames - 1, max_length, dtype=int)
            sampled_frames = [all_frames[i] for i in sampled_indices]
        else:
            sampled_frames = all_frames

        # 创建软链接
        for idx, frame in enumerate(sampled_frames):
            (sampled_dir / f"frame_{idx:04d}.png").symlink_to(frame)

    frame_pattern = str(sampled_dir / "frame_%04d.png")

    if use_gpu:
        os.system(f"ffmpeg -y -r 1 -i {frame_pattern} -c:v h264_nvenc -pix_fmt yuv420p {output_video_file}")
    else:
        os.system(f"ffmpeg -y -r 1 -i {frame_pattern} -pix_fmt yuv420p {output_video_file}")

    print(f"处理视频 {input_video_file} 完成，耗时 {time.time() - st:.2f} 秒")


