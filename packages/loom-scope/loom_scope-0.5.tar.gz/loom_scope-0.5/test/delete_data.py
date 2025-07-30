#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import random
import os
import sys
import glob

def process_single_jsonl_file(file_path, cases_to_keep=21):
    """
    处理单个JSONL文件，随机保留指定数量的行，直接覆盖原文件
    """
    # 读取所有行
    lines = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:  # 跳过空行
                lines.append(line)
    
    original_count = len(lines)
    
    # 检查行数是否足够保留
    if original_count <= cases_to_keep:
        print(f"  跳过 {os.path.basename(file_path)}: 行数不足或等于目标数量 ({original_count}行)")
        return {
            'original_count': original_count,
            'removed_count': 0,
            'final_count': original_count,
            'skipped': True
        }
    
    # 随机选择要保留的行索引
    indices_to_keep = set(random.sample(range(original_count), cases_to_keep))
    
    # 保留的行
    remaining_lines = [line for i, line in enumerate(lines) if i in indices_to_keep]
    
    # 直接覆盖原文件
    with open(file_path, 'w', encoding='utf-8') as f:
        for line in remaining_lines:
            f.write(line + '\n')
    
    removed_count = original_count - cases_to_keep
    print(f"  处理 {os.path.basename(file_path)}: {original_count} -> {cases_to_keep} 行 (删除{removed_count}行)")
    
    return {
        'original_count': original_count,
        'removed_count': removed_count,
        'final_count': cases_to_keep,
        'skipped': False
    }

def process_directory(directory_path, cases_to_keep=21, file_pattern="*.jsonl"):
    """
    处理目录下所有JSONL文件
    """
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"目录不存在: {directory_path}")
    
    if not os.path.isdir(directory_path):
        raise ValueError(f"路径不是目录: {directory_path}")
    
    # 查找所有JSONL文件
    search_pattern = os.path.join(directory_path, file_pattern)
    jsonl_files = glob.glob(search_pattern)
    
    if not jsonl_files:
        print(f"未找到匹配文件: {file_pattern}")
        return {}
    
    print(f"找到 {len(jsonl_files)} 个文件，每个保留 {cases_to_keep} 行")
    
    total_files_processed = 0
    total_cases_removed = 0
    total_files_skipped = 0
    
    for file_path in sorted(jsonl_files):
        try:
            stats = process_single_jsonl_file(file_path, cases_to_keep)
            total_files_processed += 1
            if stats['skipped']:
                total_files_skipped += 1
            else:
                total_cases_removed += stats['removed_count']
                
        except Exception as e:
            print(f"  错误 {os.path.basename(file_path)}: {e}")
    
    print(f"完成: 处理{total_files_processed}个文件, 删除{total_cases_removed}行, 跳过{total_files_skipped}个")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python script.py <目录路径> [保留行数]")
        print("示例: python script.py ./data 21")
        print("说明: 默认保留21行，输入数值表示每个文件随机保留多少行")
        sys.exit(1)
    
    directory_path = sys.argv[1]
    cases_to_keep = int(sys.argv[2]) if len(sys.argv) > 2 else 21
    
    if cases_to_keep <= 0:
        print("错误: 保留行数必须大于0")
        sys.exit(1)
    
    try:
        process_directory(directory_path, cases_to_keep)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()