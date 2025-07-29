#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kiểm tra API AdvancedColumnExtractor
==================================

Script này kiểm tra API AdvancedColumnExtractor với các bảng đã trích xuất.
"""

import os
import sys
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime

# Import module từ detect_row
from detect_row import AdvancedColumnExtractor

def ensure_dir(path):
    """Tạo thư mục nếu chưa tồn tại"""
    os.makedirs(path, exist_ok=True)
    print(f"📁 Đã tạo thư mục: {path}")

def list_image_files(directory):
    """Liệt kê tất cả các file ảnh trong thư mục"""
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']
    image_files = []
    
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            ext = os.path.splitext(file)[1].lower()
            if ext in image_extensions:
                image_files.append(file_path)
    
    return image_files

def test_column_extractor(tables_dir, output_dir, column_groups=None):
    """Kiểm tra AdvancedColumnExtractor với các bảng"""
    print(f"\n--- Xử lý các bảng trong thư mục: {tables_dir} ---")
    
    # Tạo thư mục output
    columns_dir = os.path.join(output_dir, "columns")
    merged_dir = os.path.join(output_dir, "merged_columns")
    debug_dir = os.path.join(output_dir, "debug")
    ensure_dir(columns_dir)
    ensure_dir(merged_dir)
    ensure_dir(debug_dir)
    
    # Khởi tạo AdvancedColumnExtractor
    extractor = AdvancedColumnExtractor(
        input_dir=tables_dir,
        output_dir=columns_dir,
        debug_dir=debug_dir
    )
    
    # Nếu không có column_groups, tạo một cấu hình mặc định
    if column_groups is None:
        column_groups = {
            "first_two": [1, 2],
            "middle": [3, 4],
            "first_three": [1, 2, 3],
            "all": [1, 2, 3, 4, 5]
        }
    
    # Liệt kê các file bảng
    table_files = list_image_files(tables_dir)
    if not table_files:
        print(f"  ❌ Không tìm thấy file bảng nào trong thư mục: {tables_dir}")
        return None
    
    print(f"  ✅ Tìm thấy {len(table_files)} bảng")
    
    # Xử lý từng bảng
    results = []
    total_columns = 0
    total_merged = 0
    
    for table_path in table_files:
        table_name = os.path.basename(table_path)
        print(f"  🔍 Trích xuất cột từ bảng: {table_name}")
        
        try:
            # Đọc ảnh bảng
            table_img = cv2.imread(table_path)
            if table_img is None:
                print(f"    ❌ Không thể đọc ảnh bảng: {table_path}")
                continue
            
            # Tạo thư mục cho bảng này
            table_columns_dir = os.path.join(columns_dir, os.path.splitext(table_name)[0])
            table_merged_dir = os.path.join(merged_dir, os.path.splitext(table_name)[0])
            ensure_dir(table_columns_dir)
            ensure_dir(table_merged_dir)
            
            # Phát hiện đường kẻ dọc
            gray = cv2.cvtColor(table_img, cv2.COLOR_BGR2GRAY)
            binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY_INV, 15, 3)
            
            v_lines = extractor.detect_vertical_lines(binary, min_line_length_ratio=0.4)
            print(f"    ✅ Phát hiện {len(v_lines)} đường kẻ dọc")
            
            # Vẽ đường kẻ dọc
            h, w = table_img.shape[:2]
            lines_img = table_img.copy()
            for x in v_lines:
                cv2.line(lines_img, (x, 0), (x, h), (0, 0, 255), 2)
            
            # Lưu ảnh đường kẻ dọc
            lines_path = os.path.join(debug_dir, f"{os.path.splitext(table_name)[0]}_vertical_lines.jpg")
            cv2.imwrite(lines_path, lines_img)
            
            # Trích xuất cột
            columns = []
            
            for i in range(len(v_lines) - 1):
                x1, x2 = v_lines[i], v_lines[i+1]
                
                # Bỏ qua cột quá hẹp
                if x2 - x1 < 20:
                    continue
                
                # Crop cột
                column_img = table_img[:, x1:x2]
                
                # Lưu cột
                column_filename = f"column_{i+1}.jpg"
                column_path = os.path.join(table_columns_dir, column_filename)
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
                
                print(f"      ✅ Cột {i+1}: {x2-x1}x{h}")
            
            total_columns += len(columns)
            
            # Gộp cột theo nhóm
            merged_columns = []
            
            for group_name, column_ids in column_groups.items():
                print(f"      🔄 Gộp nhóm '{group_name}': cột {column_ids}")
                
                # Tìm các cột cần gộp
                cols_to_merge = []
                for col in columns:
                    if col["id"] in column_ids:
                        cols_to_merge.append(col)
                
                if not cols_to_merge:
                    print(f"        ⚠️ Không tìm thấy cột nào trong nhóm '{group_name}'")
                    continue
                
                # Sắp xếp cột theo thứ tự
                cols_to_merge.sort(key=lambda x: x["id"])
                
                # Tìm vị trí bắt đầu và kết thúc
                x1 = min(col["x1"] for col in cols_to_merge)
                x2 = max(col["x2"] for col in cols_to_merge)
                
                # Crop ảnh
                merged_img = table_img[:, x1:x2]
                
                # Lưu ảnh
                merged_filename = f"{group_name}.jpg"
                merged_path = os.path.join(table_merged_dir, merged_filename)
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
                
                print(f"        ✅ Đã gộp nhóm '{group_name}': {x2-x1}x{h}")
            
            total_merged += len(merged_columns)
            
            # Vẽ các cột đã gộp
            result_img = table_img.copy()
            for merged in merged_columns:
                x1, x2 = merged["x1"], merged["x2"]
                name = merged["name"]
                cv2.rectangle(result_img, (x1, 0), (x2, h), (0, 255, 0), 2)
                cv2.putText(result_img, name, (x1+5, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Lưu ảnh kết quả
            result_path = os.path.join(debug_dir, f"{os.path.splitext(table_name)[0]}_merged_columns.jpg")
            cv2.imwrite(result_path, result_img)
            
            results.append({
                "table": table_path,
                "columns": columns,
                "merged_columns": merged_columns,
                "columns_dir": table_columns_dir,
                "merged_dir": table_merged_dir
            })
        
        except Exception as e:
            print(f"    ❌ Lỗi khi xử lý bảng: {e}")
    
    return {
        "tables_dir": tables_dir,
        "results": results,
        "total_columns": total_columns,
        "total_merged": total_merged
    }

def main():
    """Hàm chính"""
    # Kiểm tra tham số dòng lệnh
    if len(sys.argv) < 2:
        print("Sử dụng: python test_column_extractor.py <thư_mục_chứa_bảng>")
        print("Hoặc:    python test_column_extractor.py <thư_mục_chứa_bảng> <thư_mục_đầu_ra>")
        return
    
    # Thư mục chứa bảng đầu vào
    tables_dir = sys.argv[1]
    if not os.path.exists(tables_dir):
        print(f"❌ Không tìm thấy thư mục: {tables_dir}")
        return
    
    # Thư mục đầu ra
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "column_extractor_output"
    ensure_dir(output_dir)
    
    print(f"🚀 KIỂM TRA API ADVANCEDCOLUMNEXTRACTOR")
    print(f"📁 Thư mục bảng đầu vào: {tables_dir}")
    print(f"📁 Thư mục đầu ra: {output_dir}")
    print(f"⏰ Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Định nghĩa nhóm cột
    column_groups = {
        "info": [1, 2],           # Cột thông tin
        "result": [3, 4],         # Cột kết quả
        "info_result": [1, 2, 3], # Cột thông tin và kết quả đầu
        "all_data": [1, 2, 3, 4]  # Tất cả dữ liệu
    }
    
    # Kiểm tra column extractor
    result = test_column_extractor(tables_dir, output_dir, column_groups)
    if not result:
        print("❌ Không thể trích xuất cột")
        return
    
    # Tổng kết
    print(f"\n{'='*50}")
    print("TỔNG KẾT")
    print(f"{'='*50}")
    
    print(f"🎉 HOÀN THÀNH KIỂM TRA API ADVANCEDCOLUMNEXTRACTOR!")
    print(f"✅ Đã xử lý {len(result['results'])} bảng")
    print(f"✅ Đã trích xuất được tổng cộng {result['total_columns']} cột riêng lẻ")
    print(f"✅ Đã tạo được tổng cộng {result['total_merged']} nhóm cột gộp")
    print(f"📁 Kết quả lưu tại: {output_dir}/")

if __name__ == "__main__":
    main() 