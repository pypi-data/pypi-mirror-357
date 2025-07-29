#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quy trình trích xuất bảng, hàng và cột hoàn chỉnh
================================================

Script này kết hợp cả ba bước (trích xuất bảng, hàng và cột) thành một quy trình hoàn chỉnh.
"""

import os
import sys
import cv2
import numpy as np
import json
from pathlib import Path
from datetime import datetime

def ensure_dir(path):
    """Tạo thư mục nếu chưa tồn tại"""
    os.makedirs(path, exist_ok=True)
    print(f"[DIR] Da tao thu muc: {path}")

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

def extract_tables(image_path, output_dir):
    """Trích xuất bảng từ ảnh"""
    print(f"\n--- Trích xuất bảng từ ảnh: {os.path.basename(image_path)} ---")
    
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
            
            extracted_tables.append({
                "id": i+1,
                "filename": table_filename,
                "path": table_path,
                "width": w,
                "height": h
            })
            
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
        
        return {
            "image": image_path,
            "tables": extracted_tables,
            "tables_dir": tables_dir,
            "output_dir": image_output_dir
        }
    
    except Exception as e:
        print(f"  ❌ Lỗi khi xử lý ảnh: {e}")
        return None

def extract_rows(table_path, output_dir):
    """Trích xuất hàng từ bảng"""
    print(f"  🔍 Trích xuất hàng từ bảng: {os.path.basename(table_path)}")
    
    try:
        # Đọc ảnh bảng
        table_img = cv2.imread(table_path)
        if table_img is None:
            print(f"    ❌ Không thể đọc ảnh bảng: {table_path}")
            return None
        
        # Tạo thư mục cho hàng của bảng này
        table_name = os.path.basename(table_path)
        table_rows_dir = os.path.join(output_dir, os.path.splitext(table_name)[0])
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
            
            h, w = row_img.shape[:2]
            
            extracted_rows.append({
                "id": i+1,
                "filename": row_filename,
                "path": row_path,
                "width": w,
                "height": h,
                "y1": y1,
                "y2": y2
            })
            
            print(f"      ✅ Hàng {i+1}: {w}x{h}")
        
        # Vẽ các hàng đã phát hiện
        result_img = table_img.copy()
        for i in range(len(h_lines) - 1):
            y1, y2 = h_lines[i], h_lines[i+1]
            cv2.rectangle(result_img, (0, y1), (table_img.shape[1], y2), (0, 255, 0), 2)
            cv2.putText(result_img, f"Row {i+1}", (10, y1+20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Lưu ảnh kết quả
        result_path = os.path.join(os.path.dirname(output_dir), "debug", f"{os.path.splitext(table_name)[0]}_rows.jpg")
        cv2.imwrite(result_path, result_img)
        
        print(f"    ✅ Đã trích xuất được {len(extracted_rows)} hàng")
        
        return {
            "table": table_path,
            "rows": extracted_rows,
            "rows_dir": table_rows_dir
        }
    
    except Exception as e:
        print(f"    ❌ Lỗi khi xử lý bảng: {e}")
        return None

def detect_vertical_lines(binary_image, min_line_length_ratio=0.4):
    """Phát hiện đường kẻ dọc trong ảnh nhị phân"""
    height, width = binary_image.shape
    min_line_length = int(height * min_line_length_ratio)
    
    # Tính histogram theo chiều ngang
    histogram = np.sum(binary_image, axis=0)
    
    # Lọc các đỉnh trong histogram
    threshold_value = np.max(histogram) * 0.4
    peaks = []
    
    for i in range(1, width - 1):
        if histogram[i] > threshold_value and histogram[i] >= histogram[i-1] and histogram[i] >= histogram[i+1]:
            peaks.append((i, histogram[i]))
    
    # Sắp xếp các đỉnh theo vị trí
    peaks.sort(key=lambda x: x[0])
    
    # Lấy vị trí các đỉnh
    positions = [0] + [peak[0] for peak in peaks] + [width]
    
    # Lọc các vị trí quá gần nhau
    min_distance = width * 0.02  # Khoảng cách tối thiểu giữa các đường kẻ
    filtered_positions = [positions[0]]
    
    for i in range(1, len(positions)):
        if positions[i] - filtered_positions[-1] >= min_distance:
            filtered_positions.append(positions[i])
    
    return filtered_positions

def extract_columns(table_path, output_dir, column_groups=None):
    """Trích xuất cột từ bảng"""
    print(f"  🔍 Trích xuất cột từ bảng: {os.path.basename(table_path)}")
    
    try:
        # Đọc ảnh bảng
        table_img = cv2.imread(table_path)
        if table_img is None:
            print(f"    ❌ Không thể đọc ảnh bảng: {table_path}")
            return None
        
        # Tạo thư mục cho cột của bảng này
        table_name = os.path.basename(table_path)
        table_columns_dir = os.path.join(output_dir, "individual_columns", os.path.splitext(table_name)[0])
        table_merged_dir = os.path.join(output_dir, "merged_columns", os.path.splitext(table_name)[0])
        ensure_dir(table_columns_dir)
        ensure_dir(table_merged_dir)
        
        # Nếu không có column_groups, tạo một cấu hình mặc định
        if column_groups is None:
            column_groups = {
                "first_two": [1, 2],
                "middle": [3, 4],
                "first_three": [1, 2, 3],
                "all": [1, 2, 3, 4, 5]
            }
        
        # Phát hiện đường kẻ dọc
        gray = cv2.cvtColor(table_img, cv2.COLOR_BGR2GRAY)
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY_INV, 15, 3)
        
        v_lines = detect_vertical_lines(binary, min_line_length_ratio=0.4)
        print(f"    ✅ Phát hiện {len(v_lines)} đường kẻ dọc")
        
        # Vẽ đường kẻ dọc
        h, w = table_img.shape[:2]
        lines_img = table_img.copy()
        for x in v_lines:
            cv2.line(lines_img, (x, 0), (x, h), (0, 0, 255), 2)
        
        # Lưu ảnh đường kẻ dọc
        lines_path = os.path.join(os.path.dirname(os.path.dirname(output_dir)), "debug", f"{os.path.splitext(table_name)[0]}_vertical_lines.jpg")
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
        
        # Vẽ các cột đã gộp
        result_img = table_img.copy()
        for merged in merged_columns:
            x1, x2 = merged["x1"], merged["x2"]
            name = merged["name"]
            cv2.rectangle(result_img, (x1, 0), (x2, h), (0, 255, 0), 2)
            cv2.putText(result_img, name, (x1+5, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Lưu ảnh kết quả
        result_path = os.path.join(os.path.dirname(os.path.dirname(output_dir)), "debug", f"{os.path.splitext(table_name)[0]}_merged_columns.jpg")
        cv2.imwrite(result_path, result_img)
        
        return {
            "table": table_path,
            "columns": columns,
            "merged_columns": merged_columns,
            "columns_dir": table_columns_dir,
            "merged_dir": table_merged_dir
        }
    
    except Exception as e:
        print(f"    ❌ Lỗi khi xử lý bảng: {e}")
        return None

def process_image(image_path, output_dir, column_groups=None):
    """Xử lý một ảnh: trích xuất bảng, hàng và cột"""
    # Trích xuất bảng
    tables_result = extract_tables(image_path, output_dir)
    if not tables_result:
        print(f"❌ Không thể trích xuất bảng từ ảnh: {image_path}")
        return None
    
    # Tạo thư mục cho hàng và cột
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    image_output_dir = os.path.join(output_dir, image_name)
    
    rows_dir = os.path.join(image_output_dir, "rows")
    columns_dir = os.path.join(image_output_dir, "columns")
    
    ensure_dir(rows_dir)
    ensure_dir(columns_dir)
    ensure_dir(os.path.join(columns_dir, "individual_columns"))
    ensure_dir(os.path.join(columns_dir, "merged_columns"))
    
    # Xử lý từng bảng
    tables = tables_result["tables"]
    tables_dir = tables_result["tables_dir"]
    
    rows_results = []
    columns_results = []
    
    for table in tables:
        print(f"\n--- Xử lý bảng {table['id']} ---")
        
        # Trích xuất hàng
        rows_result = extract_rows(table["path"], rows_dir)
        if rows_result:
            rows_results.append(rows_result)
        
        # Trích xuất cột
        columns_result = extract_columns(table["path"], columns_dir, column_groups)
        if columns_result:
            columns_results.append(columns_result)
    
    # Tạo báo cáo tổng hợp
    report = {
        "image": image_path,
        "output_dir": image_output_dir,
        "tables": tables,
        "rows": rows_results,
        "columns": columns_results,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Lưu báo cáo
    report_path = os.path.join(image_output_dir, "report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    
    return report

def main():
    """Hàm chính"""
    # Kiểm tra tham số dòng lệnh
    if len(sys.argv) < 2:
        print("Sử dụng: python test_complete_workflow.py <đường_dẫn_ảnh>")
        print("Hoặc:    python test_complete_workflow.py <thư_mục_chứa_ảnh>")
        return
    
    # Đường dẫn đầu vào
    input_path = sys.argv[1]
    
    # Thư mục đầu ra
    output_dir = "complete_workflow_output"
    ensure_dir(output_dir)
    ensure_dir(os.path.join(output_dir, "debug"))
    
    # Định nghĩa nhóm cột
    column_groups = {
        "info": [1, 2],           # Cột thông tin
        "result": [3, 4],         # Cột kết quả
        "info_result": [1, 2, 3], # Cột thông tin và kết quả đầu
        "all_data": [1, 2, 3, 4]  # Tất cả dữ liệu
    }
    
    print(f"🚀 QUY TRÌNH TRÍCH XUẤT BẢNG, HÀNG VÀ CỘT")
    print(f"📁 Đường dẫn đầu vào: {input_path}")
    print(f"📁 Thư mục đầu ra: {output_dir}")
    print(f"⏰ Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Xử lý đầu vào
    if os.path.isdir(input_path):
        # Xử lý thư mục
        image_files = list_image_files(input_path)
        if not image_files:
            print(f"❌ Không tìm thấy file ảnh nào trong thư mục: {input_path}")
            return
        
        print(f"✅ Tìm thấy {len(image_files)} file ảnh")
        
        # Xử lý từng ảnh
        results = []
        for image_path in image_files:
            result = process_image(image_path, output_dir, column_groups)
            if result:
                results.append(result)
        
        # Tổng kết
        print(f"\n{'='*50}")
        print("TỔNG KẾT")
        print(f"{'='*50}")
        
        print(f"🎉 HOÀN THÀNH QUY TRÌNH TRÍCH XUẤT!")
        print(f"✅ Đã xử lý {len(image_files)} ảnh")
        print(f"✅ Đã trích xuất được bảng từ {len(results)} ảnh")
        
        # Lưu báo cáo tổng hợp
        summary = {
            "input_dir": input_path,
            "output_dir": output_dir,
            "images": len(image_files),
            "processed_images": len(results),
            "results": results,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        summary_path = os.path.join(output_dir, "summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"📁 Kết quả lưu tại: {output_dir}/")
    
    else:
        # Xử lý file ảnh đơn lẻ
        if not os.path.isfile(input_path):
            print(f"❌ Không tìm thấy file: {input_path}")
            return
        
        # Xử lý ảnh
        result = process_image(input_path, output_dir, column_groups)
        
        if result:
            print(f"\n{'='*50}")
            print("TỔNG KẾT")
            print(f"{'='*50}")
            
            print(f"🎉 HOÀN THÀNH QUY TRÌNH TRÍCH XUẤT!")
            print(f"✅ Đã xử lý ảnh: {input_path}")
            print(f"✅ Đã trích xuất được {len(result['tables'])} bảng")
            
            total_rows = sum(len(rows["rows"]) for rows in result["rows"]) if "rows" in result else 0
            print(f"✅ Đã trích xuất được {total_rows} hàng")
            
            total_columns = sum(len(cols["columns"]) for cols in result["columns"]) if "columns" in result else 0
            print(f"✅ Đã trích xuất được {total_columns} cột riêng lẻ")
            
            total_merged = sum(len(cols["merged_columns"]) for cols in result["columns"]) if "columns" in result else 0
            print(f"✅ Đã tạo được {total_merged} nhóm cột gộp")
            
            print(f"📁 Kết quả lưu tại: {output_dir}/")

if __name__ == "__main__":
    main() 