import cv2
import numpy as np
import os
from pathlib import Path

def create_debug_dir(debug_base_path):
    """Tạo thư mục debug nếu chưa tồn tại"""
    if not os.path.exists(debug_base_path):
        os.makedirs(debug_base_path)

def filter_border_lines(lines, image_width, border_threshold=10):
    """Loại bỏ các đường quá gần biên trái/phải của ảnh"""
    filtered = []
    removed = []
    for x in lines:
        # Kiểm tra khoảng cách đến biên trái và biên phải
        if x > border_threshold and x < (image_width - border_threshold):
            filtered.append(x)
        else:
            removed.append(x)
    
    if removed:
        print(f"Đã loại bỏ {len(removed)} đường dọc gần biên: {removed}")
        print(f"- Các đường dọc quá gần biên trái (<{border_threshold}px): {[x for x in removed if x <= border_threshold]}")
        print(f"- Các đường dọc quá gần biên phải (>{image_width-border_threshold}px): {[x for x in removed if x >= image_width-border_threshold]}")
    
    return filtered

def dedup_lines(lines, threshold=20):
    """Loại bỏ các đường thẳng trùng lặp"""
    if not lines:
        return []
    deduped = []
    removed = []
    for x in sorted(lines):
        if not deduped or abs(x - deduped[-1]) > threshold:
            deduped.append(x)
        else:
            removed.append(x)
    
    if removed:
        print(f"Đã loại bỏ {len(removed)} đường dọc trùng lặp")
    
    return deduped

def detect_columns(image_path, debug_dir):
    """Phát hiện đường dọc sử dụng 3 phương pháp khác nhau"""
    # Đọc và tiền xử lý ảnh
    image = cv2.imread(image_path)
    if image is None:
        print(f"Không thể đọc ảnh: {image_path}")
        return
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    height, width = binary.shape
    print(f"\nKích thước ảnh: {width}x{height} pixels")
    
    # Lưu ảnh tiền xử lý để debug
    cv2.imwrite(os.path.join(debug_dir, "1_gray.jpg"), gray)
    cv2.imwrite(os.path.join(debug_dir, "2_binary.jpg"), binary)
    
    boundaries = []
    
    # === PHƯƠNG PHÁP 1: MORPHOLOGY ===
    img_morph = image.copy()
    kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, height // 30))
    morph_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_v, iterations=2)
    cv2.imwrite(os.path.join(debug_dir, "3_morph_lines.jpg"), morph_lines)
    
    contours, _ = cv2.findContours(morph_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boundaries = [cv2.boundingRect(c)[0] for c in contours if cv2.boundingRect(c)[3] > height // 2]
    boundaries = sorted(list(set(boundaries)))
    print(f"\nĐã tìm thấy {len(boundaries)} đường dọc ban đầu:")
    for i, x in enumerate(boundaries, 1):
        print(f"Đường {i}: tại vị trí x = {x}px")
    
    boundaries = dedup_lines(boundaries)
    print(f"\nSau khi loại bỏ trùng lặp: {len(boundaries)} đường dọc:")
    for i, x in enumerate(boundaries, 1):
        print(f"Đường {i}: tại vị trí x = {x}px")
    
    # Vẽ kết quả phương pháp 1
    for i, x in enumerate(boundaries, 1):
        cv2.line(img_morph, (x, 0), (x, height), (0, 255, 0), 2)
        # Thêm số thứ tự vào ảnh
        cv2.putText(img_morph, str(i), (x-10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imwrite(os.path.join(debug_dir, "4_method1_morphology.jpg"), img_morph)
    
    # === PHƯƠNG PHÁP 2: HOUGH LINES ===
    if len(boundaries) < 3:
        img_hough = image.copy()
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        cv2.imwrite(os.path.join(debug_dir, "5_edges.jpg"), edges)
        
        hough_lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=150,
                                    minLineLength=100, maxLineGap=10)
        hough_x = []
        if hough_lines is not None:
            for line in hough_lines:
                x1, y1, x2, y2 = line[0]
                angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                if abs(angle) > 80:
                    hough_x.append(x1)
                    cv2.line(img_hough, (x1, y1), (x2, y2), (0, 0, 255), 2)
        
        cv2.imwrite(os.path.join(debug_dir, "6_method2_hough.jpg"), img_hough)
        boundaries = dedup_lines(boundaries + hough_x)
    
    # === PHƯƠNG PHÁP 3: LSD ===
    if len(boundaries) < 3:
        img_lsd = image.copy()
        lsd = cv2.createLineSegmentDetector(0)
        lines_lsd, _, _, _ = lsd.detect(gray)
        lsd_x = []
        if lines_lsd is not None:
            for line in lines_lsd:
                x1, y1, x2, y2 = map(int, line[0])
                angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                if abs(angle) > 80:
                    lsd_x.append(x1)
                    cv2.line(img_lsd, (x1, y1), (x2, y2), (255, 0, 0), 2)
        
        cv2.imwrite(os.path.join(debug_dir, "7_method3_lsd.jpg"), img_lsd)
        boundaries = dedup_lines(boundaries + lsd_x)
    
    # Lọc bỏ các đường gần biên
    print("\nLọc bỏ các đường dọc gần biên (khoảng cách < 10px):")
    boundaries = filter_border_lines(boundaries, width, border_threshold=10)
    
    # Vẽ kết quả cuối cùng
    img_final = image.copy()
    for i, x in enumerate(boundaries, 1):
        cv2.line(img_final, (x, 0), (x, height), (0, 0, 255), 2)
        # Thêm số thứ tự vào ảnh
        cv2.putText(img_final, str(i), (x-10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.imwrite(os.path.join(debug_dir, "8_final_result.jpg"), img_final)
    
    return boundaries

def main():
    # Thư mục chứa ảnh đầu vào
    input_dir = "D:/MyProjects/MagicTbl1806_restored/tables"
    # Thư mục debug
    debug_base_dir = "D:/MyProjects/MagicTbl1806_restored/debug"
    
    # Tạo thư mục debug
    create_debug_dir(debug_base_dir)
    
    # Xử lý tất cả các ảnh trong thư mục input
    for img_file in Path(input_dir).glob("**/*.jpg"):
        print(f"\n{'='*50}")
        print(f"Đang xử lý ảnh: {img_file}")
        print(f"{'='*50}")
        
        # Tạo thư mục debug cho từng ảnh
        img_debug_dir = os.path.join(debug_base_dir, img_file.stem)
        create_debug_dir(img_debug_dir)
        
        # Phát hiện đường dọc
        boundaries = detect_columns(str(img_file), img_debug_dir)
        if boundaries:
            print(f"\nKẾT QUẢ CUỐI CÙNG:")
            print(f"Số đường dọc còn lại sau khi lọc: {len(boundaries)}")
            print("Vị trí các đường dọc:")
            for i, x in enumerate(boundaries, 1):
                print(f"Đường {i}: tại vị trí x = {x}px")
        print(f"\n{'='*50}")

if __name__ == "__main__":
    main() 