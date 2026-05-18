import os
from PIL import Image

def find_card_bounding_boxes(image_path):
    img = Image.open(image_path)
    rgb_img = img.convert("RGB")
    w, h = img.size
    
    # Threshold to determine if a pixel is part of the black background
    # (Black is close to 0, 0, 0)
    def is_black(pixel):
        return sum(pixel) < 30

    # 1. Find all vertical rows by scanning Y-axis profile
    row_active = False
    row_ranges = []
    start_y = None
    
    # We sample a vertical strip near the middle of the image to find rows safely
    sample_x = w // 2
    for y in range(h):
        # Check a small horizontal span around the center line to handle noise
        pixels = [rgb_img.getpixel((x, y)) for x in range(sample_x - 10, sample_x + 10)]
        all_black = all(is_black(p) for p in pixels)
        
        if not all_black and not row_active:
            start_y = y
            row_active = True
        elif all_black and row_active:
            row_ranges.append((start_y, y))
            row_active = False
    if row_active:
        row_ranges.append((start_y, h))

    # 2. For each row, scan horizontally to locate the card columns
    grid_boxes = [] # Will hold 5 rows of data (4 main suit rows + 1 bottom row)
    
    for r_start, r_end in row_ranges:
        mid_y = (r_start + r_end) // 2
        col_active = False
        col_ranges = []
        start_x = None
        
        for x in range(w):
            # Sample a tiny vertical slice inside the current row height
            pixels = [rgb_img.getpixel((x, y)) for y in range(mid_y - 10, mid_y + 10)]
            all_black = all(is_black(p) for p in pixels)
            
            if not all_black and not col_active:
                start_x = x
                col_active = True
            elif all_black and col_active:
                col_ranges.append((start_x, x))
                col_active = False
        if col_active:
            col_ranges.append((start_x, w))
            
        # Pair the specific X coordinates found with this row's Y coordinates
        row_boxes = [(sx, r_start, ex, r_end) for sx, ex in col_ranges]
        grid_boxes.append(row_boxes)
        
    return img, grid_boxes

def main():
    image_path = "Baraja_española_completa.png"
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found in current directory.")
        return
        
    img, grid_boxes = find_card_bounding_boxes(image_path)
    
    output_dir = "extracted_cards"
    os.makedirs(output_dir, exist_ok=True)
    
    suits = ["oros", "copas", "espadas", "bastos"]
    
    # Shave 1 pixel off inside the detected bounding boxes to ensure clean white edges
    pad = 1
    
    print("Dynamically calculated card segments. Slicing...")
    
    # Extract the 4 main suit rows (rows 0 to 3)
    for row_idx in range(min(4, len(grid_boxes))):
        suit_name = suits[row_idx]
        cards_in_row = grid_boxes[row_idx]
        
        for col_idx, (left, top, right, bottom) in enumerate(cards_in_row):
            # Bound checks to make sure padding doesn't cross inside out
            if (right - left) > 5 and (bottom - top) > 5:
                card = img.crop((left + pad, top + pad, right - pad, bottom - pad))
                card_num = col_idx + 1
                card.save(os.path.join(output_dir, f"{suit_name}_{card_num}.png"))

    # Extract the bottom extra row items (row index 4)
    if len(grid_boxes) > 4:
        bottom_row = grid_boxes[4]
        
        # Element 1: Blank card
        if len(bottom_row) > 0:
            l, t, r, b = bottom_row[0]
            blank = img.crop((l + pad, t + pad, r - pad, b - pad))
            blank.save(os.path.join(output_dir, "card_blank.png"))
            
        # Element 2: Card Back pattern
        if len(bottom_row) > 1:
            l, t, r, b = bottom_row[1]
            back = img.crop((l + pad, t + pad, r - pad, b - pad))
            back.save(os.path.join(output_dir, "card_back.png"))

    print(f"Extraction complete! Clean, pixel-perfect cards saved to '{output_dir}/'.")

if __name__ == "__main__":
    main()