#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kiểm tra API cơ bản của DetectRow 2.0
====================================

Script này kiểm tra các API cơ bản của DetectRow 2.0:
1. Trích xuất bảng từ ảnh
2. Trích xuất cột từ bảng
"""

import os
import sys
import cv2
import numpy as np
from pathlib import Path

# Import các module từ detect_row
try:
    from detect_row import AdvancedTableExtractor, AdvancedColumnExtractor
    print("✅ Đã import thành công các module từ detect_row")
except ImportError as e:
    print(f"❌ Lỗi import: {e}")
    sys.exit(1)

def ensure_dir(path):
    """Tạo thư mục nếu chưa tồn tại"""
    os.makedirs(path, exist_ok=True)
    print(f"📁 Đã tạo thư mục: {path}")

def test_table_extraction():
    """Kiểm tra trích xuất bảng"""
    print("\n🔍 KIỂM TRA TRÍCH XUẤT BẢNG")
    print("=" * 50)
    
    # Tạo thư mục output
    output_dir = "output/simple_test"
    ensure_dir(output_dir)
    
    # Khởi tạo table extractor
    table_extractor = AdvancedTableExtractor(
        input_dir="input",
        output_dir=output_dir,
        debug_dir=os.path.join(output_dir, "debug")
    )
    
    # Tìm ảnh đầu tiên trong thư mục input
    input_dir = Path("input")
    image_files = []
    
    for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
        image_files.extend(list(input_dir.glob(f"*{ext}")))
        image_files.extend(list(input_dir.glob(f"*{ext.upper()}")))
    
    if not image_files:
        print("❌ Không tìm thấy ảnh nào trong thư mục input/")
        return
    
    # Lấy ảnh đầu tiên
    image_path = image_files[0]
    print(f"🖼️ Sử dụng ảnh: {image_path.name}")
    
    # Trích xuất bảng
    try:
        print(f"🔄 Đang trích xuất bảng từ {image_path.name}...")
        # Sử dụng process_image thay vì extract_tables_from_image
        tables = table_extractor.process_image(str(image_path))
        
        if not tables:
            print(f"⚠️ Không phát hiện bảng nào trong {image_path.name}")
            return
        
        print(f"✅ Đã phát hiện {len(tables)} bảng")
        
        # Hiển thị thông tin về các bảng và lưu bảng
        for i, table_img in enumerate(tables):
            table_name = f"{image_path.stem}_table_{i}"
            table_path = os.path.join(output_dir, f"{table_name}.jpg")
            cv2.imwrite(table_path, table_img)
            print(f"  📋 Bảng {i+1}: {table_name} - Kích thước: {table_img.shape[1]}x{table_img.shape[0]}")
        
        return tables
        
    except Exception as e:
        print(f"❌ Lỗi khi trích xuất bảng: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_column_extraction(tables):
    """Kiểm tra trích xuất cột"""
    print("\n🔍 KIỂM TRA TRÍCH XUẤT CỘT")
    print("=" * 50)
    
    if not tables:
        print("❌ Không có bảng nào để trích xuất cột")
        return
    
    # Tạo thư mục output
    output_dir = "output/simple_test/columns"
    ensure_dir(output_dir)
    
    # Lấy ảnh đầu tiên trong thư mục input
    image_path = next(Path("input").glob("*.*"))
    
    # Lấy bảng đầu tiên
    table_img = tables[0]
    table_name = f"{image_path.stem}_table_0"
    
    # Lưu bảng đầu tiên vào thư mục tạm
    table_path = os.path.join("output/simple_test", f"{table_name}.jpg")
    
    # Khởi tạo column extractor
    column_extractor = AdvancedColumnExtractor(
        input_dir="output/simple_test",
        output_dir=output_dir,
        debug_dir=os.path.join(output_dir, "debug")
    )
    
    # Trích xuất cột
    try:
        print(f"🔄 Đang trích xuất cột từ {table_name}...")
        
        # Định nghĩa nhóm cột
        column_groups = {
            "header": [1],
            "content": [2, 3],
            "footer": [4],
            "all": [1, 2, 3, 4, 5]
        }
        
        # Trích xuất cột trực tiếp từ ảnh bảng
        columns_info = column_extractor.extract_columns_from_table(table_img, table_name)
        
        if not columns_info:
            print(f"⚠️ Không phát hiện cột nào trong {table_name}")
            return
        
        print(f"✅ Đã phát hiện {len(columns_info)} cột")
        
        # Lưu từng cột riêng biệt
        saved_columns = column_extractor.save_individual_columns(columns_info, table_name)
        print(f"✅ Đã lưu {len(saved_columns)} cột riêng biệt")
        
        # Gộp cột theo nhóm
        saved_merged = column_extractor.save_merged_columns(columns_info, table_name, column_groups)
        print(f"✅ Đã lưu {len(saved_merged)} nhóm cột đã gộp")
        
        # Hiển thị thông tin về các cột
        for i, col_info in enumerate(columns_info):
            print(f"  📏 Cột {i+1}: x={col_info['x1']}-{col_info['x2']}, w={col_info['width']}px")
        
        return columns_info
        
    except Exception as e:
        print(f"❌ Lỗi khi trích xuất cột: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Hàm chính"""
    print("🚀 KIỂM TRA API CƠ BẢN CỦA DETECTROW 2.0")
    print("=" * 50)
    
    # Kiểm tra trích xuất bảng
    tables = test_table_extraction()
    
    # Kiểm tra trích xuất cột
    if tables:
        columns = test_column_extraction(tables)
    
    print("\n✅ HOÀN THÀNH KIỂM TRA")

if __name__ == "__main__":
    main() 