#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

SOURCE_DIR = "/nas/tangzecheng.tzc/datasets/LOOM_Data_ligh"
TARGET_BASE = "./benchmarks"

def main():
    source_items = os.listdir(SOURCE_DIR) if os.path.exists(SOURCE_DIR) else []
    for root, dirs, files in os.walk(TARGET_BASE):
        parts = Path(root).parts
        if len(parts) >= 3: 
            benchmark = Path(root).name
            for item in source_items:
                if benchmark.lower() in item.lower() or item.lower() in benchmark.lower():
                    data_dir = os.path.join(root, "data")
                    os.makedirs(data_dir, exist_ok=True)
                    source_path = os.path.join(SOURCE_DIR, item)
                    target_path = os.path.join(data_dir, item)
                    for sub_item in os.listdir(source_path):
                        sub_source = os.path.join(source_path, sub_item)
                        sub_target = os.path.join(data_dir, sub_item)
                        if not os.path.exists(sub_target):
                            if os.path.isdir(sub_source):
                                shutil.copytree(sub_source, sub_target)
                            else:
                                shutil.copy2(sub_source, sub_target)
                    print(f"复制: {item}/* -> {benchmark}/data")

if __name__ == "__main__":
    main()