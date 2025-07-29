import cv2
import numpy as np
import os
from pathlib import Path
from detect_row.advanced_table_extractor import AdvancedTableExtractor

def create_debug_dir(debug_base_path):
    """Tạo thư mục debug nếu chưa tồn tại"""
    if not os.path.exists(debug_base_path):
        os.makedirs(debug_base_path)

def draw_table_info(image, tables, table_idx):
    """Vẽ thông tin bảng lên ảnh"""
    img_debug = image.copy()
    height, width = image.shape[:2]
    
    # Vẽ các bảng đã phát hiện
    for i, (x1, y1, x2, y2) in enumerate(tables):
        # Vẽ hộp bao quanh bảng
        cv2.rectangle(img_debug, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Tính kích thước bảng
        w = x2 - x1
        h = y2 - y1
        area = w * h
        ratio = w / h if h > 0 else 0
        
        # Vẽ thông tin bảng
        info_text = f"Table {i+1}: {w}x{h}px, ratio={ratio:.2f}"
        cv2.putText(img_debug, info_text, (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Vẽ tọa độ các góc
        corner_text = f"({x1},{y1})"
        cv2.putText(img_debug, corner_text, (x1, y1+20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        corner_text = f"({x2},{y2})"
        cv2.putText(img_debug, corner_text, (x2-70, y2-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    
    # Vẽ thông tin tổng quát
    summary_text = f"Image size: {width}x{height}px, Found {len(tables)} tables"
    cv2.putText(img_debug, summary_text, (10, height-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    return img_debug

def draw_simple_boxes(image, tables):
    """Chỉ vẽ box đơn giản lên ảnh gốc"""
    img_with_boxes = image.copy()
    
    # Vẽ các bảng đã phát hiện với box màu đỏ và số thứ tự
    for i, (x1, y1, x2, y2) in enumerate(tables):
        # Vẽ box với viền đỏ dày 2px
        cv2.rectangle(img_with_boxes, (x1, y1), (x2, y2), (0, 0, 255), 2)
        
        # Vẽ số thứ tự của bảng
        cv2.putText(img_with_boxes, str(i+1), (x1+10, y1+30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    return img_with_boxes

def analyze_table_detection(image_path, debug_dir, output_dir, tables_dir):
    """Phân tích và vẽ kết quả nhận diện bảng"""
    print(f"\n{'='*50}")
    print(f"Đang xử lý ảnh: {image_path}")
    
    # Đọc ảnh
    image = cv2.imread(image_path)
    if image is None:
        print(f"Không thể đọc ảnh: {image_path}")
        return
    
    height, width = image.shape[:2]
    print(f"Kích thước ảnh: {width}x{height} pixels")
    
    # Khởi tạo table extractor
    extractor = AdvancedTableExtractor(
        input_dir="input",
        output_dir="output/tables",
        debug_dir=debug_dir
    )
    
    # Phát hiện bảng
    print("\nĐang phát hiện bảng...")
    tables = extractor.detect_table(image)
    
    if not tables:
        print("Không phát hiện được bảng nào!")
        return
    
    # Lấy tên file không có phần mở rộng
    file_stem = Path(image_path).stem
    
    print(f"\nĐã phát hiện {len(tables)} bảng:")
    for i, (x1, y1, x2, y2) in enumerate(tables):
        w = x2 - x1
        h = y2 - y1
        ratio = w / h
        area = w * h
        area_ratio = area / (width * height) * 100
        
        print(f"\nBảng {i+1}:")
        print(f"- Vị trí: ({x1}, {y1}) -> ({x2}, {y2})")
        print(f"- Kích thước: {w}x{h} pixels")
        print(f"- Tỷ lệ w/h: {ratio:.2f}")
        print(f"- Diện tích: {area} pixels ({area_ratio:.1f}% ảnh)")
        
        # Cắt và lưu bảng
        table_img = image[y1:y2, x1:x2]
        table_path = os.path.join(tables_dir, f"{file_stem}_table_{i+1}.jpg")
        cv2.imwrite(table_path, table_img)
        print(f"- Đã lưu bảng: {table_path}")
    
    # Vẽ kết quả nhận diện chi tiết để debug
    img_with_debug = draw_table_info(image, tables, os.path.basename(image_path))
    
    # Vẽ box đơn giản lên ảnh gốc
    img_with_boxes = draw_simple_boxes(image, tables)
    
    # Lưu ảnh debug
    debug_path = os.path.join(debug_dir, f"detected_tables_{file_stem}.jpg")
    cv2.imwrite(debug_path, img_with_debug)
    print(f"\nĐã lưu ảnh debug: {debug_path}")
    
    # Lưu ảnh có box vào output
    output_path = os.path.join(output_dir, f"tables_{file_stem}.jpg")
    cv2.imwrite(output_path, img_with_boxes)
    print(f"Đã lưu ảnh có box: {output_path}")
    
    # Phân tích cấu trúc từng bảng
    for i, (x1, y1, x2, y2) in enumerate(tables):
        print(f"\nPhân tích cấu trúc bảng {i+1}...")
        
        # Cắt ảnh bảng
        table_img = image[y1:y2, x1:x2]
        
        # Phân tích cấu trúc
        structure = extractor.detect_table_structure(table_img)
        
        # Vẽ cấu trúc bảng
        table_debug = table_img.copy()
        
        # Vẽ đường kẻ ngang
        for y in structure.horizontal_lines:
            cv2.line(table_debug, (0, y), (table_img.shape[1], y), (0, 255, 0), 1)
        
        # Vẽ đường kẻ dọc
        for x in structure.vertical_lines:
            cv2.line(table_debug, (x, 0), (x, table_img.shape[0]), (255, 0, 0), 1)
        
        # Đánh dấu ô gộp
        for r1, c1, r2, c2, x, y in structure.merged_cells:
            cv2.rectangle(table_debug, (x, y),
                        (structure.vertical_lines[c2+1], structure.horizontal_lines[r2+1]),
                        (0, 0, 255), 2)
        
        # Đánh dấu hàng tiêu đề
        for row_idx in structure.header_rows:
            y1 = structure.horizontal_lines[row_idx]
            y2 = structure.horizontal_lines[row_idx + 1]
            cv2.rectangle(table_debug, (0, y1), (table_img.shape[1], y2),
                        (255, 255, 0), 2)
        
        # Lưu ảnh debug cấu trúc bảng
        structure_debug_path = os.path.join(debug_dir, 
                                          f"table_{i+1}_structure_{file_stem}.jpg")
        cv2.imwrite(structure_debug_path, table_debug)
        
        print(f"- Số hàng: {len(structure.horizontal_lines) - 1}")
        print(f"- Số cột: {len(structure.vertical_lines) - 1}")
        print(f"- Số ô gộp: {len(structure.merged_cells)}")
        print(f"- Số hàng tiêu đề: {len(structure.header_rows)}")
        print(f"- Đã lưu ảnh cấu trúc: {structure_debug_path}")
    
    print(f"\n{'='*50}")

def main():
    # Thư mục chứa ảnh đầu vào
    input_dir = "input"
    # Thư mục debug và output
    debug_dir = "debug/table_detection"
    output_dir = "output/detected_tables"
    tables_dir = "tables"
    
    # Tạo các thư mục cần thiết
    create_debug_dir(debug_dir)
    create_debug_dir(output_dir)
    create_debug_dir(tables_dir)
    
    # Lấy danh sách các file ảnh
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png']:
        image_files.extend(Path(input_dir).glob(ext))
    
    if not image_files:
        print(f"Không tìm thấy file ảnh nào trong thư mục {input_dir}")
        return
    
    print(f"Tìm thấy {len(image_files)} file ảnh")
    
    # Xử lý từng ảnh
    for img_file in image_files:
        analyze_table_detection(str(img_file), debug_dir, output_dir, tables_dir)

if __name__ == "__main__":
    main() 