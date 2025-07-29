#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tạo báo cáo HTML hiển thị kết quả trích xuất
============================================

Script này tạo báo cáo HTML hiển thị kết quả trích xuất từ quy trình hoàn chỉnh.
"""

import os
import sys
import json
import base64
from datetime import datetime
from pathlib import Path

def ensure_dir(path):
    """Tạo thư mục nếu chưa tồn tại"""
    os.makedirs(path, exist_ok=True)
    print(f"📁 Đã tạo thư mục: {path}")

def image_to_base64(image_path):
    """Chuyển đổi ảnh thành chuỗi base64"""
    if not os.path.exists(image_path):
        return ""
    
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    
    ext = os.path.splitext(image_path)[1].lower()
    if ext in [".jpg", ".jpeg"]:
        mime_type = "image/jpeg"
    elif ext == ".png":
        mime_type = "image/png"
    elif ext == ".gif":
        mime_type = "image/gif"
    else:
        mime_type = "image/jpeg"
    
    return f"data:{mime_type};base64,{encoded_string}"

def generate_html_report(input_dir, output_file):
    """Tạo báo cáo HTML từ thư mục kết quả"""
    print(f"🔍 Đang phân tích thư mục kết quả: {input_dir}")
    
    # Tìm file report.json
    report_path = os.path.join(input_dir, "report.json")
    if not os.path.exists(report_path):
        print(f"❌ Không tìm thấy file báo cáo: {report_path}")
        return False
    
    # Đọc file báo cáo
    with open(report_path, "r", encoding="utf-8") as f:
        report_data = json.load(f)
    
    # Tạo nội dung HTML
    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Báo cáo trích xuất bảng, hàng và cột</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1, h2, h3, h4 {{
            color: #2c3e50;
        }}
        .header {{
            background-color: #3498db;
            color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
        }}
        .section {{
            margin-bottom: 30px;
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .table-section {{
            margin-bottom: 40px;
            border-left: 5px solid #3498db;
            padding-left: 15px;
        }}
        .image-container {{
            margin: 20px 0;
            text-align: center;
        }}
        .image-container img {{
            max-width: 100%;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .grid-item {{
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            background-color: white;
        }}
        .grid-item h4 {{
            margin-top: 0;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        table, th, td {{
            border: 1px solid #ddd;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .info {{
            background-color: #d4edda;
            color: #155724;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .timestamp {{
            color: #6c757d;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Báo cáo trích xuất bảng, hàng và cột</h1>
            <p class="timestamp">Thời gian: {report_data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}</p>
        </div>
        
        <div class="section">
            <h2>Thông tin tổng quan</h2>
            <table>
                <tr>
                    <th>Ảnh gốc</th>
                    <td>{os.path.basename(report_data.get("image", ""))}</td>
                </tr>
                <tr>
                    <th>Số lượng bảng</th>
                    <td>{len(report_data.get("tables", []))}</td>
                </tr>
                <tr>
                    <th>Số lượng hàng</th>
                    <td>{sum(len(rows.get("rows", [])) for rows in report_data.get("rows", []))}</td>
                </tr>
                <tr>
                    <th>Số lượng cột riêng lẻ</th>
                    <td>{sum(len(cols.get("columns", [])) for cols in report_data.get("columns", []))}</td>
                </tr>
                <tr>
                    <th>Số lượng nhóm cột gộp</th>
                    <td>{sum(len(cols.get("merged_columns", [])) for cols in report_data.get("columns", []))}</td>
                </tr>
            </table>
            
            <div class="image-container">
                <h3>Ảnh gốc</h3>
                <img src="{image_to_base64(os.path.join(input_dir, 'original.jpg'))}" alt="Ảnh gốc">
            </div>
            
            <div class="image-container">
                <h3>Bảng đã phát hiện</h3>
                <img src="{image_to_base64(os.path.join(input_dir, 'detected_tables.jpg'))}" alt="Bảng đã phát hiện">
            </div>
        </div>
"""
    
    # Thêm phần chi tiết cho từng bảng
    for i, table in enumerate(report_data.get("tables", [])):
        table_id = table.get("id", i+1)
        table_path = table.get("path", "")
        
        # Tìm thông tin hàng và cột tương ứng
        rows_info = next((rows for rows in report_data.get("rows", []) if os.path.basename(rows.get("table", "")) == os.path.basename(table_path)), {})
        columns_info = next((cols for cols in report_data.get("columns", []) if os.path.basename(cols.get("table", "")) == os.path.basename(table_path)), {})
        
        rows = rows_info.get("rows", [])
        columns = columns_info.get("columns", [])
        merged_columns = columns_info.get("merged_columns", [])
        
        html_content += f"""
        <div class="table-section">
            <h2>Bảng {table_id}</h2>
            
            <div class="image-container">
                <h3>Ảnh bảng</h3>
                <img src="{image_to_base64(table_path)}" alt="Bảng {table_id}">
            </div>
            
            <h3>Thông tin chi tiết</h3>
            <table>
                <tr>
                    <th>Kích thước</th>
                    <td>{table.get("width", 0)}x{table.get("height", 0)}</td>
                </tr>
                <tr>
                    <th>Số lượng hàng</th>
                    <td>{len(rows)}</td>
                </tr>
                <tr>
                    <th>Số lượng cột</th>
                    <td>{len(columns)}</td>
                </tr>
                <tr>
                    <th>Số lượng nhóm cột gộp</th>
                    <td>{len(merged_columns)}</td>
                </tr>
            </table>
            
            <h3>Hàng đã trích xuất</h3>
"""
        
        # Hiển thị các hàng
        if rows:
            html_content += """
            <div class="grid">
"""
            
            for row in rows:
                row_id = row.get("id", 0)
                row_path = row.get("path", "")
                
                html_content += f"""
                <div class="grid-item">
                    <h4>Hàng {row_id}</h4>
                    <img src="{image_to_base64(row_path)}" alt="Hàng {row_id}">
                    <p>Kích thước: {row.get("width", 0)}x{row.get("height", 0)}</p>
                </div>
"""
            
            html_content += """
            </div>
"""
        else:
            html_content += """
            <div class="info">Không có hàng nào được trích xuất.</div>
"""
        
        # Hiển thị các cột riêng lẻ
        html_content += """
            <h3>Cột đã trích xuất</h3>
"""
        
        if columns:
            html_content += """
            <div class="grid">
"""
            
            for column in columns:
                col_id = column.get("id", 0)
                col_path = column.get("path", "")
                
                html_content += f"""
                <div class="grid-item">
                    <h4>Cột {col_id}</h4>
                    <img src="{image_to_base64(col_path)}" alt="Cột {col_id}">
                    <p>Kích thước: {column.get("width", 0)}x{column.get("height", 0)}</p>
                </div>
"""
            
            html_content += """
            </div>
"""
        else:
            html_content += """
            <div class="info">Không có cột nào được trích xuất.</div>
"""
        
        # Hiển thị các nhóm cột gộp
        html_content += """
            <h3>Nhóm cột gộp</h3>
"""
        
        if merged_columns:
            html_content += """
            <div class="grid">
"""
            
            for merged in merged_columns:
                name = merged.get("name", "")
                merged_path = merged.get("path", "")
                
                html_content += f"""
                <div class="grid-item">
                    <h4>Nhóm '{name}'</h4>
                    <img src="{image_to_base64(merged_path)}" alt="Nhóm {name}">
                    <p>Kích thước: {merged.get("width", 0)}x{merged.get("height", 0)}</p>
                    <p>Cột: {', '.join(map(str, merged.get("columns", [])))}</p>
                </div>
"""
            
            html_content += """
            </div>
"""
        else:
            html_content += """
            <div class="info">Không có nhóm cột gộp nào được tạo.</div>
"""
        
        html_content += """
        </div>
"""
    
    # Kết thúc HTML
    html_content += """
    </div>
</body>
</html>
"""
    
    # Ghi file HTML
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✅ Đã tạo báo cáo HTML: {output_file}")
    return True

def main():
    """Hàm chính"""
    # Kiểm tra tham số dòng lệnh
    if len(sys.argv) < 2:
        print("Sử dụng: python generate_html_report.py <thư_mục_kết_quả>")
        print("Hoặc:    python generate_html_report.py <thư_mục_kết_quả> <file_html_đầu_ra>")
        return
    
    # Thư mục kết quả đầu vào
    input_dir = sys.argv[1]
    if not os.path.exists(input_dir):
        print(f"❌ Không tìm thấy thư mục: {input_dir}")
        return
    
    # File HTML đầu ra
    output_file = sys.argv[2] if len(sys.argv) > 2 else os.path.join(input_dir, "report.html")
    
    print(f"🚀 TẠO BÁO CÁO HTML")
    print(f"📁 Thư mục kết quả: {input_dir}")
    print(f"📄 File HTML đầu ra: {output_file}")
    print(f"⏰ Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Tạo báo cáo HTML
    if generate_html_report(input_dir, output_file):
        print(f"\n{'='*50}")
        print("TỔNG KẾT")
        print(f"{'='*50}")
        
        print(f"🎉 HOÀN THÀNH TẠO BÁO CÁO HTML!")
        print(f"✅ Đã tạo báo cáo HTML: {output_file}")
        print(f"👀 Mở file HTML để xem kết quả trực quan.")

if __name__ == "__main__":
    main() 