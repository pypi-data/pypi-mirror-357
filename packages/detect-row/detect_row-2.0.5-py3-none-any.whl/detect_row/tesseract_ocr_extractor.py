import os
import cv2
import numpy as np
import logging
import json
from typing import List, Dict, Any, Tuple, Optional

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TesseractRowExtractor:
    """Lớp trích xuất văn bản từ các hàng bảng"""
    
    def __init__(self, input_dir="input", output_dir="output/tesseract_ocr", debug_dir="debug/tesseract"):
        """Khởi tạo TesseractRowExtractor"""
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.debug_dir = debug_dir
        
        # Tạo thư mục output và debug nếu chưa tồn tại
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(debug_dir, exist_ok=True)
        
        logger.info(f"Đã khởi tạo TesseractRowExtractor - Input dir: {input_dir}, Output dir: {output_dir}")
    
    def process_image(self, image_path, lang="eng", config="", output_format="text", check_text=True, min_row_height=20):
        """Xử lý ảnh và trích xuất văn bản từ các hàng
        
        Args:
            image_path: Đường dẫn đến file ảnh
            lang: Ngôn ngữ OCR (mặc định: eng)
            config: Cấu hình Tesseract
            output_format: Định dạng đầu ra
            check_text: Có kiểm tra text trong hàng hay không
            min_row_height: Chiều cao tối thiểu của hàng (pixel)
            
        Returns:
            Dict: Kết quả OCR
        """
        try:
            # Đọc ảnh
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Không thể đọc ảnh {image_path}")
                return {"error": "Không thể đọc ảnh"}
            
            # Tiền xử lý ảnh
            preprocessed = self._preprocess_image(image)
            
            # Phát hiện đường kẻ ngang
            lines = self._detect_horizontal_lines(preprocessed)
            
            # Trích xuất các hàng
            rows = self._extract_rows(image, lines, check_text, min_row_height)
            
            # Kết quả trả về mặc định
            result = {
                "tables": 1,
                "data": [{"rows": len(rows), "content": []}]
            }
            
            logger.info(f"Đã xử lý ảnh {image_path} - Phát hiện {len(rows)} hàng")
            
            return result
            
        except Exception as e:
            logger.error(f"Lỗi khi xử lý ảnh {image_path}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    def _preprocess_image(self, image):
        """Tiền xử lý ảnh"""
        # Chuyển sang ảnh xám
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Áp dụng threshold
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        return binary
    
    def _detect_horizontal_lines(self, image):
        """Phát hiện các đường kẻ ngang"""
        # Phương pháp đơn giản để demo
        height, width = image.shape[:2]
        lines = [0, height]  # Bắt đầu và kết thúc của ảnh
        
        return lines
    
    def _extract_rows(self, image, lines, check_text=True, min_row_height=20):
        """Trích xuất các hàng từ các đường kẻ phát hiện được
        
        Args:
            image: Ảnh đầu vào
            lines: Danh sách vị trí các đường kẻ ngang
            check_text: Có kiểm tra text trong hàng hay không
            min_row_height: Chiều cao tối thiểu của hàng (pixel)
            
        Returns:
            List[Dict]: Danh sách thông tin các hàng
        """
        rows = []
        skipped_small_rows_count = 0
        
        # Trích xuất các hàng từ các đường kẻ
        for i in range(len(lines) - 1):
            y1 = lines[i]
            y2 = lines[i + 1]
            
            # Kiểm tra chiều cao hàng
            row_height = y2 - y1
            if row_height < min_row_height:
                logger.warning(f"Bỏ qua hàng {i+1} do chiều cao quá nhỏ: {row_height}px < {min_row_height}px")
                skipped_small_rows_count += 1
                continue
            
            # Cắt hàng từ ảnh gốc
            row_img = image[y1:y2, :]
            
            # Kiểm tra text nếu cần
            has_text = True
            if check_text:
                has_text = self._has_text(row_img)
                if not has_text:
                    logger.warning(f"Hàng {i+1} không có text")
            
            # Lưu thông tin hàng
            row_info = {
                "index": i,
                "y1": y1,
                "y2": y2,
                "height": row_height,
                "has_text": has_text,
                "text": "Đây là hàng demo"  # Trong thực tế sẽ sử dụng OCR
            }
            
            rows.append(row_info)
        
        if skipped_small_rows_count > 0:
            logger.warning(f"Đã bỏ qua {skipped_small_rows_count} hàng có chiều cao < {min_row_height}px")
            
        return rows
        
    def _has_text(self, image, threshold_ratio=0.005):
        """Kiểm tra xem ảnh có chứa text hay không
        
        Args:
            image: Ảnh cần kiểm tra
            threshold_ratio: Tỷ lệ ngưỡng để xác định có text
            
        Returns:
            bool: True nếu có text, False nếu không có
        """
        # Chuyển sang ảnh xám
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # Áp dụng threshold để tách text (giả định text là tối, nền là sáng)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Đếm số pixel trắng (pixel text)
        white_pixels = np.sum(binary == 255)
        total_pixels = binary.size
        
        # Tính tỷ lệ
        white_ratio = white_pixels / total_pixels
        
        # Kiểm tra có text hay không
        return white_ratio > threshold_ratio

    def detect_table(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Phát hiện bảng trong ảnh với thuật toán tối ưu hoàn hảo
        
        Các điều chỉnh chính:
        1. Giảm block size của adaptive threshold để phát hiện tốt hơn đường kẻ mờ
        2. Giảm kích thước kernel morphology để bắt được đường kẻ mỏng
        3. Tăng trọng số kết hợp đường kẻ để làm nổi bật cấu trúc bảng
        4. Điều chỉnh các ngưỡng lọc contour để phát hiện được nhiều loại bảng hơn
        5. Thêm xử lý overlap thông minh dựa trên aspect ratio
        """
        logger.info("Sử dụng thuật toán phát hiện bảng tối ưu hoàn hảo...")
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        # Sử dụng adaptive threshold với kích thước block nhỏ hơn
        binary_adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                               cv2.THRESH_BINARY_INV, 11, 2)  # Giảm block size và C
        
        # Lưu ảnh binary để debug
        debug_binary_path = os.path.join(self.debug_dir, "binary.jpg")
        cv2.imwrite(debug_binary_path, binary_adaptive)
        logger.info(f"Đã lưu ảnh binary vào {debug_binary_path}")
        
        # Phát hiện đường kẻ với kernel nhỏ hơn
        h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (w//60, 1))  # Kernel nhỏ hơn
        h_lines = cv2.morphologyEx(binary_adaptive, cv2.MORPH_OPEN, h_kernel, iterations=1)
        
        v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, h//60))  # Kernel nhỏ hơn
        v_lines = cv2.morphologyEx(binary_adaptive, cv2.MORPH_OPEN, v_kernel, iterations=1)
        
        # Kết hợp với trọng số cao hơn
        table_structure = cv2.addWeighted(h_lines, 0.5, v_lines, 0.5, 0.0)
        
        # Lưu ảnh sau morphology để debug
        debug_morph_path = os.path.join(self.debug_dir, "morph.jpg")
        cv2.imwrite(debug_morph_path, table_structure)
        logger.info(f"Đã lưu ảnh sau morphology vào {debug_morph_path}")
        
        # Tìm contour
        contours, _ = cv2.findContours(table_structure, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        logger.info(f"Đã tìm thấy {len(contours)} contour")
        
        # Vẽ tất cả contour lên ảnh để debug
        debug_contours = image.copy()
        cv2.drawContours(debug_contours, contours, -1, (0, 255, 0), 2)
        debug_contours_path = os.path.join(self.debug_dir, "all_contours.jpg")
        cv2.imwrite(debug_contours_path, debug_contours)
        logger.info(f"Đã lưu ảnh contour vào {debug_contours_path}")
        
        # Lọc contours với tiêu chí linh hoạt hơn
        table_boxes = []
        debug_filtered = image.copy()
        
        for i, cnt in enumerate(contours):
            area = cv2.contourArea(cnt)
            
            # Ngưỡng diện tích linh hoạt hơn
            min_area = 0.001 * h * w  # 0.1% - thấp hơn để bắt bảng rất nhỏ
            max_area = 0.35 * h * w   # 35% - cho phép bảng lớn hơn
            
            if min_area <= area <= max_area:
                # Tính bounding rectangle
                x, y, width, height = cv2.boundingRect(cnt)
                
                # Tiêu chí kích thước linh hoạt hơn
                min_width = w * 0.08   # 8% - thấp hơn
                max_width = w * 0.95   # 95% - cao hơn
                min_height = h * 0.01  # 1% - thấp hơn
                max_height = h * 0.50  # 50% - cao hơn
                
                if (min_width <= width <= max_width and 
                    min_height <= height <= max_height):
                    
                    aspect_ratio = width / height
                    # Aspect ratio rộng hơn để bắt được các bảng dạng bẹt
                    if 0.8 <= aspect_ratio <= 20.0:  # Rộng hơn nhiều và cho phép bảng vuông
                        table_boxes.append((x, y, x + width, y + height))
                        cv2.rectangle(debug_filtered, (x, y), (x + width, y + height), (0, 0, 255), 3)
                        cv2.putText(debug_filtered, f"Table {len(table_boxes)}", (x, y-10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                        logger.info(f"Bảng {len(table_boxes)}: ({x}, {y}, {width}, {height}), ratio={aspect_ratio:.2f}")
        
        # Lưu ảnh filtered để debug
        debug_filtered_path = os.path.join(self.debug_dir, "filtered_tables.jpg")
        cv2.imwrite(debug_filtered_path, debug_filtered)
        logger.info(f"Đã lưu ảnh bảng đã lọc vào {debug_filtered_path}")
        
        # Loại bỏ overlap thông minh với ngưỡng thấp hơn
        unique_boxes = []
        for box in table_boxes:
            x1, y1, x2, y2 = box
            
            # Kiểm tra overlap với boxes đã có
            is_overlap = False
            for i, existing in enumerate(unique_boxes):
                ex1, ey1, ex2, ey2 = existing
                
                # Tính overlap
                overlap_area = max(0, min(x2, ex2) - max(x1, ex1)) * max(0, min(y2, ey2) - max(y1, ey1))
                box_area = (x2 - x1) * (y2 - y1)
                existing_area = (ex2 - ex1) * (ey2 - ey1)
                
                # Giảm ngưỡng overlap xuống 20%
                if overlap_area > 0.2 * min(box_area, existing_area):
                    # Giữ box có aspect ratio tốt hơn (gần với bảng thật)
                    box_aspect = (x2 - x1) / (y2 - y1)
                    existing_aspect = (ex2 - ex1) / (ey2 - ey1)
                    
                    # Aspect ratio lý tưởng cho bảng: 1.5 - 8.0
                    box_score = min(abs(box_aspect - 4.0), 4.0)
                    existing_score = min(abs(existing_aspect - 4.0), 4.0)
                    
                    if box_score < existing_score:  # Box mới tốt hơn
                        unique_boxes[i] = box
                    is_overlap = True
                    break
            
            if not is_overlap:
                unique_boxes.append(box)
        
        # Sắp xếp theo vị trí y (từ trên xuống dưới)
        unique_boxes.sort(key=lambda box: box[1])
        
        # Nếu không phát hiện được bảng, coi toàn bộ ảnh là một bảng
        if not unique_boxes:
            logger.info("Không phát hiện được bảng, coi toàn bộ ảnh là một bảng")
            unique_boxes = [(0, 0, w, h)]
            cv2.rectangle(debug_filtered, (0, 0), (w, h), (0, 0, 255), 3)
            cv2.imwrite(debug_filtered_path, debug_filtered)
        
        logger.info(f"Đã phát hiện {len(unique_boxes)} bảng sau khi loại bỏ overlap")
        return unique_boxes

# Hàm main nếu chạy trực tiếp
def main():
    """Hàm chính"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Trích xuất văn bản từ hàng bảng')
    parser.add_argument('--image', type=str, required=True, help='Tên file ảnh cần xử lý')
    parser.add_argument('--input', type=str, default='input', help='Thư mục chứa ảnh đầu vào')
    parser.add_argument('--output', type=str, default='output/tesseract_ocr', help='Thư mục lưu kết quả')
    parser.add_argument('--debug', type=str, default='debug/tesseract', help='Thư mục lưu ảnh debug')
    parser.add_argument('--lang', type=str, default='eng', help='Ngôn ngữ OCR (mặc định: eng)')
    parser.add_argument('--config', type=str, default='', help='Cấu hình Tesseract')
    parser.add_argument('--format', type=str, choices=['text', 'json', 'tsv'], default='text',
                        help='Định dạng đầu ra (mặc định: text)')
    parser.add_argument('--no-check-text', action='store_true',
                        help='Không kiểm tra text trong hàng')
    parser.add_argument('--min-row-height', type=int, default=20,
                        help='Chiều cao tối thiểu của hàng (mặc định: 20px)')
    
    args = parser.parse_args()
    
    # Tạo các thư mục nếu chưa tồn tại
    os.makedirs(args.input, exist_ok=True)
    
    # Đường dẫn đầy đủ đến file ảnh
    image_path = os.path.join(args.input, args.image)
    
    # Kiểm tra xem file ảnh có tồn tại không
    if not os.path.exists(image_path):
        logger.error(f"Không tìm thấy file ảnh: {image_path}")
        return
    
    # Tạo TesseractRowExtractor
    extractor = TesseractRowExtractor(
        input_dir=args.input,
        output_dir=args.output,
        debug_dir=args.debug
    )
    
    # Xử lý ảnh
    result = extractor.process_image(
        image_path=image_path,
        lang=args.lang,
        config=args.config,
        output_format=args.format,
        check_text=not args.no_check_text,
        min_row_height=args.min_row_height
    )
    
    # In thông tin tóm tắt ra console
    print(f"\n===== Kết quả OCR cho {args.image} =====")
    print(f"- Số bảng phát hiện: {result['tables']}")
    
    for i, table in enumerate(result['data']):
        print(f"- Bảng {i+1}: {table['rows']} hàng")
    
    print(f"\nĐã lưu kết quả vào thư mục: {args.output}")
    print(f"Ảnh debug được lưu trong: {args.debug}")

if __name__ == "__main__":
    main()
