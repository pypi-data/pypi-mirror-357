#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kiểm tra khả năng GPU nâng cao - DetectRow
=========================================

Script này kiểm tra và đánh giá khả năng sử dụng GPU của thư viện DetectRow:
1. Kiểm tra GPU có sẵn
2. So sánh tốc độ xử lý giữa CPU và GPU
3. Kiểm tra các tùy chọn GPU nâng cao
"""

import os
import sys
import cv2
import numpy as np
import time
import json
from datetime import datetime
from pathlib import Path

# Import các module từ detect_row
from detect_row import (
    AdvancedTableExtractor, 
    AdvancedColumnExtractor,
    AdvancedRowExtractorMain
)

# Import module GPU support
try:
    from detect_row.gpu_support import GPUSupport
    has_gpu_support = True
except ImportError:
    has_gpu_support = False

def ensure_dir(path):
    """Tạo thư mục nếu chưa tồn tại"""
    os.makedirs(path, exist_ok=True)
    print(f"📁 Đã tạo thư mục: {path}")

def check_gpu_availability():
    """Kiểm tra GPU có sẵn không"""
    print("\n🔍 KIỂM TRA GPU")
    print("=" * 50)
    
    if not has_gpu_support:
        print("❌ Module GPU support không có sẵn")
        return False
    
    try:
        gpu_support = GPUSupport()
        if gpu_support.is_gpu_available():
            print("✅ GPU có sẵn")
            
            # Kiểm tra thông tin GPU
            gpu_info = gpu_support.get_gpu_info()
            if gpu_info:
                print(f"📊 Thông tin GPU:")
                for key, value in gpu_info.items():
                    print(f"  - {key}: {value}")
            
            return True
        else:
            print("❌ GPU không có sẵn")
            return False
    except Exception as e:
        print(f"❌ Lỗi khi kiểm tra GPU: {e}")
        return False

def benchmark_cpu_vs_gpu(image_path, output_dir):
    """So sánh hiệu suất giữa CPU và GPU"""
    print("\n🔍 SO SÁNH HIỆU SUẤT CPU VS GPU")
    print("=" * 50)
    
    # Đọc ảnh
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Không thể đọc ảnh: {image_path}")
        return None
    
    # Tạo thư mục output
    ensure_dir(output_dir)
    
    # Lưu ảnh gốc
    original_path = os.path.join(output_dir, "original.jpg")
    cv2.imwrite(original_path, image)
    
    # Kết quả benchmark
    benchmark_results = {
        "image_path": image_path,
        "image_size": f"{image.shape[1]}x{image.shape[0]}",
        "cpu": {},
        "gpu": {}
    }
    
    # Benchmark với CPU
    print("\n📊 Benchmark với CPU:")
    
    # 1. Trích xuất bảng
    print("  1. Trích xuất bảng")
    cpu_table_extractor = AdvancedTableExtractor(
        input_dir=os.path.dirname(image_path),
        output_dir=os.path.join(output_dir, "cpu_tables"),
        debug_dir=os.path.join(output_dir, "cpu_debug"),
        use_gpu=False
    )
    
    cpu_start_time = time.time()
    cpu_tables = cpu_table_extractor.process_image(os.path.basename(image_path), margin=5, check_text=True)
    cpu_table_time = time.time() - cpu_start_time
    
    print(f"     ⏱️ Thời gian: {cpu_table_time:.2f}s")
    benchmark_results["cpu"]["table_extraction"] = cpu_table_time
    
    # Tìm các bảng đã trích xuất
    cpu_tables_dir = os.path.join(output_dir, "cpu_tables")
    cpu_table_files = []
    
    if os.path.exists(cpu_tables_dir):
        cpu_table_files = [f for f in os.listdir(cpu_tables_dir) if f.endswith('.jpg')]
        cpu_table_files.sort()
    
    print(f"     ✅ Trích xuất được {len(cpu_table_files)} bảng")
    benchmark_results["cpu"]["tables_count"] = len(cpu_table_files)
    
    # 2. Trích xuất hàng
    print("  2. Trích xuất hàng")
    cpu_row_extractor = AdvancedRowExtractorMain(
        input_dir=cpu_tables_dir,
        output_dir=os.path.join(output_dir, "cpu_rows"),
        debug_dir=os.path.join(output_dir, "cpu_debug"),
        use_gpu=False
    )
    
    cpu_rows_count = 0
    cpu_row_time = 0
    
    for table_file in cpu_table_files:
        table_start_time = time.time()
        rows = cpu_row_extractor.process_image(table_file)
        table_time = time.time() - table_start_time
        cpu_row_time += table_time
        
        if rows:
            cpu_rows_count += len(rows)
    
    print(f"     ⏱️ Thời gian: {cpu_row_time:.2f}s")
    print(f"     ✅ Trích xuất được {cpu_rows_count} hàng")
    benchmark_results["cpu"]["row_extraction"] = cpu_row_time
    benchmark_results["cpu"]["rows_count"] = cpu_rows_count
    
    # 3. Trích xuất cột
    print("  3. Trích xuất cột")
    cpu_column_extractor = AdvancedColumnExtractor(
        input_dir=cpu_tables_dir,
        output_dir=os.path.join(output_dir, "cpu_columns"),
        debug_dir=os.path.join(output_dir, "cpu_debug"),
        use_gpu=False
    )
    
    cpu_columns_count = 0
    cpu_column_time = 0
    
    for table_file in cpu_table_files:
        # Đọc ảnh bảng
        table_path = os.path.join(cpu_tables_dir, table_file)
        table_image = cv2.imread(table_path)
        
        if table_image is None:
            continue
        
        # Phát hiện đường kẻ dọc
        gray = cv2.cvtColor(table_image, cv2.COLOR_BGR2GRAY)
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY_INV, 15, 3)
        
        table_start_time = time.time()
        v_lines = cpu_column_extractor.detect_vertical_lines(binary, min_line_length_ratio=0.4)
        
        # Trích xuất cột
        columns = cpu_column_extractor.extract_columns(table_image, v_lines)
        table_time = time.time() - table_start_time
        cpu_column_time += table_time
        
        if columns:
            cpu_columns_count += len(columns)
    
    print(f"     ⏱️ Thời gian: {cpu_column_time:.2f}s")
    print(f"     ✅ Trích xuất được {cpu_columns_count} cột")
    benchmark_results["cpu"]["column_extraction"] = cpu_column_time
    benchmark_results["cpu"]["columns_count"] = cpu_columns_count
    
    # Tổng thời gian CPU
    cpu_total_time = cpu_table_time + cpu_row_time + cpu_column_time
    print(f"  ⏱️ Tổng thời gian CPU: {cpu_total_time:.2f}s")
    benchmark_results["cpu"]["total_time"] = cpu_total_time
    
    # Nếu không có GPU support, dừng tại đây
    if not has_gpu_support:
        print("\n❌ Không có GPU support, bỏ qua benchmark GPU")
        return benchmark_results
    
    # Kiểm tra GPU có sẵn không
    gpu_support = GPUSupport()
    if not gpu_support.is_gpu_available():
        print("\n❌ GPU không có sẵn, bỏ qua benchmark GPU")
        return benchmark_results
    
    # Benchmark với GPU
    print("\n📊 Benchmark với GPU:")
    
    # 1. Trích xuất bảng
    print("  1. Trích xuất bảng")
    gpu_table_extractor = AdvancedTableExtractor(
        input_dir=os.path.dirname(image_path),
        output_dir=os.path.join(output_dir, "gpu_tables"),
        debug_dir=os.path.join(output_dir, "gpu_debug"),
        use_gpu=True
    )
    
    gpu_start_time = time.time()
    gpu_tables = gpu_table_extractor.process_image(os.path.basename(image_path), margin=5, check_text=True)
    gpu_table_time = time.time() - gpu_start_time
    
    print(f"     ⏱️ Thời gian: {gpu_table_time:.2f}s")
    benchmark_results["gpu"]["table_extraction"] = gpu_table_time
    
    # Tìm các bảng đã trích xuất
    gpu_tables_dir = os.path.join(output_dir, "gpu_tables")
    gpu_table_files = []
    
    if os.path.exists(gpu_tables_dir):
        gpu_table_files = [f for f in os.listdir(gpu_tables_dir) if f.endswith('.jpg')]
        gpu_table_files.sort()
    
    print(f"     ✅ Trích xuất được {len(gpu_table_files)} bảng")
    benchmark_results["gpu"]["tables_count"] = len(gpu_table_files)
    
    # 2. Trích xuất hàng
    print("  2. Trích xuất hàng")
    gpu_row_extractor = AdvancedRowExtractorMain(
        input_dir=gpu_tables_dir,
        output_dir=os.path.join(output_dir, "gpu_rows"),
        debug_dir=os.path.join(output_dir, "gpu_debug"),
        use_gpu=True
    )
    
    gpu_rows_count = 0
    gpu_row_time = 0
    
    for table_file in gpu_table_files:
        table_start_time = time.time()
        rows = gpu_row_extractor.process_image(table_file)
        table_time = time.time() - table_start_time
        gpu_row_time += table_time
        
        if rows:
            gpu_rows_count += len(rows)
    
    print(f"     ⏱️ Thời gian: {gpu_row_time:.2f}s")
    print(f"     ✅ Trích xuất được {gpu_rows_count} hàng")
    benchmark_results["gpu"]["row_extraction"] = gpu_row_time
    benchmark_results["gpu"]["rows_count"] = gpu_rows_count
    
    # 3. Trích xuất cột
    print("  3. Trích xuất cột")
    gpu_column_extractor = AdvancedColumnExtractor(
        input_dir=gpu_tables_dir,
        output_dir=os.path.join(output_dir, "gpu_columns"),
        debug_dir=os.path.join(output_dir, "gpu_debug"),
        use_gpu=True
    )
    
    gpu_columns_count = 0
    gpu_column_time = 0
    
    for table_file in gpu_table_files:
        # Đọc ảnh bảng
        table_path = os.path.join(gpu_tables_dir, table_file)
        table_image = cv2.imread(table_path)
        
        if table_image is None:
            continue
        
        # Phát hiện đường kẻ dọc
        gray = cv2.cvtColor(table_image, cv2.COLOR_BGR2GRAY)
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY_INV, 15, 3)
        
        table_start_time = time.time()
        v_lines = gpu_column_extractor.detect_vertical_lines(binary, min_line_length_ratio=0.4)
        
        # Trích xuất cột
        columns = gpu_column_extractor.extract_columns(table_image, v_lines)
        table_time = time.time() - table_start_time
        gpu_column_time += table_time
        
        if columns:
            gpu_columns_count += len(columns)
    
    print(f"     ⏱️ Thời gian: {gpu_column_time:.2f}s")
    print(f"     ✅ Trích xuất được {gpu_columns_count} cột")
    benchmark_results["gpu"]["column_extraction"] = gpu_column_time
    benchmark_results["gpu"]["columns_count"] = gpu_columns_count
    
    # Tổng thời gian GPU
    gpu_total_time = gpu_table_time + gpu_row_time + gpu_column_time
    print(f"  ⏱️ Tổng thời gian GPU: {gpu_total_time:.2f}s")
    benchmark_results["gpu"]["total_time"] = gpu_total_time
    
    # So sánh tốc độ
    if cpu_total_time > 0:
        speedup = cpu_total_time / gpu_total_time if gpu_total_time > 0 else float('inf')
        print(f"\n🚀 GPU nhanh hơn CPU {speedup:.2f}x")
        benchmark_results["speedup"] = speedup
    
    # Lưu kết quả benchmark
    result_path = os.path.join(output_dir, "benchmark_results.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(benchmark_results, f, indent=2)
    
    print(f"💾 Đã lưu kết quả benchmark: {result_path}")
    
    return benchmark_results

def test_gpu_advanced_options(image_path, output_dir):
    """Kiểm tra các tùy chọn GPU nâng cao"""
    print("\n🔍 KIỂM TRA TÙY CHỌN GPU NÂNG CAO")
    print("=" * 50)
    
    # Nếu không có GPU support, dừng tại đây
    if not has_gpu_support:
        print("❌ Không có GPU support, bỏ qua kiểm tra tùy chọn nâng cao")
        return None
    
    # Kiểm tra GPU có sẵn không
    gpu_support = GPUSupport()
    if not gpu_support.is_gpu_available():
        print("❌ GPU không có sẵn, bỏ qua kiểm tra tùy chọn nâng cao")
        return None
    
    # Đọc ảnh
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Không thể đọc ảnh: {image_path}")
        return None
    
    # Tạo thư mục output
    ensure_dir(output_dir)
    
    # Kiểm tra các tùy chọn GPU nâng cao
    advanced_options = {
        "default": {},
        "high_precision": {"precision": "high"},
        "low_precision": {"precision": "low"},
        "batch_processing": {"batch_size": 2},
        "custom_memory": {"memory_limit": 1024}  # 1GB
    }
    
    results = {}
    
    for option_name, options in advanced_options.items():
        print(f"\n📊 Kiểm tra tùy chọn: {option_name}")
        
        option_dir = os.path.join(output_dir, option_name)
        ensure_dir(option_dir)
        
        try:
            # Tạo GPU support với tùy chọn
            custom_gpu_support = GPUSupport(**options)
            
            # Trích xuất bảng
            table_extractor = AdvancedTableExtractor(
                input_dir=os.path.dirname(image_path),
                output_dir=os.path.join(option_dir, "tables"),
                debug_dir=os.path.join(option_dir, "debug"),
                use_gpu=True,
                gpu_options=options
            )
            
            start_time = time.time()
            tables = table_extractor.process_image(os.path.basename(image_path), margin=5, check_text=True)
            processing_time = time.time() - start_time
            
            # Tìm các bảng đã trích xuất
            tables_dir = os.path.join(option_dir, "tables")
            table_files = []
            
            if os.path.exists(tables_dir):
                table_files = [f for f in os.listdir(tables_dir) if f.endswith('.jpg')]
            
            print(f"  ⏱️ Thời gian: {processing_time:.2f}s")
            print(f"  ✅ Trích xuất được {len(table_files)} bảng")
            
            results[option_name] = {
                "time": processing_time,
                "tables_count": len(table_files),
                "options": options
            }
            
        except Exception as e:
            print(f"  ❌ Lỗi: {e}")
            results[option_name] = {
                "error": str(e),
                "options": options
            }
    
    # Lưu kết quả
    result_path = os.path.join(output_dir, "advanced_options_results.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Đã lưu kết quả kiểm tra tùy chọn nâng cao: {result_path}")
    
    return results

def main():
    """Hàm chính"""
    # Kiểm tra tham số dòng lệnh
    if len(sys.argv) < 2:
        print("Sử dụng: python test_gpu_advanced.py <đường_dẫn_ảnh>")
        return
    
    # Lấy đường dẫn ảnh từ tham số dòng lệnh
    image_path = sys.argv[1]
    output_dir = "gpu_test_output"
    
    print(f"🚀 KIỂM TRA KHẢ NĂNG GPU NÂNG CAO")
    print(f"📸 Ảnh đầu vào: {image_path}")
    print(f"📁 Thư mục đầu ra: {output_dir}")
    print(f"⏰ Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Kiểm tra file
    if not os.path.exists(image_path):
        print(f"❌ Không tìm thấy file: {image_path}")
        return
    
    # Tạo thư mục output
    ensure_dir(output_dir)
    
    # Kiểm tra GPU có sẵn không
    has_gpu = check_gpu_availability()
    
    # Benchmark CPU vs GPU
    benchmark_dir = os.path.join(output_dir, "benchmark")
    ensure_dir(benchmark_dir)
    
    benchmark_results = benchmark_cpu_vs_gpu(image_path, benchmark_dir)
    
    # Kiểm tra các tùy chọn GPU nâng cao
    if has_gpu:
        advanced_dir = os.path.join(output_dir, "advanced_options")
        ensure_dir(advanced_dir)
        
        advanced_results = test_gpu_advanced_options(image_path, advanced_dir)
    
    # Tổng kết
    print(f"\n{'='*50}")
    print("TỔNG KẾT")
    print(f"{'='*50}")
    
    print(f"🎉 HOÀN THÀNH KIỂM TRA KHẢ NĂNG GPU NÂNG CAO!")
    print(f"📁 Kết quả lưu tại: {output_dir}/")
    
    if has_gpu and benchmark_results:
        cpu_time = benchmark_results.get("cpu", {}).get("total_time", 0)
        gpu_time = benchmark_results.get("gpu", {}).get("total_time", 0)
        
        if cpu_time > 0 and gpu_time > 0:
            speedup = cpu_time / gpu_time
            print(f"🚀 GPU nhanh hơn CPU {speedup:.2f}x")
        
        print(f"⏱️ Thời gian xử lý CPU: {cpu_time:.2f}s")
        print(f"⏱️ Thời gian xử lý GPU: {gpu_time:.2f}s")

if __name__ == "__main__":
    main() 