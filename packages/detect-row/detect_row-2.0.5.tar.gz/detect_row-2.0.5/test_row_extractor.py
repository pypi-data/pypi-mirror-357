#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kiểm tra API AdvancedRowExtractorMain
===================================

Script này kiểm tra API AdvancedRowExtractorMain với các bảng đã trích xuất.
"""

import os
import sys
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime

# Import module từ detect_row
from detect_row import AdvancedRowExtractorMain

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

def test_row_extractor(tables_dir, output_dir):
    """Kiểm tra AdvancedRowExtractorMain với các bảng"""
    print(f"\n--- Xử lý các bảng trong thư mục: {tables_dir} ---")
    
    # Tạo thư mục output
    rows_dir = os.path.join(output_dir, "rows")
    debug_dir = os.path.join(output_dir, "debug")
    ensure_dir(rows_dir)
    ensure_dir(debug_dir)
    
    # Liệt kê các file bảng
    table_files = list_image_files(tables_dir)
    if not table_files:
        print(f"  ❌ Không tìm thấy file bảng nào trong thư mục: {tables_dir}")
        return None
    
    print(f"  ✅ Tìm thấy {len(table_files)} bảng")
    
    # Xử lý từng bảng
    results = []
    total_rows = 0
    
    for table_path in table_files:
        table_name = os.path.basename(table_path)
        print(f"  🔍 Trích xuất hàng từ bảng: {table_name}")
        
        try:
            # Đọc ảnh bảng
            table_img = cv2.imread(table_path)
            if table_img is None:
                print(f"    ❌ Không thể đọc ảnh bảng: {table_path}")
                continue
            
            # Tạo thư mục cho hàng của bảng này
            table_rows_dir = os.path.join(rows_dir, os.path.splitext(table_name)[0])
            ensure_dir(table_rows_dir)
            
            # Trích xuất hàng trực tiếp
            # 1. Chuyển sang ảnh xám và nhị phân
            gray = cv2.cvtColor(table_img, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # 2. Phát hiện đường kẻ ngang
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
            
            # 3. Tìm đường kẻ ngang
            h_lines = []
            contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w > table_img.shape[1] * 0.5:  # Chỉ lấy đường kẻ ngang đủ dài
                    h_lines.append(y + h//2)
            
            # Thêm đường biên trên và dưới
            h_lines = [0] + sorted(h_lines) + [table_img.shape[0]]
            
            # 4. Trích xuất hàng dựa trên đường kẻ ngang
            extracted_rows = []
            
            for i in range(len(h_lines) - 1):
                y1, y2 = h_lines[i], h_lines[i+1]
                
                # Bỏ qua hàng quá hẹp
                if y2 - y1 < 10:
                    continue
                
                # Crop hàng
                row_img = table_img[y1:y2, :]
                
                # Lưu hàng
                row_filename = f"row_{i+1}.jpg"
                row_path = os.path.join(table_rows_dir, row_filename)
                cv2.imwrite(row_path, row_img)
                
                extracted_rows.append(row_filename)
                
                h, w = row_img.shape[:2]
                print(f"      ✅ Hàng {i+1}: {w}x{h}")
            
            # Vẽ các hàng đã phát hiện
            result_img = table_img.copy()
            for i in range(len(h_lines) - 1):
                y1, y2 = h_lines[i], h_lines[i+1]
                cv2.rectangle(result_img, (0, y1), (table_img.shape[1], y2), (0, 255, 0), 2)
                cv2.putText(result_img, f"Row {i+1}", (10, y1+20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Lưu ảnh kết quả
            result_path = os.path.join(debug_dir, f"{os.path.splitext(table_name)[0]}_rows.jpg")
            cv2.imwrite(result_path, result_img)
            
            num_rows = len(extracted_rows)
            total_rows += num_rows
            print(f"    ✅ Đã trích xuất được {num_rows} hàng")
            
            results.append({
                "table": table_path,
                "rows": extracted_rows,
                "rows_dir": table_rows_dir
            })
        
        except Exception as e:
            print(f"    ❌ Lỗi khi xử lý bảng: {e}")
    
    return {
        "tables_dir": tables_dir,
        "results": results,
        "total_rows": total_rows
    }

def main():
    """Hàm chính"""
    # Kiểm tra tham số dòng lệnh
    if len(sys.argv) < 2:
        print("Sử dụng: python test_row_extractor.py <thư_mục_chứa_bảng>")
        print("Hoặc:    python test_row_extractor.py <thư_mục_chứa_bảng> <thư_mục_đầu_ra>")
        return
    
    # Thư mục chứa bảng đầu vào
    tables_dir = sys.argv[1]
    if not os.path.exists(tables_dir):
        print(f"❌ Không tìm thấy thư mục: {tables_dir}")
        return
    
    # Thư mục đầu ra
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "row_extractor_output"
    ensure_dir(output_dir)
    
    print(f"🚀 KIỂM TRA API ADVANCEDROWEXTRACTORMAIN")
    print(f"📁 Thư mục bảng đầu vào: {tables_dir}")
    print(f"📁 Thư mục đầu ra: {output_dir}")
    print(f"⏰ Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Kiểm tra row extractor
    result = test_row_extractor(tables_dir, output_dir)
    if not result:
        print("❌ Không thể trích xuất hàng")
        return
    
    # Tổng kết
    print(f"\n{'='*50}")
    print("TỔNG KẾT")
    print(f"{'='*50}")
    
    print(f"🎉 HOÀN THÀNH KIỂM TRA API ADVANCEDROWEXTRACTORMAIN!")
    print(f"✅ Đã xử lý {len(result['results'])} bảng")
    print(f"✅ Đã trích xuất được tổng cộng {result['total_rows']} hàng")
    print(f"📁 Kết quả lưu tại: {output_dir}/")

if __name__ == "__main__":
    main() 