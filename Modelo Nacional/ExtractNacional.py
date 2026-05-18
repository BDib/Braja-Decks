import os
from PIL import Image

def main():
    # Target your local image asset
    image_path = "Spanish_National_pattern.png"
    if not os.path.exists(image_path):
        if os.path.exists("Spanish_National_pattern.jpg"):
            image_path = "Spanish_National_pattern.jpg"
        else:
            print(f"Error: Could not find {image_path}")
            return

    img = Image.open(image_path)
    img_w, img_h = img.size

    output_dir = "national_extracted_perfect"
    os.makedirs(output_dir, exist_ok=True)

    columns = 12
    rows = 4

    # Establish the absolute mathematical block size per card slot
    slot_w = img_w / columns
    slot_h = img_h / rows

    # --- THE MANUAL TRIMMING CONFIGURATION ---
    # Adjust these pixel values to control the crop border framing.
    # Increasing a value shaves MORE off that side of the card.
    trim_left = 6
    trim_right = 6
    trim_top = 5
    trim_bottom = 5
    # ------------------------------------------

    # Specific row order matching the Spanish National pattern asset
    suits = ["oros", "espadas", "copas", "bastos"]

    print(f"Canvas size detected: {img_w}x{img_h}")
    print(f"Slicing cards cleanly into '{output_dir}/'...")

    for row_idx, suit in enumerate(suits):
        for col_idx in range(columns):
            # Calculate the un-padded raw coordinate boundaries for the grid slot
            raw_left = col_idx * slot_w
            raw_top = row_idx * slot_h
            raw_right = (col_idx + 1) * slot_w
            raw_bottom = (row_idx + 1) * slot_h
            
            # Collapse the crop frame inward to completely isolate the white card face
            left = int(raw_left + trim_left)
            top = int(raw_top + trim_top)
            right = int(raw_right - trim_right)
            bottom = int(raw_bottom - trim_bottom)
            
            # Safe crop execution
            if right > left and bottom > top:
                card = img.crop((left, top, right, bottom))
                card_num = col_idx + 1
                card.save(os.path.join(output_dir, f"{suit}_{card_num}.png"))

    print("Done! Slicing completed using a safe normalized grid.")

if __name__ == "__main__":
    main()