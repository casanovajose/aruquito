#!/usr/bin/env python
"""Generate ArUco markers to PDF."""
import argparse
import math
import sys

import cv2

def main():
    parser = argparse.ArgumentParser(description='Generate ArUco markers to PDF')
    parser.add_argument('--id', type=int, default=5, help='Max marker ID')
    parser.add_argument('--copies', type=int, default=1, help='Copies of each marker')
    parser.add_argument('--size', type=int, default=50, help='Marker size in pixels')
    
    args = parser.parse_args()
    max_id = args.id
    copies = args.copies
    size = args.size
    
    try:
        from PIL import Image
        has_pil = True
    except ImportError:
        has_pil = False
        print("⚠ PIL not available. Install with: pip install pillow", file=sys.stderr)
        sys.exit(1)
    
    if max_id < 0:
        print('ERROR: --id must be >= 0', file=sys.stderr)
        sys.exit(1)
    if copies < 1:
        print('ERROR: --copies must be >= 1', file=sys.stderr)
        sys.exit(1)
    if size < 16:
        print('ERROR: --size must be >= 16', file=sys.stderr)
        sys.exit(1)

    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    dictionary_size = int(aruco_dict.bytesList.shape[0])
    if max_id >= dictionary_size:
        print(f'ERROR: --id must be <= {dictionary_size - 1} for DICT_4X4_50', file=sys.stderr)
        sys.exit(1)

    marker_images = []
    for marker_id in range(max_id + 1):
        for _ in range(copies):
            marker_img = cv2.aruco.generateImageMarker(aruco_dict, marker_id, size)
            marker_img = cv2.copyMakeBorder(
                marker_img,
                10,
                10,
                10,
                10,
                cv2.BORDER_CONSTANT,
                value=255,
            )
            marker_images.append(marker_img)
    
    print(f"Generated {len(marker_images)} markers")
    
    # Generate PDF pages
    cols, rows = 4, 5
    markers_per_page = cols * rows
    num_pages = math.ceil(len(marker_images) / markers_per_page)
    
    page_images = []
    
    for page_num in range(num_pages):
        # Create blank A4 page (2480x3508 at 300dpi)
        page = Image.new('RGB', (2480, 3508), color='white')
        
        start_idx = page_num * markers_per_page
        end_idx = min(start_idx + markers_per_page, len(marker_images))
        
        margin = 50
        spacing = 30
        marker_display_size = (2480 - 2*margin - (cols-1)*spacing) // cols
        
        for i, marker_idx in enumerate(range(start_idx, end_idx)):
            row = i // cols
            col = i % cols
            
            x = margin + col * (marker_display_size + spacing)
            y = margin + row * (marker_display_size + spacing)
            
            # Marker images are single-channel grayscale.
            marker_cv = marker_images[marker_idx]
            marker_pil = Image.fromarray(marker_cv)
            marker_pil = marker_pil.resize((marker_display_size, marker_display_size), Image.Resampling.LANCZOS)
            page.paste(marker_pil, (x, y))
        
        page_images.append(page)
    
    # Save as multi-page PDF
    output_pdf = "aruco_markers.pdf"
    page_images[0].save(output_pdf, save_all=True, append_images=page_images[1:])
    print(f"✓ Generated {output_pdf} ({num_pages} pages, {len(marker_images)} markers)")

if __name__ == '__main__':
    main()
