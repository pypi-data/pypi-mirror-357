import json
import os
from pathlib import Path
from collections import defaultdict

def split_len(folder_path, output_path=None):
    folder_path = Path(folder_path)
    if output_path is None:
        output_path = folder_path.parent / f"{folder_path.name}_split_by_len"
    else:
        output_path = Path(output_path)
    
    # 定义长度范围和对应的文件夹名称
    len_ranges = [
        (0, 8000, "0_8k"),
        (8000, 16000, "8_16k"),
        (16000, 32000, "16_32k"),
        (32000, 64000, "32_64k"),
        (64000, 128000, "64_128k"),
        (128000, float('inf'), "128k_")
    ]
    
    # 创建输出文件夹
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 创建子文件夹
    for _, _, folder_name in len_ranges:
        (output_path / folder_name).mkdir(exist_ok=True)
    
    # 为每个长度范围创建输出文件句柄字典
    output_files = {}
    record_count = defaultdict(int)
    total_records = 0
    error_records = 0
    processed_files = 0
    
    try:
        # 遍历所有JSONL文件
        for jsonl_file in folder_path.glob("*.jsonl"):
            processed_files += 1
            print(f"Processing: {jsonl_file.name}")
            
            try:
                with open(jsonl_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue
                        
                        try:
                            data = json.loads(line)
                            total_records += 1
                            
                            # 检查是否有LEN字段
                            if 'LEN' not in data:
                                print(f"Warning: Missing LEN field in line {line_num} of {jsonl_file.name}")
                                error_records += 1
                                continue
                            
                            record_len = data['LEN']
                            
                            # 确定该记录应该放入哪个长度范围
                            target_folder = None
                            for min_len, max_len, folder_name in len_ranges:
                                if min_len <= record_len < max_len:
                                    target_folder = folder_name
                                    break
                            
                            if target_folder:
                                # 如果该长度范围的输出文件还没有打开，就打开它
                                if target_folder not in output_files:
                                    output_file_path = output_path / target_folder / jsonl_file.name
                                    output_files[target_folder] = open(output_file_path, 'w', encoding='utf-8')
                                
                                # 将记录写入对应的输出文件
                                output_files[target_folder].write(json.dumps(data, ensure_ascii=False) + '\n')
                                record_count[target_folder] += 1
                            else:
                                print(f"Warning: Record with LEN={record_len} doesn't fit any range in line {line_num} of {jsonl_file.name}")
                                error_records += 1
                        
                        except json.JSONDecodeError as e:
                            print(f"Error: JSON decode error in line {line_num} of {jsonl_file.name}: {str(e)}")
                            error_records += 1
                            continue
                            
            except Exception as e:
                print(f"Error: Error processing file {jsonl_file.name}: {str(e)}")
                continue
            
            # 关闭当前文件的所有输出文件句柄
            for file_handle in output_files.values():
                file_handle.close()
            output_files.clear()
    
    finally:
        # 确保所有文件句柄都被关闭
        for file_handle in output_files.values():
            try:
                file_handle.close()
            except:
                pass
    
    # 打印统计信息
    print("\n=== Processing Complete ===")
    print(f"Total files processed: {processed_files}")
    print(f"Total records processed: {total_records}")
    print(f"Total error records: {error_records}")
    print("\nRecord count per length range:")
    
    total_valid_records = 0
    for _, _, folder_name in len_ranges:
        count = record_count[folder_name]
        total_valid_records += count
        print(f"  {folder_name}: {count} records")
    
    print(f"\nTotal valid records: {total_valid_records}")
    print(f"Output path: {output_path}")
    
    # 检查并报告空文件夹
    empty_folders = []
    for _, _, folder_name in len_ranges:
        folder_path = output_path / folder_name
        if not any(folder_path.iterdir()):
            empty_folders.append(folder_name)
    
    if empty_folders:
        print(f"\nEmpty folders (no matching records): {', '.join(empty_folders)}")