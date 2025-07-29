#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tạo báo cáo tổng hợp cho tất cả các ảnh đã xử lý
===============================================

Script này tạo báo cáo tổng hợp HTML cho tất cả các ảnh đã xử lý.
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

def collect_reports(input_dir):
    """Thu thập tất cả các báo cáo từ thư mục đầu vào"""
    reports = []
    
    # Tìm file summary.json
    summary_path = os.path.join(input_dir, "summary.json")
    if os.path.exists(summary_path):
        with open(summary_path, "r", encoding="utf-8") as f:
            summary_data = json.load(f)
            if "results" in summary_data:
                return summary_data
    
    # Tìm các thư mục con
    for item in os.listdir(input_dir):
        item_path = os.path.join(input_dir, item)
        if os.path.isdir(item_path):
            # Tìm file report.json trong thư mục con
            report_path = os.path.join(item_path, "report.json")
            if os.path.exists(report_path):
                with open(report_path, "r", encoding="utf-8") as f:
                    report_data = json.load(f)
                    reports.append(report_data)
    
    # Tạo summary data
    summary_data = {
        "input_dir": input_dir,
        "output_dir": input_dir,
        "images": len(reports),
        "processed_images": len(reports),
        "results": reports,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return summary_data

def generate_summary_report(input_dir, output_file):
    """Tạo báo cáo tổng hợp HTML từ thư mục kết quả"""
    print(f"🔍 Đang phân tích thư mục kết quả: {input_dir}")
    
    # Thu thập báo cáo
    summary_data = collect_reports(input_dir)
    if not summary_data or not summary_data.get("results"):
        print(f"❌ Không tìm thấy báo cáo nào trong thư mục: {input_dir}")
        return False
    
    # Tạo nội dung HTML
    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Báo cáo tổng hợp trích xuất bảng, hàng và cột</title>
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
        .image-section {{
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
        .summary-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .summary-table th {{
            background-color: #3498db;
            color: white;
        }}
        .btn {{
            display: inline-block;
            padding: 8px 16px;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            margin: 5px 0;
        }}
        .btn:hover {{
            background-color: #2980b9;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Báo cáo tổng hợp trích xuất bảng, hàng và cột</h1>
            <p class="timestamp">Thời gian: {summary_data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}</p>
        </div>
        
        <div class="section">
            <h2>Thông tin tổng quan</h2>
            <table>
                <tr>
                    <th>Thư mục đầu vào</th>
                    <td>{summary_data.get("input_dir", "")}</td>
                </tr>
                <tr>
                    <th>Số lượng ảnh</th>
                    <td>{summary_data.get("images", 0)}</td>
                </tr>
                <tr>
                    <th>Số lượng ảnh đã xử lý</th>
                    <td>{summary_data.get("processed_images", 0)}</td>
                </tr>
            </table>
        </div>
        
        <div class="section">
            <h2>Bảng tổng hợp kết quả</h2>
            <table class="summary-table">
                <tr>
                    <th>STT</th>
                    <th>Ảnh</th>
                    <th>Số lượng bảng</th>
                    <th>Số lượng hàng</th>
                    <th>Số lượng cột</th>
                    <th>Số lượng nhóm cột gộp</th>
                    <th>Báo cáo chi tiết</th>
                </tr>
"""
    
    # Thêm dòng cho từng ảnh
    for i, result in enumerate(summary_data.get("results", [])):
        image_name = os.path.basename(result.get("image", f"image_{i+1}"))
        output_dir = result.get("output_dir", "")
        report_path = os.path.join(output_dir, "report.html")
        
        # Tính tổng số hàng
        total_rows = sum(len(rows.get("rows", [])) for rows in result.get("rows", []))
        
        # Tính tổng số cột
        total_columns = sum(len(cols.get("columns", [])) for cols in result.get("columns", []))
        
        # Tính tổng số nhóm cột gộp
        total_merged = sum(len(cols.get("merged_columns", [])) for cols in result.get("columns", []))
        
        html_content += f"""
                <tr>
                    <td>{i+1}</td>
                    <td>{image_name}</td>
                    <td>{len(result.get("tables", []))}</td>
                    <td>{total_rows}</td>
                    <td>{total_columns}</td>
                    <td>{total_merged}</td>
                    <td><a href="{os.path.basename(report_path)}" class="btn">Xem chi tiết</a></td>
                </tr>
"""
    
    html_content += """
            </table>
        </div>
        
        <div class="section">
            <h2>Chi tiết từng ảnh</h2>
"""
    
    # Thêm phần chi tiết cho từng ảnh
    for i, result in enumerate(summary_data.get("results", [])):
        image_name = os.path.basename(result.get("image", f"image_{i+1}"))
        output_dir = result.get("output_dir", "")
        
        # Đường dẫn ảnh
        original_path = os.path.join(output_dir, "original.jpg")
        detected_tables_path = os.path.join(output_dir, "detected_tables.jpg")
        
        html_content += f"""
            <div class="image-section">
                <h3>{i+1}. {image_name}</h3>
                
                <div class="grid">
                    <div class="grid-item">
                        <h4>Ảnh gốc</h4>
                        <img src="{image_to_base64(original_path)}" alt="Ảnh gốc">
                    </div>
                    
                    <div class="grid-item">
                        <h4>Bảng đã phát hiện</h4>
                        <img src="{image_to_base64(detected_tables_path)}" alt="Bảng đã phát hiện">
                    </div>
                </div>
                
                <h4>Thông tin chi tiết</h4>
                <table>
                    <tr>
                        <th>Số lượng bảng</th>
                        <td>{len(result.get("tables", []))}</td>
                    </tr>
                    <tr>
                        <th>Số lượng hàng</th>
                        <td>{sum(len(rows.get("rows", [])) for rows in result.get("rows", []))}</td>
                    </tr>
                    <tr>
                        <th>Số lượng cột riêng lẻ</th>
                        <td>{sum(len(cols.get("columns", [])) for cols in result.get("columns", []))}</td>
                    </tr>
                    <tr>
                        <th>Số lượng nhóm cột gộp</th>
                        <td>{sum(len(cols.get("merged_columns", [])) for cols in result.get("columns", []))}</td>
                    </tr>
                </table>
                
                <p><a href="{os.path.basename(os.path.join(output_dir, 'report.html'))}" class="btn">Xem báo cáo chi tiết</a></p>
            </div>
"""
    
    # Kết thúc HTML
    html_content += """
        </div>
    </div>
</body>
</html>
"""
    
    # Ghi file HTML
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✅ Đã tạo báo cáo tổng hợp HTML: {output_file}")
    return True

def main():
    """Hàm chính"""
    # Kiểm tra tham số dòng lệnh
    if len(sys.argv) < 2:
        print("Sử dụng: python generate_summary_report.py <thư_mục_kết_quả>")
        print("Hoặc:    python generate_summary_report.py <thư_mục_kết_quả> <file_html_đầu_ra>")
        return
    
    # Thư mục kết quả đầu vào
    input_dir = sys.argv[1]
    if not os.path.exists(input_dir):
        print(f"❌ Không tìm thấy thư mục: {input_dir}")
        return
    
    # File HTML đầu ra
    output_file = sys.argv[2] if len(sys.argv) > 2 else os.path.join(input_dir, "summary.html")
    
    print(f"🚀 TẠO BÁO CÁO TỔNG HỢP HTML")
    print(f"📁 Thư mục kết quả: {input_dir}")
    print(f"📄 File HTML đầu ra: {output_file}")
    print(f"⏰ Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Tạo báo cáo HTML
    if generate_summary_report(input_dir, output_file):
        print(f"\n{'='*50}")
        print("TỔNG KẾT")
        print(f"{'='*50}")
        
        print(f"🎉 HOÀN THÀNH TẠO BÁO CÁO TỔNG HỢP HTML!")
        print(f"✅ Đã tạo báo cáo tổng hợp HTML: {output_file}")
        print(f"👀 Mở file HTML để xem kết quả trực quan.")

if __name__ == "__main__":
    main() 