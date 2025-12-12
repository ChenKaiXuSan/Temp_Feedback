# %%

path_1 = "/home/chenkaixu/Temp_Feedback/GUI/assets_old/videos/fire.mp4"
json_path_1 = "/home/chenkaixu/Temp_Feedback/GUI/assets_old/llm_res/fire.json"

path_2 = "/home/chenkaixu/Temp_Feedback/GUI/assets_old/videos/ice_cup.mp4"
json_path_2 = "/home/chenkaixu/Temp_Feedback/GUI/assets_old/llm_res/ice_cup.json"

path_3 = path_1
json_path_3 = json_path_1

# %%
import cv2
import os
import re
from pathlib import Path
import json

def get_video_frame_count(video_path: str) -> int:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    # 某些视频 CAP_PROP_FRAME_COUNT 可能为 0/不准，兜底逐帧统计
    if n <= 0:
        cap = cv2.VideoCapture(video_path)
        n = 0
        while True:
            ret, _ = cap.read()
            if not ret:
                break
            n += 1
        cap.release()
    return n


def convert_str_dict(llm_res):
	match = re.search(r"\{.*?\}", llm_res[0], re.DOTALL)
	if match:
		return json.loads(match.group(0))
	return {"source": "none", "proportion": "none", "location": "none"}

def merge_json_files_frameidx(json_paths, video_paths, merged_json_path):
    """
    你的单条记录格式:
    {
      "second": 0,
      "ms": 0,
      "source": "heat",
      "proportion": 0.5789,
      "frame_idx": 0
    }
    合并后：所有条目保持同样字段，仅 frame_idx 加 offset 连续。
    offset 用视频真实帧数累加，确保和合并后视频对齐。
    """
    assert len(json_paths) == len(video_paths), "json_paths 和 video_paths 长度必须一致"

    merged = []
    frame_offset = 0

    for json_path, video_path in zip(json_paths, video_paths):
        with open(json_path, "r") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError(f"{json_path} 必须是 list[dict]，但实际是 {type(data)}")

        # 更新 frame_idx
        for item in data:
            new_item = {}
            if not isinstance(item, dict):
                raise ValueError(f"{json_path} 内部元素必须是 dict，但发现 {type(item)}")

            if "frame_idx" not in item:
                raise ValueError(f"{json_path} 缺少 key: frame_idx")

            _data = convert_str_dict(item["output_text"])

            new_item["second"] = item["second"]
            new_item["ms"] = item["ms"]
            new_item["source"] = _data["source"]
            new_item["proportion"] = _data["proportion"]
            new_item["frame_idx"] = int(item["frame_idx"]) + frame_offset
            merged.append(new_item)

        # 关键：offset 按视频帧数累加
        frame_offset += get_video_frame_count(video_path)

    os.makedirs(Path(merged_json_path).parent, exist_ok=True)
    with open(merged_json_path, "w") as f:
        json.dump(merged, f, indent=4, ensure_ascii=False)

    return frame_offset, len(merged)


# %%
import json
import cv2
import os
from pathlib import Path

merged_path = "GUI/assets_old/videos/merged_video.mp4"
merged_json_path = "GUI/assets_old/llm_res/merged_video.json"

# 常见帧索引字段名（按你项目可能性排序）
FRAME_KEYS = ["frame_idx", "frame_id", "frame", "idx", "frame_index"]

def detect_frame_key(sample_item: dict) -> str | None:
    for k in FRAME_KEYS:
        if k in sample_item:
            return k
    return None

def merge_json_files_with_video_offsets(json_paths, video_paths, merged_json_path):
    assert len(json_paths) == len(video_paths), "json_paths 和 video_paths 长度必须一致"

    merged_data = []
    frame_offset = 0
    frame_key = None

    for seg_id, (json_path, video_path) in enumerate(zip(json_paths, video_paths)):
        with open(json_path, "r") as f:
            data = json.load(f)

        if isinstance(data, dict):
            raise ValueError(f"{json_path} 读出来是 dict，不是 list。你需要告诉我结构我再适配。")
        if not isinstance(data, list):
            raise ValueError(f"{json_path} 读出来不是 list，实际类型: {type(data)}")

        # 找 frame key（只在第一次有样本时检测）
        if frame_key is None:
            for item in data:
                if isinstance(item, dict):
                    frame_key = detect_frame_key(item)
                    if frame_key is not None:
                        break

        # 更新 frame idx
        for item in data:
            if isinstance(item, dict):
                if frame_key is not None and frame_key in item:
                    item[frame_key] = int(item[frame_key]) + frame_offset
                # 可选：debug 信息
                item["segment_id"] = seg_id
                item["source_video"] = os.path.basename(video_path)

            merged_data.append(item)

        # offset 用视频真实帧数累加（最稳）
        seg_frames = get_video_frame_count(video_path)
        frame_offset += seg_frames

    os.makedirs(Path(merged_json_path).parent, exist_ok=True)
    with open(merged_json_path, "w") as f:
        json.dump(merged_data, f, indent=4, ensure_ascii=False)

    print(f"Detected frame key = {frame_key}, total_offset = {frame_offset}")

def merge_videos(video_paths, output_path):
    caps = [cv2.VideoCapture(p) for p in video_paths]

    width = int(caps[0].get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(caps[0].get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = caps[0].get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    os.makedirs(Path(output_path).parent, exist_ok=True)
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for cap, path in zip(caps, video_paths):
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video: {path}")

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame.shape[1] != width or frame.shape[0] != height:
                frame = cv2.resize(frame, (width, height))
            writer.write(frame)

        cap.release()

    writer.release()

def main():
    video_paths = [path_1, path_2, path_3]
    json_paths  = [json_path_1, json_path_2, json_path_3]

    merge_videos(video_paths, merged_path)

    total_frames, total_records = merge_json_files_frameidx(
        json_paths, video_paths, merged_json_path
    )

    print(f"✅ Merged video saved to: {merged_path}")
    print(f"✅ Merged JSON saved to: {merged_json_path}")
    print(f"   total_frames_offset={total_frames}, total_records={total_records}")
	
if __name__ == "__main__":
    main()



