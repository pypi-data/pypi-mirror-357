#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thử nghiệm tính năng nâng cao của DetectRow 2.0
===============================================

Script này thử nghiệm các tính năng nâng cao của DetectRow 2.0:
1. Phát hiện bảng và phân tích cấu trúc chi tiết
2. Trích xuất cột với các tùy chọn nâng cao
3. Gộp cột theo nhóm tùy chỉnh
4. Phát hiện header/footer thông minh
5. Tối ưu hóa hiệu suất với GPU (nếu có)
"""

import os
import sys
import cv2
import numpy as np
import json
import time
from pathlib import Path
from datetime import datetime

# Import các module từ detect_row
try:
    from detect_row import (
        AdvancedTableExtractor, 
        AdvancedColumnExtractor,
        AdvancedRowExtractor
    )
    print("✅ Đã import thành công các module từ detect_row")
except ImportError as e:
    print(f"❌ Lỗi import: {e}")
    sys.exit(1)

# Import GPU support nếu có
try:
    from detect_row.gpu_support import GPUManager
    has_gpu = True
    print("✅ Đã import thành công GPU support")
except ImportError:
    has_gpu = False
    print("⚠️ Không tìm thấy GPU support")

def ensure_dir(path):
    """Tạo thư mục nếu chưa tồn tại"""
    os.makedirs(path, exist_ok=True)
    print(f"📁 Đã tạo thư mục: {path}")

def check_gpu_support():
    """Kiểm tra hỗ trợ GPU"""
    if has_gpu:
        gpu_manager = GPUManager()
        if gpu_manager.is_gpu_available():
            gpu_info = gpu_manager.get_gpu_info()
            print(f"🎮 GPU khả dụng: {gpu_info}")
            return True
        else:
            print("⚠️ Không tìm thấy GPU hỗ trợ CUDA")
    return False

def analyze_image_structure(image_path, output_dir):
    """Phân tích cấu trúc ảnh và trích xuất bảng"""
    print(f"\n🔍 PHÂN TÍCH CẤU TRÚC ẢNH: {image_path}")
    print("=" * 60)
    
    # Đọc ảnh
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Không thể đọc ảnh: {image_path}")
        return None
    
    # Tạo thư mục output
    image_name = Path(image_path).stem
    image_output_dir = os.path.join(output_dir, image_name)
    ensure_dir(image_output_dir)
    
    # Lưu ảnh gốc
    original_path = os.path.join(image_output_dir, "original.jpg")
    cv2.imwrite(original_path, image)
    
    # Khởi tạo table extractor
    table_extractor = AdvancedTableExtractor(
        input_dir="",
        output_dir=os.path.join(image_output_dir, "tables"),
        debug_dir=os.path.join(image_output_dir, "debug")
    )
    
    # Đo thời gian xử lý
    start_time = time.time()
    
    # Trích xuất bảng
    print(f"🔄 Đang trích xuất bảng từ {image_path}...")
    tables = table_extractor.process_image(image_path)
    
    if not tables:
        print(f"⚠️ Không phát hiện bảng nào trong {image_path}")
        return None
    
    print(f"✅ Đã phát hiện {len(tables)} bảng trong {time.time() - start_time:.2f} giây")
    
    # Phân tích cấu trúc từng bảng
    table_results = []
    
    for i, table_img in enumerate(tables):
        table_name = f"{image_name}_table_{i}"
        print(f"\n📊 Phân tích bảng {i+1}/{len(tables)}: {table_name}")
        
        # Lưu ảnh bảng
        table_path = os.path.join(image_output_dir, "tables", f"{table_name}.jpg")
        cv2.imwrite(table_path, table_img)
        
        # Phân tích cấu trúc bảng
        try:
            structure = table_extractor.detect_table_structure(table_img)
            
            # Tạo visualization
            viz_img = table_img.copy()
            
            # Vẽ đường kẻ ngang
            for y in structure.horizontal_lines:
                cv2.line(viz_img, (0, y), (table_img.shape[1], y), (0, 255, 0), 2)
            
            # Vẽ đường kẻ dọc
            for x in structure.vertical_lines:
                cv2.line(viz_img, (x, 0), (x, table_img.shape[0]), (0, 0, 255), 2)
            
            # Đánh dấu header rows
            for row_idx in structure.header_rows:
                if row_idx < len(structure.horizontal_lines) - 1:
                    y1 = structure.horizontal_lines[row_idx]
                    y2 = structure.horizontal_lines[row_idx + 1]
                    cv2.rectangle(viz_img, (0, y1), (table_img.shape[1], y2), (255, 0, 0), 3)
            
            # Lưu visualization
            viz_path = os.path.join(image_output_dir, "debug", f"{table_name}_structure.jpg")
            cv2.imwrite(viz_path, viz_img)
            
            print(f"✅ Cấu trúc bảng: {len(structure.horizontal_lines)-1} hàng x {len(structure.vertical_lines)-1} cột")
            print(f"✅ Header rows: {structure.header_rows}")
            print(f"✅ Merged cells: {len(structure.merged_cells)}")
            
            table_results.append({
                "table_name": table_name,
                "path": table_path,
                "structure": structure,
                "visualization": viz_path
            })
            
        except Exception as e:
            print(f"❌ Lỗi khi phân tích cấu trúc bảng: {str(e)}")
    
    return table_results

def extract_columns_with_merging(table_results, output_dir, column_groups=None):
    """Trích xuất cột và gộp cột theo nhóm"""
    if not table_results:
        print("❌ Không có bảng nào để trích xuất cột")
        return None
    
    print("\n🔍 TRÍCH XUẤT VÀ GỘP CỘT")
    print("=" * 60)
    
    # Nếu không có column_groups, tạo một cấu hình mặc định
    if column_groups is None:
        column_groups = {
            "header": [1],
            "content": [2, 3],
            "footer": [4],
            "all": [1, 2, 3, 4, 5]
        }
    
    column_results = []
    
    for table_info in table_results:
        table_name = table_info["table_name"]
        table_path = table_info["path"]
        
        print(f"\n📊 Trích xuất cột từ bảng: {table_name}")
        
        # Đọc ảnh bảng
        table_img = cv2.imread(table_path)
        if table_img is None:
            print(f"❌ Không thể đọc ảnh bảng: {table_path}")
            continue
        
        # Tạo thư mục output cho cột
        columns_dir = os.path.join(output_dir, table_name, "columns")
        merged_dir = os.path.join(output_dir, table_name, "merged_columns")
        ensure_dir(columns_dir)
        ensure_dir(merged_dir)
        
        # Khởi tạo column extractor
        column_extractor = AdvancedColumnExtractor(
            input_dir="",
            output_dir=columns_dir,
            debug_dir=os.path.join(output_dir, table_name, "debug")
        )
        
        # Trích xuất cột
        try:
            columns_info = column_extractor.extract_columns_from_table(table_img, table_name)
            
            if not columns_info:
                print(f"⚠️ Không phát hiện cột nào trong bảng {table_name}")
                continue
            
            print(f"✅ Đã phát hiện {len(columns_info)} cột")
            
            # Lưu từng cột riêng biệt
            saved_columns = column_extractor.save_individual_columns(columns_info, table_name)
            print(f"✅ Đã lưu {len(saved_columns)} cột riêng biệt")
            
            # Gộp cột theo nhóm
            saved_merged = column_extractor.save_merged_columns(columns_info, table_name, column_groups)
            print(f"✅ Đã lưu {len(saved_merged)} nhóm cột đã gộp")
            
            # Tạo visualization
            viz_img = table_img.copy()
            
            # Vẽ các cột đã phát hiện
            for i, col in enumerate(columns_info):
                x1, x2 = col["x1"], col["x2"]
                cv2.rectangle(viz_img, (x1, 0), (x2, table_img.shape[0]), (0, 255, 0), 2)
                cv2.putText(viz_img, f"Col {i+1}", (x1+5, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Lưu visualization
            viz_path = os.path.join(output_dir, table_name, "columns_visualization.jpg")
            cv2.imwrite(viz_path, viz_img)
            
            column_results.append({
                "table_name": table_name,
                "columns": columns_info,
                "merged_groups": column_groups,
                "visualization": viz_path
            })
            
        except Exception as e:
            print(f"❌ Lỗi khi trích xuất cột: {str(e)}")
    
    return column_results

def main():
    """Hàm chính"""
    print("🚀 THỬ NGHIỆM TÍNH NĂNG NÂNG CAO CỦA DETECTROW 2.0")
    print("=" * 60)
    
    # Kiểm tra GPU
    has_gpu_support = check_gpu_support()
    
    # Tạo thư mục output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"output/advanced_test_{timestamp}"
    ensure_dir(output_dir)
    
    # Tìm các ảnh trong thư mục input
    input_dir = "input"
    image_files = []
    
    for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
        image_files.extend(list(Path(input_dir).glob(f"*{ext}")))
        image_files.extend(list(Path(input_dir).glob(f"*{ext.upper()}")))
    
    if not image_files:
        print("❌ Không tìm thấy ảnh nào trong thư mục input/")
        return
    
    print(f"🔍 Tìm thấy {len(image_files)} ảnh trong thư mục input/")
    
    # Cấu hình nhóm cột tùy chỉnh
    column_groups = {
        "header": [1],
        "content": [2, 3],
        "footer": [4],
        "all": [1, 2, 3, 4, 5]
    }
    
    # Xử lý từng ảnh
    all_results = {}
    
    for image_path in image_files:
        image_path_str = str(image_path)
        print(f"\n🖼️ XỬ LÝ ẢNH: {image_path.name}")
        print("-" * 60)
        
        # Phân tích cấu trúc ảnh và trích xuất bảng
        table_results = analyze_image_structure(image_path_str, output_dir)
        
        if table_results:
            # Trích xuất cột và gộp cột
            column_results = extract_columns_with_merging(table_results, output_dir, column_groups)
            
            all_results[image_path.name] = {
                "tables": table_results,
                "columns": column_results
            }
    
    # Lưu kết quả tổng hợp
    result_summary = {
        "timestamp": timestamp,
        "total_images": len(image_files),
        "gpu_support": has_gpu_support,
        "results": all_results
    }
    
    with open(os.path.join(output_dir, "results_summary.json"), "w", encoding="utf-8") as f:
        json.dump(result_summary, f, indent=2, ensure_ascii=False)
    
    print("\n✅ HOÀN THÀNH THỬ NGHIỆM")
    print(f"📁 Kết quả được lưu trong: {output_dir}")

if __name__ == "__main__":
    main() 