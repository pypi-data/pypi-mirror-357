#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test API nâng cao của dự án DetectRow
====================================

Script này sử dụng các API nâng cao của dự án DetectRow để:
1. Phân tích cấu trúc bảng chi tiết
2. Trích xuất cột với các tùy chọn nâng cao
3. Phát hiện header và footer
4. Gộp cột với các cấu hình tùy chỉnh
"""

import os
import sys
import cv2
import numpy as np
import json
from datetime import datetime
from pathlib import Path

# Import các module từ detect_row
from detect_row import (
    AdvancedTableExtractor, 
    AdvancedColumnExtractor,
    AdvancedRowExtractorMain
)

# Import các module hỗ trợ GPU nếu có
try:
    from detect_row.gpu_support import GPUSupport
    has_gpu_support = True
except ImportError:
    has_gpu_support = False

def ensure_dir(path):
    """Tạo thư mục nếu chưa tồn tại"""
    os.makedirs(path, exist_ok=True)
    print(f"📁 Đã tạo thư mục: {path}")

def analyze_table_structure_advanced(table_image, output_dir):
    """Phân tích cấu trúc bảng chi tiết"""
    print("\n🔍 PHÂN TÍCH CẤU TRÚC BẢNG NÂNG CAO")
    print("=" * 50)
    
    # Lưu ảnh gốc
    original_path = os.path.join(output_dir, "original.jpg")
    cv2.imwrite(original_path, table_image)
    
    # Sử dụng API analyze_table_structure từ AdvancedTableExtractor
    extractor = AdvancedTableExtractor()
    
    # Phân tích cấu trúc bảng
    try:
        # Sử dụng phương thức analyze_table_structure nếu có
        if hasattr(extractor, 'analyze_table_structure'):
            structure = extractor.analyze_table_structure(table_image)
            print(f"✅ Đã phân tích cấu trúc bảng sử dụng phương thức có sẵn")
        else:
            # Nếu không có phương thức sẵn, sử dụng detect_table_structure
            structure = extractor.detect_table_structure(table_image)
            print(f"✅ Đã phân tích cấu trúc bảng sử dụng detect_table_structure")
    except Exception as e:
        print(f"❌ Lỗi khi phân tích cấu trúc bảng: {e}")
        return None
    
    # Vẽ cấu trúc bảng
    visualization = table_image.copy()
    
    # Vẽ đường kẻ ngang
    if hasattr(structure, 'horizontal_lines'):
        h_lines = structure.horizontal_lines
        for y in h_lines:
            cv2.line(visualization, (0, y), (table_image.shape[1], y), (0, 255, 0), 2)
        print(f"✅ Phát hiện {len(h_lines)} đường kẻ ngang")
    
    # Vẽ đường kẻ dọc
    if hasattr(structure, 'vertical_lines'):
        v_lines = structure.vertical_lines
        for x in v_lines:
            cv2.line(visualization, (x, 0), (x, table_image.shape[0]), (0, 0, 255), 2)
        print(f"✅ Phát hiện {len(v_lines)} đường kẻ dọc")
    
    # Đánh dấu header rows
    if hasattr(structure, 'header_rows'):
        header_rows = structure.header_rows
        print(f"✅ Phát hiện {len(header_rows)} header rows")
    
    # Lưu visualization
    viz_path = os.path.join(output_dir, "table_structure.jpg")
    cv2.imwrite(viz_path, visualization)
    print(f"💾 Đã lưu visualization: {viz_path}")
    
    return structure

def extract_columns_advanced(table_image, output_dir, column_groups=None):
    """Trích xuất cột với các tùy chọn nâng cao"""
    print("\n🔍 TRÍCH XUẤT CỘT NÂNG CAO")
    print("=" * 50)
    
    # Tạo thư mục output
    columns_dir = os.path.join(output_dir, "columns")
    merged_dir = os.path.join(output_dir, "merged_columns")
    ensure_dir(columns_dir)
    ensure_dir(merged_dir)
    
    # Lưu ảnh gốc
    original_path = os.path.join(output_dir, "original.jpg")
    cv2.imwrite(original_path, table_image)
    
    # Sử dụng AdvancedColumnExtractor
    extractor = AdvancedColumnExtractor(
        input_dir="",
        output_dir=columns_dir,
        debug_dir=os.path.join(output_dir, "debug")
    )
    
    # Nếu không có column_groups, tạo một cấu hình mặc định
    if column_groups is None:
        column_groups = {
            "first_two": [1, 2],
            "third": [3],
            "fourth": [4],
            "all": [1, 2, 3, 4, 5]
        }
    
    # Phát hiện đường kẻ dọc
    h, w = table_image.shape[:2]
    gray = cv2.cvtColor(table_image, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  cv2.THRESH_BINARY_INV, 15, 3)
    
    # Sử dụng phương thức detect_vertical_lines
    v_lines = extractor.detect_vertical_lines(binary, min_line_length_ratio=0.4)
    print(f"✅ Phát hiện {len(v_lines)} đường kẻ dọc")
    
    # Vẽ đường kẻ dọc
    lines_img = table_image.copy()
    for x in v_lines:
        cv2.line(lines_img, (x, 0), (x, h), (0, 0, 255), 2)
    
    # Lưu ảnh đường kẻ dọc
    lines_path = os.path.join(output_dir, "vertical_lines.jpg")
    cv2.imwrite(lines_path, lines_img)
    print(f"💾 Đã lưu ảnh đường kẻ dọc: {lines_path}")
    
    # Trích xuất cột
    columns = []
    
    # Sử dụng v_lines để trích xuất cột
    for i in range(len(v_lines) - 1):
        x1, x2 = v_lines[i], v_lines[i+1]
        
        # Bỏ qua cột quá hẹp
        if x2 - x1 < 20:
            continue
        
        # Crop cột
        column_img = table_image[:, x1:x2]
        
        # Lưu cột
        column_filename = f"column_{i+1}.jpg"
        column_path = os.path.join(columns_dir, column_filename)
        cv2.imwrite(column_path, column_img)
        
        columns.append({
            "id": i+1,
            "x1": x1,
            "x2": x2,
            "width": x2-x1,
            "height": h,
            "filename": column_filename,
            "path": column_path
        })
        
        print(f"✅ Cột {i+1}: {x2-x1}x{h}")
    
    # Gộp cột theo nhóm
    merged_columns = []
    
    for group_name, column_ids in column_groups.items():
        print(f"  🔄 Gộp nhóm '{group_name}': cột {column_ids}")
        
        # Tìm các cột cần gộp
        cols_to_merge = []
        for col in columns:
            if col["id"] in column_ids:
                cols_to_merge.append(col)
        
        if not cols_to_merge:
            print(f"  ⚠️ Không tìm thấy cột nào trong nhóm '{group_name}'")
            continue
        
        # Sắp xếp cột theo thứ tự
        cols_to_merge.sort(key=lambda x: x["id"])
        
        # Tìm vị trí bắt đầu và kết thúc
        x1 = min(col["x1"] for col in cols_to_merge)
        x2 = max(col["x2"] for col in cols_to_merge)
        
        # Crop ảnh
        merged_img = table_image[:, x1:x2]
        
        # Lưu ảnh
        merged_filename = f"{group_name}.jpg"
        merged_path = os.path.join(merged_dir, merged_filename)
        cv2.imwrite(merged_path, merged_img)
        
        merged_columns.append({
            "name": group_name,
            "x1": x1,
            "x2": x2,
            "width": x2-x1,
            "height": h,
            "columns": [col["id"] for col in cols_to_merge],
            "filename": merged_filename,
            "path": merged_path
        })
        
        print(f"  ✅ Đã gộp nhóm '{group_name}': {x2-x1}x{h}")
    
    # Vẽ các cột đã gộp
    result_img = table_image.copy()
    for merged in merged_columns:
        x1, x2 = merged["x1"], merged["x2"]
        name = merged["name"]
        cv2.rectangle(result_img, (x1, 0), (x2, h), (0, 255, 0), 2)
        cv2.putText(result_img, name, (x1+5, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    result_path = os.path.join(output_dir, "merged_columns.jpg")
    cv2.imwrite(result_path, result_img)
    print(f"💾 Đã lưu ảnh cột gộp: {result_path}")
    
    return {
        "columns": columns,
        "merged_columns": merged_columns
    }

def extract_tables_direct(image, output_dir):
    """Trích xuất bảng trực tiếp từ ảnh"""
    print("\n🔍 TRÍCH XUẤT BẢNG TRỰC TIẾP")
    print("=" * 50)
    
    # Tạo thư mục output
    tables_dir = os.path.join(output_dir, "tables")
    ensure_dir(tables_dir)
    
    # Sử dụng AdvancedTableExtractor
    extractor = AdvancedTableExtractor()
    
    # Trích xuất bảng
    try:
        # Phương pháp 1: Tìm contours
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Tìm contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Lọc contours theo kích thước
        min_area = image.shape[0] * image.shape[1] * 0.01  # Tối thiểu 1% diện tích ảnh
        table_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]
        
        # Nếu không tìm thấy bảng, thử phương pháp khác
        if not table_contours:
            # Phương pháp 2: Chia ảnh thành các phần
            h, w = image.shape[:2]
            num_tables = 3  # Giả sử có 3 bảng
            table_height = h // num_tables
            
            table_contours = []
            for i in range(num_tables):
                y1 = i * table_height
                y2 = (i + 1) * table_height if i < num_tables - 1 else h
                table_contours.append(np.array([
                    [[0, y1]],
                    [[w, y1]],
                    [[w, y2]],
                    [[0, y2]]
                ]))
        
        # Trích xuất và lưu các bảng
        tables = []
        for i, contour in enumerate(table_contours):
            x, y, w, h = cv2.boundingRect(contour)
            
            # Thêm margin
            margin = 5
            x = max(0, x - margin)
            y = max(0, y - margin)
            w = min(image.shape[1] - x, w + 2 * margin)
            h = min(image.shape[0] - y, h + 2 * margin)
            
            # Crop bảng
            table_img = image[y:y+h, x:x+w]
            
            # Lưu bảng
            table_filename = f"table_{i+1}.jpg"
            table_path = os.path.join(tables_dir, table_filename)
            cv2.imwrite(table_path, table_img)
            
            tables.append({
                "id": i+1,
                "x": x,
                "y": y,
                "width": w,
                "height": h,
                "filename": table_filename,
                "path": table_path
            })
            
            print(f"✅ Bảng {i+1}: {w}x{h}")
        
        # Vẽ các bảng đã phát hiện
        result_img = image.copy()
        for table in tables:
            x, y = table["x"], table["y"]
            w, h = table["width"], table["height"]
            cv2.rectangle(result_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(result_img, f"Table {table['id']}", (x+5, y+30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Lưu ảnh kết quả
        result_path = os.path.join(output_dir, "detected_tables.jpg")
        cv2.imwrite(result_path, result_img)
        print(f"💾 Đã lưu ảnh phát hiện bảng: {result_path}")
        
        return tables
        
    except Exception as e:
        print(f"❌ Lỗi khi trích xuất bảng: {e}")
        return []

def main():
    """Hàm chính"""
    # Kiểm tra tham số dòng lệnh
    if len(sys.argv) < 2:
        print("Sử dụng: python test_advanced_api.py <đường_dẫn_ảnh>")
        return
    
    # Lấy đường dẫn ảnh từ tham số dòng lệnh
    image_path = sys.argv[1]
    output_dir = "advanced_api_output"
    
    print(f"🚀 TEST API NÂNG CAO DETECT-ROW")
    print(f"📸 Ảnh đầu vào: {image_path}")
    print(f"📁 Thư mục đầu ra: {output_dir}")
    print(f"⏰ Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Kiểm tra GPU support
    if has_gpu_support:
        gpu_support = GPUSupport()
        if gpu_support.is_gpu_available():
            print(f"✅ GPU support: Available")
        else:
            print(f"⚠️ GPU support: Not available")
    else:
        print(f"⚠️ GPU support module not found")
    
    # Kiểm tra file
    if not os.path.exists(image_path):
        print(f"❌ Không tìm thấy file: {image_path}")
        return
    
    # Đọc ảnh
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Không thể đọc ảnh: {image_path}")
        return
    
    # Tạo thư mục output
    ensure_dir(output_dir)
    
    # Bước 1: Trích xuất bảng trực tiếp
    print(f"\n{'='*50}")
    print("BƯỚC 1: TRÍCH XUẤT BẢNG")
    print(f"{'='*50}")
    
    tables = extract_tables_direct(image, output_dir)
    
    if not tables:
        print("❌ Không trích xuất được bảng nào!")
        return
    
    print(f"✅ Trích xuất được {len(tables)} bảng")
    
    # Bước 2: Phân tích cấu trúc bảng và trích xuất cột nâng cao
    print(f"\n{'='*50}")
    print("BƯỚC 2: PHÂN TÍCH CẤU TRÚC BẢNG VÀ TRÍCH XUẤT CỘT NÂNG CAO")
    print(f"{'='*50}")
    
    # Định nghĩa nhóm cột nâng cao
    advanced_column_groups = {
        "info": [1, 2],           # Cột thông tin
        "result": [3, 4],         # Cột kết quả
        "info_result": [1, 2, 3], # Cột thông tin và kết quả đầu
        "all_data": [1, 2, 3, 4], # Tất cả dữ liệu
    }
    
    for i, table in enumerate(tables):
        table_path = table["path"]
        table_name = os.path.splitext(os.path.basename(table_path))[0]
        
        print(f"\n--- Xử lý {table_name} ({i+1}/{len(tables)}) ---")
        
        # Đọc ảnh bảng
        table_image = cv2.imread(table_path)
        if table_image is None:
            print(f"❌ Không thể đọc {table_path}")
            continue
        
        # Tạo thư mục output cho bảng này
        table_output_dir = os.path.join(output_dir, table_name)
        ensure_dir(table_output_dir)
        
        # Phân tích cấu trúc bảng
        structure = analyze_table_structure_advanced(table_image, table_output_dir)
        
        # Trích xuất cột nâng cao
        columns_result = extract_columns_advanced(
            table_image, 
            table_output_dir, 
            column_groups=advanced_column_groups
        )
    
    # Bước 3: Tạo báo cáo tổng hợp
    print(f"\n{'='*50}")
    print("BƯỚC 3: BÁO CÁO TỔNG HỢP")
    print(f"{'='*50}")
    
    # Tổng kết
    print(f"🎉 HOÀN THÀNH TEST API NÂNG CAO!")
    print(f"✅ Đã xử lý: {len(tables)} bảng")
    print(f"📁 Kết quả lưu tại: {output_dir}/")
    
    # Hiển thị danh sách bảng
    print(f"\n📋 {len(tables)} bảng đã trích xuất:")
    for table in tables:
        print(f"  - {table['filename']}: {table['width']}x{table['height']}")

if __name__ == "__main__":
    main() 