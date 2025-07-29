#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Xử lý nhiều ảnh cùng lúc và tạo báo cáo tổng hợp
=============================================

Script này xử lý nhiều ảnh cùng lúc, trích xuất bảng, hàng và cột, sau đó tạo báo cáo tổng hợp.
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

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

def process_image(image_path, output_dir):
    """Xử lý một ảnh bằng cách gọi script test_complete_workflow.py"""
    print(f"\n--- Xử lý ảnh: {os.path.basename(image_path)} ---")
    
    try:
        # Gọi script test_complete_workflow.py
        cmd = ["python", "test_complete_workflow.py", image_path, output_dir]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print(result.stdout)
        
        if result.returncode == 0:
            print(f"✅ Đã xử lý thành công ảnh: {os.path.basename(image_path)}")
            return True
        else:
            print(f"❌ Lỗi khi xử lý ảnh: {os.path.basename(image_path)}")
            print(result.stderr)
            return False
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi xử lý ảnh: {os.path.basename(image_path)}")
        print(e.stderr)
        return False
    
    except Exception as e:
        print(f"❌ Lỗi khi xử lý ảnh: {os.path.basename(image_path)}")
        print(f"  {e}")
        return False

def generate_reports(output_dir):
    """Tạo báo cáo HTML cho từng ảnh và báo cáo tổng hợp"""
    print(f"\n--- Tạo báo cáo HTML ---")
    
    # Tìm các thư mục con chứa kết quả
    image_dirs = []
    for item in os.listdir(output_dir):
        item_path = os.path.join(output_dir, item)
        if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "report.json")):
            image_dirs.append(item_path)
    
    # Tạo báo cáo HTML cho từng ảnh
    for image_dir in image_dirs:
        try:
            # Gọi script generate_html_report.py
            cmd = ["python", "generate_html_report.py", image_dir]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if result.returncode == 0:
                print(f"✅ Đã tạo báo cáo HTML cho thư mục: {os.path.basename(image_dir)}")
            else:
                print(f"❌ Lỗi khi tạo báo cáo HTML cho thư mục: {os.path.basename(image_dir)}")
                print(result.stderr)
        
        except Exception as e:
            print(f"❌ Lỗi khi tạo báo cáo HTML cho thư mục: {os.path.basename(image_dir)}")
            print(f"  {e}")
    
    # Tạo báo cáo tổng hợp
    try:
        # Gọi script generate_summary_report.py
        cmd = ["python", "generate_summary_report.py", output_dir]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            print(f"✅ Đã tạo báo cáo tổng hợp HTML")
            return True
        else:
            print(f"❌ Lỗi khi tạo báo cáo tổng hợp HTML")
            print(result.stderr)
            return False
    
    except Exception as e:
        print(f"❌ Lỗi khi tạo báo cáo tổng hợp HTML")
        print(f"  {e}")
        return False

def main():
    """Hàm chính"""
    # Phân tích tham số dòng lệnh
    parser = argparse.ArgumentParser(description="Xử lý nhiều ảnh cùng lúc và tạo báo cáo tổng hợp")
    parser.add_argument("input", help="Đường dẫn đến thư mục chứa ảnh hoặc đường dẫn đến một ảnh")
    parser.add_argument("-o", "--output", help="Thư mục đầu ra", default="batch_processing_output")
    parser.add_argument("-f", "--force", help="Ghi đè thư mục đầu ra nếu đã tồn tại", action="store_true")
    
    args = parser.parse_args()
    
    # Kiểm tra đường dẫn đầu vào
    input_path = args.input
    if not os.path.exists(input_path):
        print(f"❌ Không tìm thấy đường dẫn: {input_path}")
        return
    
    # Thư mục đầu ra
    output_dir = args.output
    if os.path.exists(output_dir) and not args.force:
        print(f"❌ Thư mục đầu ra đã tồn tại: {output_dir}")
        print("Sử dụng tham số -f hoặc --force để ghi đè")
        return
    
    ensure_dir(output_dir)
    
    print(f"🚀 XỬ LÝ NHIỀU ẢNH CÙNG LÚC")
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
            success = process_image(image_path, output_dir)
            if success:
                results.append(image_path)
        
        # Tạo báo cáo
        generate_reports(output_dir)
        
        # Tổng kết
        print(f"\n{'='*50}")
        print("TỔNG KẾT")
        print(f"{'='*50}")
        
        print(f"🎉 HOÀN THÀNH XỬ LÝ NHIỀU ẢNH CÙNG LÚC!")
        print(f"✅ Đã xử lý {len(image_files)} ảnh")
        print(f"✅ Đã xử lý thành công {len(results)} ảnh")
        print(f"📁 Kết quả lưu tại: {output_dir}/")
        print(f"📄 Báo cáo tổng hợp: {os.path.join(output_dir, 'summary.html')}")
    
    else:
        # Xử lý file ảnh đơn lẻ
        success = process_image(input_path, output_dir)
        
        # Tạo báo cáo
        if success:
            generate_reports(output_dir)
            
            # Tổng kết
            print(f"\n{'='*50}")
            print("TỔNG KẾT")
            print(f"{'='*50}")
            
            print(f"🎉 HOÀN THÀNH XỬ LÝ ẢNH!")
            print(f"✅ Đã xử lý thành công ảnh: {input_path}")
            print(f"📁 Kết quả lưu tại: {output_dir}/")
            print(f"📄 Báo cáo tổng hợp: {os.path.join(output_dir, 'summary.html')}")

if __name__ == "__main__":
    main() 