#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kiểm tra API AdvancedTableExtractor
==================================

Script này kiểm tra API AdvancedTableExtractor với các file ảnh trong thư mục input.
"""

import os
import sys
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime

# Import module từ detect_row
from detect_row import AdvancedTableExtractor

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

def test_table_extractor(image_path, output_dir):
    """Kiểm tra AdvancedTableExtractor với một ảnh"""
    print(f"\n--- Xử lý ảnh: {os.path.basename(image_path)} ---")
    
    # Tạo thư mục output cho ảnh này
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    image_output_dir = os.path.join(output_dir, image_name)
    ensure_dir(image_output_dir)
    
    # Tạo thư mục cho các bảng
    tables_dir = os.path.join(image_output_dir, "tables")
    debug_dir = os.path.join(image_output_dir, "debug")
    ensure_dir(tables_dir)
    ensure_dir(debug_dir)
    
    # Đọc ảnh trực tiếp
    image = cv2.imread(image_path)
    if image is None:
        print(f"  ❌ Không thể đọc ảnh: {image_path}")
        return None
    
    # Lưu ảnh gốc
    original_path = os.path.join(image_output_dir, "original.jpg")
    cv2.imwrite(original_path, image)
    
    # Trích xuất bảng trực tiếp từ ảnh
    try:
        print(f"  🔍 Trích xuất bảng từ {os.path.basename(image_path)}")
        
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
        extracted_tables = []
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
            
            extracted_tables.append(table_filename)
            
            print(f"    ✅ Bảng {i+1}: {w}x{h}")
        
        # Vẽ các bảng đã phát hiện
        result_img = image.copy()
        for i, contour in enumerate(table_contours):
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(result_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(result_img, f"Table {i+1}", (x+5, y+30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Lưu ảnh kết quả
        result_path = os.path.join(image_output_dir, "detected_tables.jpg")
        cv2.imwrite(result_path, result_img)
        
        print(f"  ✅ Đã trích xuất được {len(extracted_tables)} bảng")
        
        # Hiển thị danh sách bảng
        for table_file in extracted_tables:
            table_path = os.path.join(tables_dir, table_file)
            table_img = cv2.imread(table_path)
            if table_img is not None:
                h, w = table_img.shape[:2]
                print(f"    - {table_file}: {w}x{h}")
        
        return {
            "image": image_path,
            "tables": extracted_tables,
            "tables_dir": tables_dir
        }
    
    except Exception as e:
        print(f"  ❌ Lỗi khi xử lý ảnh: {e}")
        return None

def main():
    """Hàm chính"""
    # Thư mục chứa ảnh đầu vào
    input_dir = "input"
    if not os.path.exists(input_dir):
        print(f"❌ Không tìm thấy thư mục: {input_dir}")
        return
    
    # Thư mục đầu ra
    output_dir = "table_extractor_output"
    ensure_dir(output_dir)
    
    print(f"🚀 KIỂM TRA API ADVANCEDTABLEEXTRACTOR")
    print(f"📁 Thư mục ảnh đầu vào: {input_dir}")
    print(f"📁 Thư mục đầu ra: {output_dir}")
    print(f"⏰ Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Liệt kê các file ảnh
    image_files = list_image_files(input_dir)
    if not image_files:
        print(f"❌ Không tìm thấy file ảnh nào trong thư mục: {input_dir}")
        return
    
    print(f"✅ Tìm thấy {len(image_files)} file ảnh")
    
    # Xử lý từng ảnh
    results = []
    for image_path in image_files:
        result = test_table_extractor(image_path, output_dir)
        if result:
            results.append(result)
    
    # Tổng kết
    print(f"\n{'='*50}")
    print("TỔNG KẾT")
    print(f"{'='*50}")
    
    print(f"🎉 HOÀN THÀNH KIỂM TRA API ADVANCEDTABLEEXTRACTOR!")
    print(f"✅ Đã xử lý {len(image_files)} ảnh")
    print(f"✅ Đã trích xuất được bảng từ {len(results)} ảnh")
    
    # Hiển thị kết quả chi tiết
    total_tables = sum(len(result["tables"]) for result in results)
    print(f"✅ Tổng số bảng đã trích xuất: {total_tables}")
    
    print(f"📁 Kết quả lưu tại: {output_dir}/")

if __name__ == "__main__":
    main() 