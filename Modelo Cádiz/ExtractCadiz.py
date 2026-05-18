import os
from PIL import Image

def main():
    # Targets the local PNG directly
    image_path = "Cádiz_pattern.png"
    
    if not os.path.exists(image_path):
        if os.path.exists("Cádiz_pattern.jpg"):
            image_path = "Cádiz_pattern.jpg"
        else:
            print(f"Error: Could not find {image_path}")
            return

    img = Image.open(image_path)
    img_w, img_h = img.size

    output_dir = "cadiz_extracted_perfect"
    os.makedirs(output_dir, exist_ok=True)

    columns = 12
    rows = 4

    # Calculate base mathematical blocks
    base_w = img_w / columns
    base_h = img_h / rows

    # --- FINE-TUNING SLIDERS ---
    # Increase these pixel values if you still see background bits on any side.
    # Decrease them if the card text/numbers are being cut too close.
    trim_left = 6
    trim_right = 6
    trim_top = 4
    trim_bottom = 4
    # ---------------------------

    suits = ["oros", "copas", "espadas", "bastos"]

    print(f"Image Canvas Size: {img_w}x{img_h}")
    print(f"Slicing cards into '{output_dir}/' with custom margins...")

    for row_idx, suit in enumerate(suits):
        for col_idx in range(columns):
            # Calculate raw structural grid boundaries
            raw_left = col_idx * base_w
            raw_top = row_idx * base_h
            raw_right = (col_idx + 1) * base_w
            raw_bottom = (row_idx + 1) * base_h
            
            # Collapse the crop window inward away from gutters/shadows
            left = int(raw_left + trim_left)
            top = int(raw_top + trim_top)
            right = int(raw_right - trim_right)
            bottom = int(raw_bottom - trim_bottom)
            
            # Ensure boundaries are logical before cropping
            if right > left and bottom > top:
                card = img.crop((left, top, right, bottom))
                card_num = col_idx + 1
                card.save(os.path.join(output_dir, f"{suit}_{card_num}.png"))
            else:
                print(f"Skipping crop error at Row {row_idx}, Col {col_idx}")

    print("Success! Slicing pipeline completed cleanly.")

if __name__ == "__main__":
    main()