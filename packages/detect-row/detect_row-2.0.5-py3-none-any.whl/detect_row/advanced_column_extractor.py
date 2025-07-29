"""
Module trích xuất cột nâng cao
--------------------------

Module này cung cấp các chức năng trích xuất cột từ bảng, bao gồm:
- Phát hiện vị trí các cột trong bảng
- Trích xuất từng cột riêng biệt
- Gộp nhiều cột thành một file
- Hỗ trợ nhiều loại bảng khác nhau
"""

import os
import cv2
import numpy as np
import logging
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path

# Sửa import để hoạt động trong cả môi trường development và production
try:
    from .base import BaseRowExtractor, logger
    from .advanced_table_extractor import AdvancedTableExtractor
except ImportError:
    from detect_row.base import BaseRowExtractor, logger
    from detect_row.advanced_table_extractor import AdvancedTableExtractor

logger = logging.getLogger(__name__)

class AdvancedColumnExtractor(AdvancedTableExtractor):
    """Lớp trích xuất cột nâng cao từ bảng"""
    
    def __init__(self, 
                 input_dir: str = "input", 
                 output_dir: str = "output/columns",
                 debug_dir: str = "debug/columns",
                 min_column_width: int = 30):
        """Khởi tạo AdvancedColumnExtractor
        
        Args:
            input_dir: Thư mục chứa ảnh đầu vào
            output_dir: Thư mục lưu các cột đã trích xuất
            debug_dir: Thư mục lưu ảnh debug
            min_column_width: Chiều rộng tối thiểu của cột (pixel)
        """
        super().__init__(input_dir, output_dir, debug_dir)
        self.min_column_width = min_column_width
        
        # Tạo thư mục con cho từng loại cột
        self.columns_dir = os.path.join(output_dir, "individual_columns")
        self.merged_columns_dir = os.path.join(output_dir, "merged_columns")
        os.makedirs(self.columns_dir, exist_ok=True)
        os.makedirs(self.merged_columns_dir, exist_ok=True)
    
    def detect_table(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Phát hiện bảng trong ảnh với thuật toán tối ưu hoàn hảo
        
        Các điều chỉnh chính:
        1. Giảm block size của adaptive threshold để phát hiện tốt hơn đường kẻ mờ
        2. Giảm kích thước kernel morphology để bắt được đường kẻ mỏng
        3. Tăng trọng số kết hợp đường kẻ để làm nổi bật cấu trúc bảng
        4. Điều chỉnh các ngưỡng lọc contour để phát hiện được nhiều loại bảng hơn
        5. Thêm xử lý overlap thông minh dựa trên aspect ratio
        """
        logger.info("Sử dụng thuật toán phát hiện bảng tối ưu hoàn hảo cho column extractor...")
        
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
        
        logger.info(f"Đã phát hiện {len(unique_boxes)} bảng sau khi loại bỏ overlap")
        return unique_boxes
    
    def detect_vertical_lines(self, image: np.ndarray, min_line_length_ratio: float = 0.4) -> List[int]:
        """Phát hiện các đường kẻ dọc trong ảnh với độ chính xác cao hơn
        
        Args:
            image: Ảnh đã tiền xử lý
            min_line_length_ratio: Tỷ lệ tối thiểu của chiều dài đường kẻ so với chiều cao ảnh
            
        Returns:
            List[int]: Danh sách các tọa độ x của đường kẻ dọc
        """
        height, width = image.shape[:2]
        min_line_length = int(height * min_line_length_ratio)
        
        logger.info(f"Chiều dài tối thiểu của đường kẻ dọc: {min_line_length}px (={min_line_length_ratio:.2f} × {height}px)")
        
        # Tạo kernel dọc để phát hiện đường kẻ dọc
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, min_line_length // 6))
        
        # Áp dụng phép toán mở để phát hiện đường kẻ dọc
        vertical_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, vertical_kernel, iterations=3)
        
        # Lọc các đường dọc có chiều dài nhỏ hơn 80% đường dài nhất
        filtered_vertical_lines = np.zeros_like(vertical_lines)
        contours, _ = cv2.findContours(vertical_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Tìm chiều dài lớn nhất của đường kẻ dọc
        max_length = 0
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            max_length = max(max_length, h)
        
        # Lọc các đường kẻ có chiều dài lớn hơn 80% đường dài nhất
        min_length_threshold = int(max_length * 0.8)
        logger.info(f"Chiều dài tối thiểu của đường kẻ dọc (80% đường dài nhất): {min_length_threshold}px")
        
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if h >= min_length_threshold:
                cv2.drawContours(filtered_vertical_lines, [cnt], -1, 255, -1)
        
        # Làm dày đường kẻ để dễ phát hiện
        dilate_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, min_line_length // 15))
        filtered_vertical_lines = cv2.dilate(filtered_vertical_lines, dilate_kernel, iterations=2)
        
        # Lưu ảnh đường kẻ dọc để debug
        debug_path_original = os.path.join(self.debug_dir, "vertical_lines_original.jpg")
        cv2.imwrite(debug_path_original, vertical_lines)
        
        debug_path_filtered = os.path.join(self.debug_dir, "vertical_lines_filtered.jpg")
        cv2.imwrite(debug_path_filtered, filtered_vertical_lines)
        
        # Phát hiện đường kẻ dọc bằng histogram theo phương dọc
        # Chiếu tổng theo trục y để tìm vị trí các đường kẻ dọc
        v_projection = cv2.reduce(filtered_vertical_lines, 0, cv2.REDUCE_SUM, dtype=cv2.CV_32S)
        v_projection = v_projection.flatten()
        
        # Chuẩn hóa histogram
        v_projection = v_projection / 255
        
        # Tìm giá trị lớn nhất trong histogram để lọc
        max_projection_value = np.max(v_projection)
        threshold_value = max_projection_value * 0.4  # Lọc giá trị < 40% đỉnh cao nhất
        logger.info(f"Giá trị ngưỡng lọc histogram dọc (40% giá trị lớn nhất): {threshold_value:.2f}")
        
        # Áp dụng ngưỡng để lọc histogram
        filtered_projection = np.copy(v_projection)
        filtered_projection[filtered_projection < threshold_value] = 0
        
        # Lưu histogram để debug
        import matplotlib.pyplot as plt
        plt.figure(figsize=(width // 50, 8))
        plt.plot(range(width), v_projection, color='blue', alpha=0.5, label='Original')
        plt.plot(range(width), filtered_projection, color='red', label='Filtered (>40%)')
        plt.axhline(y=threshold_value, color='green', linestyle='--', label=f'Threshold (40%): {threshold_value:.2f}')
        plt.title('Vertical Projection Histogram')
        plt.legend()
        plt.savefig(os.path.join(self.debug_dir, 'v_projection.png'), bbox_inches='tight')
        plt.close()
        
        # Tìm vị trí các đỉnh trong histogram
        line_positions = []
        threshold = height / 6  # Ngưỡng cơ bản để xác định đường kẻ dọc
        
        for x in range(1, width - 1):
            if filtered_projection[x] > threshold:
                # Kiểm tra xem có phải đỉnh cục bộ không
                if filtered_projection[x] >= filtered_projection[x-1] and filtered_projection[x] >= filtered_projection[x+1]:
                    line_positions.append(x)
        
        # Lọc các đường kẻ quá gần nhau
        filtered_positions = self._filter_close_lines(line_positions, min_distance=self.min_column_width)
        
        # Thêm vị trí đầu và cuối ảnh nếu cần
        if len(filtered_positions) > 0 and filtered_positions[0] > 20:
            filtered_positions.insert(0, 0)
        if len(filtered_positions) > 0 and filtered_positions[-1] < width - 20:
            filtered_positions.append(width)
        
        # Sắp xếp lại các vị trí
        filtered_positions.sort()
        
        # Vẽ các đường kẻ dọc lên ảnh để debug
        debug_image = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2BGR)
        for x in filtered_positions:
            cv2.line(debug_image, (x, 0), (x, height), (0, 255, 0), 2)
        
        debug_lines_path = os.path.join(self.debug_dir, "detected_vertical_lines.jpg")
        cv2.imwrite(debug_lines_path, debug_image)
        
        logger.info(f"Đã phát hiện {len(filtered_positions)} đường kẻ dọc sau khi lọc")
        return filtered_positions
    
    def extract_columns_from_table(self, table_image: np.ndarray, table_name: str) -> List[Dict[str, Any]]:
        """Trích xuất các cột từ bảng
        
        Args:
            table_image: Ảnh bảng
            table_name: Tên bảng (để đặt tên file)
            
        Returns:
            List[Dict]: Danh sách thông tin các cột đã trích xuất
        """
        logger.info(f"Bắt đầu trích xuất cột từ bảng: {table_name}")
        
        # Tiền xử lý ảnh
        processed_image = self.preprocess_image(table_image)
        
        # Phát hiện đường kẻ dọc
        vertical_lines = self.detect_vertical_lines(processed_image)
        
        if len(vertical_lines) < 2:
            logger.warning(f"Không đủ đường kẻ dọc để tạo cột (chỉ có {len(vertical_lines)} đường)")
            return []
        
        # Trích xuất từng cột
        columns_info = []
        height, width = table_image.shape[:2]
        
        for i in range(len(vertical_lines) - 1):
            x1, x2 = vertical_lines[i], vertical_lines[i + 1]
            
            # Kiểm tra chiều rộng cột
            column_width = x2 - x1
            if column_width < self.min_column_width:
                logger.info(f"Bỏ qua cột {i+1} (chiều rộng {column_width}px < {self.min_column_width}px)")
                continue
            
            # Cắt cột từ ảnh
            column_image = table_image[:, x1:x2]
            
            # Thông tin cột
            column_info = {
                'column_index': i + 1,
                'x1': x1,
                'x2': x2,
                'width': column_width,
                'image': column_image,
                'filename': f"{table_name}_column_{i+1:02d}.jpg"
            }
            
            columns_info.append(column_info)
            logger.info(f"Da trich xuat cot {i+1}: x={x1}-{x2}, width={column_width}px")
        
        return columns_info
    
    def save_individual_columns(self, columns_info: List[Dict[str, Any]], table_name: str) -> List[str]:
        """Lưu từng cột riêng biệt
        
        Args:
            columns_info: Thông tin các cột
            table_name: Tên bảng
            
        Returns:
            List[str]: Danh sách đường dẫn file đã lưu
        """
        saved_files = []
        
        for column_info in columns_info:
            filepath = os.path.join(self.columns_dir, column_info['filename'])
            cv2.imwrite(filepath, column_info['image'])
            saved_files.append(filepath)
            logger.info(f"Da luu cot {column_info['column_index']}: {column_info['filename']}")
        
        return saved_files
    
    def save_merged_columns(self, columns_info: List[Dict[str, Any]], table_name: str, 
                          column_groups: Dict[str, List[int]]) -> List[str]:
        """Lưu các cột đã gộp theo yêu cầu
        
        Args:
            columns_info: Thông tin các cột
            table_name: Tên bảng
            column_groups: Dict định nghĩa nhóm cột {"group_name": [list_column_indices]}
            
        Returns:
            List[str]: Danh sách đường dẫn file đã lưu
        """
        saved_files = []
        
        for group_name, column_indices in column_groups.items():
            # Tìm các cột cần gộp
            columns_to_merge = []
            for column_info in columns_info:
                if column_info['column_index'] in column_indices:
                    columns_to_merge.append(column_info)
            
            if not columns_to_merge:
                logger.warning(f"Khong tim thay cot nao cho nhom {group_name} voi indices {column_indices}")
                continue
            
            # Sắp xếp theo thứ tự cột
            columns_to_merge.sort(key=lambda x: x['column_index'])
            
            # Gộp các cột theo chiều ngang
            merged_image = np.hstack([col['image'] for col in columns_to_merge])
            
            # Tạo tên file
            column_numbers = [str(col['column_index']) for col in columns_to_merge]
            filename = f"{table_name}_columns_{'_'.join(column_numbers)}_{group_name}.jpg"
            filepath = os.path.join(self.merged_columns_dir, filename)
            
            # Lưu file
            cv2.imwrite(filepath, merged_image)
            saved_files.append(filepath)
            
            logger.info(f"Da luu nhom cot {group_name} (cot {', '.join(column_numbers)}): {filename}")
        
        return saved_files
    
    def process_image(self, image_path: str, 
                     save_individual: bool = True,
                     column_groups: Optional[Dict[str, List[int]]] = None,
                     max_tables: int = 3) -> Dict[str, Any]:
        """Xử lý ảnh và trích xuất cột từ tối đa 3 bảng
        
        Args:
            image_path: Đường dẫn ảnh (có thể là đường dẫn đầy đủ hoặc tên file trong input_dir)
            save_individual: Có lưu từng cột riêng không
            column_groups: Dict định nghĩa nhóm cột cần gộp
            max_tables: Số lượng bảng tối đa cần xử lý (mặc định: 3)
            
        Returns:
            Dict: Kết quả xử lý
        """
        logger.info(f"Bat dau xu ly anh: {image_path}")
        
        # Xử lý đường dẫn ảnh
        if os.path.isabs(image_path):
            full_image_path = image_path
        else:
            full_image_path = os.path.join(self.input_dir, image_path)
        
        # Đọc ảnh
        image = cv2.imread(full_image_path)
        if image is None:
            logger.error(f"Không thể đọc ảnh: {full_image_path}")
            return {"success": False, "error": f"Cannot read image: {full_image_path}"}
        
        logger.info(f"Da doc anh kich thuoc: {image.shape[1]}x{image.shape[0]} pixels")
        
        # BƯỚC 1: Sử dụng AdvancedTableExtractor để tìm bảng
        logger.info("BUOC 1: Tim bang trong anh...")
        tables = self.detect_table(image)
        
        if not tables:
            logger.warning("Khong phat hien duoc bang nao trong anh")
            return {"success": False, "error": "No tables detected"}
        
        # Giới hạn số lượng bảng
        if len(tables) > max_tables:
            logger.info(f"Tim thay {len(tables)} bang, chi xu ly {max_tables} bang dau")
            tables = tables[:max_tables]
        else:
            logger.info(f"Tim thay {len(tables)} bang de xu ly")
        
        result = {
            "success": True,
            "image_path": image_path,
            "total_tables_found": len(tables),
            "tables_processed": 0,
            "individual_files": [],
            "merged_files": [],
            "tables_info": []
        }
        
        # BƯỚC 2: Crop và xử lý từng bảng
        for table_idx, (x1, y1, x2, y2) in enumerate(tables):
            table_name = f"table_{table_idx+1:02d}"
            w, h = x2 - x1, y2 - y1
            
            logger.info(f"📊 BƯỚC 2.{table_idx+1}: Xử lý bảng {table_idx+1}")
            logger.info(f"   🔲 Vị trí bảng: x={x1}-{x2}, y={y1}-{y2}, size={w}x{h}")
            
            # Crop bảng từ ảnh gốc
            table_image = image[y1:y2, x1:x2].copy()
            
            # Lưu ảnh bảng đã crop để debug
            table_debug_path = os.path.join(self.debug_dir, f"{table_name}_cropped.jpg")
            cv2.imwrite(table_debug_path, table_image)
            logger.info(f"   💾 Đã lưu bảng crop: {table_debug_path}")
            
            # BƯỚC 3: Trích xuất cột từ bảng đã crop
            logger.info(f"   🔍 BƯỚC 3.{table_idx+1}: Trích xuất cột từ bảng {table_idx+1}...")
            columns_info = self.extract_columns_from_table(table_image, table_name)
            
            if not columns_info:
                logger.warning(f"   ❌ Không trích xuất được cột nào từ bảng {table_idx+1}")
                continue
            
            logger.info(f"   ✅ Đã trích xuất {len(columns_info)} cột từ bảng {table_idx+1}")
            
            table_result = {
                "table_index": table_idx + 1,
                "table_name": table_name,
                "bbox": (x1, y1, x2, y2),
                "cropped_size": (w, h),
                "columns_count": len(columns_info),
                "individual_files": [],
                "merged_files": []
            }
            
            # BƯỚC 4: Lưu từng cột riêng biệt
            if save_individual:
                logger.info(f"   💾 BƯỚC 4.{table_idx+1}: Lưu {len(columns_info)} cột riêng biệt...")
                individual_files = self.save_individual_columns(columns_info, table_name)
                table_result["individual_files"] = individual_files
                result["individual_files"].extend(individual_files)
                logger.info(f"   ✅ Đã lưu {len(individual_files)} file cột riêng")
            
            # BƯỚC 5: Lưu các cột đã gộp
            if column_groups:
                logger.info(f"   🔗 BƯỚC 5.{table_idx+1}: Gộp cột theo nhóm...")
                merged_files = self.save_merged_columns(columns_info, table_name, column_groups)
                table_result["merged_files"] = merged_files
                result["merged_files"].extend(merged_files)
                logger.info(f"   ✅ Đã lưu {len(merged_files)} file cột gộp")
            
            result["tables_info"].append(table_result)
            result["tables_processed"] += 1
            
            logger.info(f"✅ Hoàn thành xử lý bảng {table_idx+1}/{len(tables)}")
        
        # Tổng kết
        logger.info(f"🎉 HOÀN THÀNH XỬ LÝ:")
        logger.info(f"   📊 Tổng số bảng xử lý: {result['tables_processed']}/{result['total_tables_found']}")
        logger.info(f"   📁 File cột riêng: {len(result['individual_files'])}")
        logger.info(f"   📁 File cột gộp: {len(result['merged_files'])}")
        
        return result

def main():
    """Hàm chính để test AdvancedColumnExtractor"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Trích xuất cột từ bảng trong ảnh')
    parser.add_argument('image_path', help='Đường dẫn ảnh')
    parser.add_argument('--input-dir', default='input', help='Thư mục chứa ảnh')
    parser.add_argument('--output-dir', default='output/columns', help='Thư mục lưu kết quả')
    parser.add_argument('--debug-dir', default='debug/columns', help='Thư mục lưu debug')
    parser.add_argument('--max-tables', type=int, default=3, help='Số lượng bảng tối đa (mặc định: 3)')
    
    args = parser.parse_args()
    
    # Khởi tạo extractor
    extractor = AdvancedColumnExtractor(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        debug_dir=args.debug_dir
    )
    
    # Định nghĩa nhóm cột theo yêu cầu
    column_groups = {
        "first_two": [1, 2],     # Cột 1 và 2 thành 1 file
        "third": [3],            # Cột 3 thành file riêng
        "fourth": [4],           # Cột 4 thành file riêng
        "last_columns": [5, 6, 7]  # Cột 5, 6, 7 thành 1 file
    }
    
    print(f"🚀 Trích xuất cột từ {args.image_path}")
    print(f"📊 Tối đa {args.max_tables} bảng")
    print(f"🔗 Nhóm cột: {column_groups}")
    
    # Xử lý ảnh
    result = extractor.process_image(
        image_path=args.image_path,
        save_individual=True,
        column_groups=column_groups,
        max_tables=args.max_tables
    )
    
    # In kết quả
    if result["success"]:
        print(f"\n✅ Kết quả xử lý:")
        print(f"   📊 Số bảng xử lý: {result['tables_processed']}/{result['total_tables_found']}")
        print(f"   📁 File cột riêng: {len(result['individual_files'])}")
        print(f"   📁 File cột gộp: {len(result['merged_files'])}")
        
        for table_info in result["tables_info"]:
            print(f"\n   📊 {table_info['table_name']}:")
            print(f"      🔲 Vị trí: {table_info['bbox']}")
            print(f"      📏 Kích thước: {table_info['cropped_size']}")
            print(f"      📄 Số cột: {table_info['columns_count']}")
    else:
        print(f"❌ Lỗi: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()