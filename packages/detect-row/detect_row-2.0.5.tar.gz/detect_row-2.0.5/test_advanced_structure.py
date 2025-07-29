#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phân tích cấu trúc bảng nâng cao - DetectRow
===========================================

Script này tập trung vào phân tích cấu trúc bảng nâng cao:
1. Phát hiện header và footer
2. Phân tích cấu trúc hàng và cột
3. Tạo visualization chi tiết
"""

import os
import sys
import cv2
import numpy as np
from pathlib import Path
import json
from datetime import datetime

# Import các module từ detect_row
from detect_row import (
    AdvancedTableExtractor,
    AdvancedRowExtractorMain,
    AdvancedColumnExtractor
)

def ensure_dir(path):
    """Tạo thư mục nếu chưa tồn tại"""
    os.makedirs(path, exist_ok=True)
    print(f"📁 Đã tạo thư mục: {path}")

def preprocess_image(image):
    """Tiền xử lý ảnh"""
    # Chuyển sang ảnh xám
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Khử nhiễu
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Nhị phân hóa
    _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    return gray, binary

def detect_table_lines(binary, image):
    """Phát hiện đường kẻ ngang và dọc trong bảng"""
    # Phát hiện đường kẻ ngang
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    
    # Phát hiện đường kẻ dọc
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    
    # Kết hợp đường kẻ ngang và dọc
    table_lines = cv2.add(horizontal_lines, vertical_lines)
    
    # Tìm contours
    contours, _ = cv2.findContours(table_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Vẽ contours
    visualization = image.copy()
    cv2.drawContours(visualization, contours, -1, (0, 255, 0), 2)
    
    # Tìm đường kẻ ngang
    h_lines = []
    contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > image.shape[1] * 0.5:  # Chỉ lấy đường kẻ ngang đủ dài
            h_lines.append(y + h//2)
            cv2.line(visualization, (0, y + h//2), (image.shape[1], y + h//2), (0, 0, 255), 2)
    
    # Tìm đường kẻ dọc
    v_lines = []
    contours, _ = cv2.findContours(vertical_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if h > image.shape[0] * 0.5:  # Chỉ lấy đường kẻ dọc đủ dài
            v_lines.append(x + w//2)
            cv2.line(visualization, (x + w//2, 0), (x + w//2, image.shape[0]), (255, 0, 0), 2)
    
    # Sắp xếp các đường kẻ
    h_lines.sort()
    v_lines.sort()
    
    return {
        "horizontal_lines": h_lines,
        "vertical_lines": v_lines,
        "visualization": visualization
    }

def detect_header_footer(image, h_lines, v_lines):
    """Phát hiện header và footer của bảng"""
    h, w = image.shape[:2]
    
    # Phát hiện header (dòng đầu tiên)
    header_y1 = 0
    header_y2 = h_lines[0] if h_lines else h // 10
    
    # Phát hiện footer (dòng cuối cùng)
    footer_y1 = h_lines[-1] if h_lines else h * 9 // 10
    footer_y2 = h
    
    # Cắt header và footer
    header_img = image[header_y1:header_y2, :]
    footer_img = image[footer_y1:footer_y2, :]
    
    # Tạo visualization
    visualization = image.copy()
    
    # Vẽ header
    cv2.rectangle(visualization, (0, header_y1), (w, header_y2), (0, 255, 0), 2)
    cv2.putText(visualization, "HEADER", (10, header_y1 + 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Vẽ footer
    cv2.rectangle(visualization, (0, footer_y1), (w, footer_y2), (0, 0, 255), 2)
    cv2.putText(visualization, "FOOTER", (10, footer_y1 + 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    return {
        "header": {
            "y1": header_y1,
            "y2": header_y2,
            "image": header_img
        },
        "footer": {
            "y1": footer_y1,
            "y2": footer_y2,
            "image": footer_img
        },
        "visualization": visualization
    }

def analyze_table_cells(image, h_lines, v_lines):
    """Phân tích các ô trong bảng"""
    # Thêm các đường biên
    h_lines = [0] + h_lines + [image.shape[0]]
    v_lines = [0] + v_lines + [image.shape[1]]
    
    # Tạo visualization
    visualization = image.copy()
    
    # Phân tích các ô
    cells = []
    
    for i in range(len(h_lines) - 1):
        row_cells = []
        for j in range(len(v_lines) - 1):
            # Tọa độ của ô
            x1, y1 = v_lines[j], h_lines[i]
            x2, y2 = v_lines[j+1], h_lines[i+1]
            
            # Cắt ô
            cell_img = image[y1:y2, x1:x2]
            
            # Thêm ô vào danh sách
            cell = {
                "row": i,
                "col": j,
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "width": x2 - x1,
                "height": y2 - y1,
                "image": cell_img
            }
            row_cells.append(cell)
            
            # Vẽ ô
            cv2.rectangle(visualization, (x1, y1), (x2, y2), (0, 255, 0), 1)
            cv2.putText(visualization, f"{i},{j}", (x1 + 5, y1 + 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        cells.append(row_cells)
    
    return {
        "cells": cells,
        "rows": len(cells),
        "cols": len(cells[0]) if cells else 0,
        "visualization": visualization
    }

def analyze_table_structure(image_path, output_dir):
    """Phân tích cấu trúc bảng"""
    print(f"\n🔍 PHÂN TÍCH CẤU TRÚC BẢNG NÂNG CAO")
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
    
    # Tiền xử lý ảnh
    gray, binary = preprocess_image(image)
    
    # Lưu ảnh nhị phân
    binary_path = os.path.join(output_dir, "binary.jpg")
    cv2.imwrite(binary_path, binary)
    
    # Phát hiện đường kẻ
    lines_result = detect_table_lines(binary, image)
    h_lines = lines_result["horizontal_lines"]
    v_lines = lines_result["vertical_lines"]
    
    # Lưu visualization đường kẻ
    lines_path = os.path.join(output_dir, "table_lines.jpg")
    cv2.imwrite(lines_path, lines_result["visualization"])
    
    print(f"✅ Phát hiện {len(h_lines)} đường kẻ ngang")
    print(f"✅ Phát hiện {len(v_lines)} đường kẻ dọc")
    
    # Phát hiện header và footer
    header_footer_result = detect_header_footer(image, h_lines, v_lines)
    
    # Lưu visualization header và footer
    header_footer_path = os.path.join(output_dir, "header_footer.jpg")
    cv2.imwrite(header_footer_path, header_footer_result["visualization"])
    
    # Lưu header và footer
    header_path = os.path.join(output_dir, "header.jpg")
    footer_path = os.path.join(output_dir, "footer.jpg")
    cv2.imwrite(header_path, header_footer_result["header"]["image"])
    cv2.imwrite(footer_path, header_footer_result["footer"]["image"])
    
    print(f"✅ Phát hiện header: {header_footer_result['header']['y1']} - {header_footer_result['header']['y2']}")
    print(f"✅ Phát hiện footer: {header_footer_result['footer']['y1']} - {header_footer_result['footer']['y2']}")
    
    # Phân tích các ô
    cells_result = analyze_table_cells(image, h_lines, v_lines)
    
    # Lưu visualization các ô
    cells_path = os.path.join(output_dir, "table_cells.jpg")
    cv2.imwrite(cells_path, cells_result["visualization"])
    
    print(f"✅ Phân tích {cells_result['rows']} hàng x {cells_result['cols']} cột = {cells_result['rows'] * cells_result['cols']} ô")
    
    # Tạo thư mục để lưu các ô
    cells_dir = os.path.join(output_dir, "cells")
    ensure_dir(cells_dir)
    
    # Lưu các ô
    for i, row in enumerate(cells_result["cells"]):
        for j, cell in enumerate(row):
            cell_path = os.path.join(cells_dir, f"cell_{i}_{j}.jpg")
            cv2.imwrite(cell_path, cell["image"])
    
    # Tạo kết quả
    result = {
        "image_path": image_path,
        "output_dir": output_dir,
        "horizontal_lines": h_lines,
        "vertical_lines": v_lines,
        "header": header_footer_result["header"],
        "footer": header_footer_result["footer"],
        "cells": cells_result["cells"],
        "rows": cells_result["rows"],
        "cols": cells_result["cols"]
    }
    
    # Lưu kết quả dưới dạng JSON
    result_path = os.path.join(output_dir, "structure_analysis.json")
    with open(result_path, "w", encoding="utf-8") as f:
        # Chỉ lưu thông tin cần thiết, không lưu ảnh
        result_json = {
            "image_path": image_path,
            "output_dir": output_dir,
            "horizontal_lines": h_lines,
            "vertical_lines": v_lines,
            "header": {
                "y1": header_footer_result["header"]["y1"],
                "y2": header_footer_result["header"]["y2"]
            },
            "footer": {
                "y1": header_footer_result["footer"]["y1"],
                "y2": header_footer_result["footer"]["y2"]
            },
            "rows": cells_result["rows"],
            "cols": cells_result["cols"]
        }
        json.dump(result_json, f, indent=2)
    
    print(f"💾 Đã lưu kết quả phân tích: {result_path}")
    
    return result

def analyze_with_advanced_api(image_path, output_dir):
    """Phân tích bảng sử dụng API nâng cao"""
    print(f"\n🔍 PHÂN TÍCH BẢNG VỚI API NÂNG CAO")
    print("=" * 50)
    
    # Tạo thư mục output
    ensure_dir(output_dir)
    api_output_dir = os.path.join(output_dir, "api_results")
    ensure_dir(api_output_dir)
    
    # Đọc ảnh
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Không thể đọc ảnh: {image_path}")
        return None
    
    # Sử dụng AdvancedTableExtractor
    table_extractor = AdvancedTableExtractor(
        input_dir=os.path.dirname(image_path),
        output_dir=os.path.join(api_output_dir, "tables"),
        debug_dir=os.path.join(api_output_dir, "debug")
    )
    
    # Trích xuất bảng
    print("\n1. Trích xuất bảng")
    tables = table_extractor.process_image(os.path.basename(image_path), margin=5, check_text=True)
    
    # Tìm các bảng đã trích xuất
    tables_dir = os.path.join(api_output_dir, "tables")
    table_files = []
    
    if os.path.exists(tables_dir):
        table_files = [f for f in os.listdir(tables_dir) if f.endswith('.jpg')]
        table_files.sort()
    
    print(f"✅ Trích xuất được {len(table_files)} bảng")
    
    # Sử dụng AdvancedRowExtractorMain
    row_extractor = AdvancedRowExtractorMain(
        input_dir=tables_dir,
        output_dir=os.path.join(api_output_dir, "rows"),
        debug_dir=os.path.join(api_output_dir, "debug")
    )
    
    # Trích xuất hàng
    print("\n2. Trích xuất hàng")
    for table_file in table_files:
        print(f"  🔍 Xử lý bảng: {table_file}")
        rows = row_extractor.process_image(table_file)
        print(f"  ✅ Trích xuất được {len(rows) if rows else 0} hàng")
    
    # Sử dụng AdvancedColumnExtractor
    column_extractor = AdvancedColumnExtractor(
        input_dir=tables_dir,
        output_dir=os.path.join(api_output_dir, "columns"),
        debug_dir=os.path.join(api_output_dir, "debug")
    )
    
    # Trích xuất cột
    print("\n3. Trích xuất cột")
    for table_file in table_files:
        print(f"  🔍 Xử lý bảng: {table_file}")
        
        # Đọc ảnh bảng
        table_path = os.path.join(tables_dir, table_file)
        table_image = cv2.imread(table_path)
        
        if table_image is None:
            print(f"  ❌ Không thể đọc {table_path}")
            continue
        
        # Phát hiện đường kẻ dọc
        gray = cv2.cvtColor(table_image, cv2.COLOR_BGR2GRAY)
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY_INV, 15, 3)
        
        v_lines = column_extractor.detect_vertical_lines(binary, min_line_length_ratio=0.4)
        print(f"  ✅ Phát hiện {len(v_lines)} đường kẻ dọc")
        
        # Trích xuất cột
        columns = column_extractor.extract_columns(table_image, v_lines)
        print(f"  ✅ Trích xuất được {len(columns) if columns else 0} cột")
    
    return {
        "tables": table_files,
        "tables_dir": tables_dir,
        "rows_dir": os.path.join(api_output_dir, "rows"),
        "columns_dir": os.path.join(api_output_dir, "columns")
    }

def main():
    """Hàm chính"""
    # Kiểm tra tham số dòng lệnh
    if len(sys.argv) < 2:
        print("Sử dụng: python test_advanced_structure.py <đường_dẫn_ảnh>")
        return
    
    # Lấy đường dẫn ảnh từ tham số dòng lệnh
    image_path = sys.argv[1]
    output_dir = "advanced_structure_output"
    
    print(f"🚀 PHÂN TÍCH CẤU TRÚC BẢNG NÂNG CAO")
    print(f"📸 Ảnh đầu vào: {image_path}")
    print(f"📁 Thư mục đầu ra: {output_dir}")
    print(f"⏰ Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Kiểm tra file
    if not os.path.exists(image_path):
        print(f"❌ Không tìm thấy file: {image_path}")
        return
    
    # Tạo thư mục output
    ensure_dir(output_dir)
    
    # Phân tích cấu trúc bảng
    structure_dir = os.path.join(output_dir, "structure")
    ensure_dir(structure_dir)
    
    structure_result = analyze_table_structure(image_path, structure_dir)
    
    # Phân tích bảng với API nâng cao
    api_dir = os.path.join(output_dir, "api")
    ensure_dir(api_dir)
    
    api_result = analyze_with_advanced_api(image_path, api_dir)
    
    # Tổng kết
    print(f"\n{'='*50}")
    print("TỔNG KẾT")
    print(f"{'='*50}")
    
    print(f"🎉 HOÀN THÀNH PHÂN TÍCH CẤU TRÚC BẢNG NÂNG CAO!")
    print(f"✅ Đã phân tích cấu trúc bảng")
    print(f"✅ Đã trích xuất {len(api_result['tables'])} bảng")
    print(f"📁 Kết quả lưu tại: {output_dir}/")

if __name__ == "__main__":
    main() 