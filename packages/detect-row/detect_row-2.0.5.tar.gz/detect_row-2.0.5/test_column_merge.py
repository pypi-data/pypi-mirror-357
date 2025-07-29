import os
from pathlib import Path
import cv2
import logging
from detect_row.advanced_column_extractor import AdvancedColumnExtractor

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_column_merge():
    """Test tính năng merge cột từ các bảng trong thư mục tables/"""
    
    # Khởi tạo column extractor
    extractor = AdvancedColumnExtractor(
        input_dir="tables",
        output_dir="output/columns",
        debug_dir="debug/columns",
        min_column_width=30
    )
    
    # Tạo thư mục output cho các cột đã merge
    merged_dir = "columns"
    os.makedirs(merged_dir, exist_ok=True)
    
    # Định nghĩa các nhóm cột cần merge
    column_groups = {
        "columns_123": [1, 2, 3],  # Merge cột 1,2,3
        "columns_124": [1, 2, 4]   # Merge cột 1,2,4
    }
    
    # Lấy danh sách các file bảng trong thư mục tables/
    table_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png']:
        table_files.extend(Path("tables").glob(ext))
    
    if not table_files:
        logger.error("Không tìm thấy file ảnh nào trong thư mục tables/")
        return
    
    logger.info(f"Tìm thấy {len(table_files)} file bảng")
    
    # Xử lý từng bảng
    for table_file in table_files:
        logger.info(f"\n{'='*50}")
        logger.info(f"Xử lý bảng: {table_file}")
        
        # Đọc ảnh bảng
        table_image = cv2.imread(str(table_file))
        if table_image is None:
            logger.error(f"Không thể đọc file: {table_file}")
            continue
            
        # Lấy tên file không có phần mở rộng
        table_name = table_file.stem
        
        # Trích xuất các cột từ bảng
        columns_info = extractor.extract_columns_from_table(table_image, table_name)
        
        if not columns_info:
            logger.warning(f"Không trích xuất được cột nào từ bảng {table_name}")
            continue
            
        logger.info(f"Đã trích xuất {len(columns_info)} cột")
        
        # Lưu debug thông tin các cột
        for col in columns_info:
            logger.info(f"Cột {col['column_index']}: x={col['x1']}-{col['x2']}, width={col['width']}px")
            
            # Lưu ảnh cột để debug
            debug_path = os.path.join("debug/columns", f"{table_name}_col_{col['column_index']}.jpg")
            cv2.imwrite(debug_path, col['image'])
        
        # Merge và lưu các nhóm cột
        merged_files = extractor.save_merged_columns(columns_info, table_name, column_groups)
        
        if merged_files:
            logger.info(f"\nĐã tạo {len(merged_files)} file cột đã merge:")
            for f in merged_files:
                # Copy file từ output/columns/merged_columns sang thư mục columns/
                target_path = os.path.join(merged_dir, os.path.basename(f))
                cv2.imwrite(target_path, cv2.imread(f))
                logger.info(f"- {target_path}")
        
        logger.info(f"{'='*50}\n")

if __name__ == "__main__":
    test_column_merge() 