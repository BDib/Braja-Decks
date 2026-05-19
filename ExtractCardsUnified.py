import cv2
import numpy as np
import os

def extract_cards(image_path, output_dir, suit_names=None, cards_per_row=12):
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found.")
        return

    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read {image_path}.")
        return

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Use a combination of blurring and adaptive thresholding to handle different backgrounds
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Try different thresholding methods
    # For dark backgrounds, simple thresholding might work.
    # For others, adaptive might be better.
    # We'll use Canny edge detection as it's often more robust for finding card edges.
    edged = cv2.Canny(blurred, 30, 150)

    # Thresholding might be better for solid backgrounds
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Also try morphological operations to emphasize card shapes
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Combine edged and morph for better detection
    combined = cv2.bitwise_or(edged, cv2.bitwise_not(morph))

    # Pre-calculate dilated edges for later use
    kernel_dilate = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated = cv2.dilate(edged, kernel_dilate, iterations=1)

    # Try different approaches if first one fails
    # Braja has black background, so objects are light on dark background
    # Others might have white background, so objects are dark on light background

    # For white background with borders, dilated edges are often best
    # but we should be careful about which one we use first.
    # Let's try combined first as it was most successful for all
    contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # If too few, try dilated
    if len(contours) < 10:
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # If too few, try thresholded image directly
    if len(contours) < 10:
         contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # If no contours found, try inverting or using just edges
    if len(contours) < 10:
         # Sample corners of original image to see if it's black or white background
         corner_sample = np.mean([gray[0,0], gray[0,-1], gray[-1,0], gray[-1,-1]])
         if corner_sample < 50: # Black background
              _, thresh_inv = cv2.threshold(blurred, 10, 255, cv2.THRESH_BINARY)
              contours, _ = cv2.findContours(thresh_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
         else:
              contours, _ = cv2.findContours(cv2.bitwise_not(thresh), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


    os.makedirs(output_dir, exist_ok=True)

    # Filter contours by area to ignore noise
    img_area = img.shape[0] * img.shape[1]
    min_card_area = img_area / 1000
    max_card_area = img_area / 5

    card_contours = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if min_card_area < area < max_card_area:
            # Check aspect ratio
            x, y, w, h = cv2.boundingRect(cnt)
            if h == 0: continue
            aspect_ratio = float(w)/h
            # Playing cards are usually 0.6 to 0.8 aspect ratio, or vice-versa if rotated
            if 0.4 < aspect_ratio < 2.5:
                card_contours.append(cnt)

    print(f"Found {len(card_contours)} potential cards in {image_path}")

    # Sort cards by Y then X to group them into rows
    # We'll use a more sophisticated sorting later if needed
    bounding_boxes = [cv2.boundingRect(c) for c in card_contours]

    # To name them correctly, we need to sort them into a grid
    # Let's find the average height to help with row grouping
    if not bounding_boxes:
        print("No cards found.")
        return

    avg_height = sum([b[3] for b in bounding_boxes]) / len(bounding_boxes)

    # Sort primarily by Y, with some tolerance
    bounding_boxes.sort(key=lambda b: b[1] + b[3]/2)

    # Group by rows and sort each row by X
    rows = []
    if bounding_boxes:
        current_row = [bounding_boxes[0]]
        for i in range(1, len(bounding_boxes)):
            # Check if this box is in the same row as the previous one
            # Use center Y for more robustness
            prev_center_y = current_row[-1][1] + current_row[-1][3]/2
            curr_center_y = bounding_boxes[i][1] + bounding_boxes[i][3]/2

            if abs(curr_center_y - prev_center_y) < avg_height * 0.5:
                current_row.append(bounding_boxes[i])
            else:
                current_row.sort(key=lambda b: b[0])
                rows.append(current_row)
                current_row = [bounding_boxes[i]]
        current_row.sort(key=lambda b: b[0])
        rows.append(current_row)

    # Flatten rows back to sorted list
    final_sorted_boxes = [box for row in rows for box in row]

    # Map back to contours
    sorted_contours = []
    for box in final_sorted_boxes:
        # Find contour with this bounding box
        for cnt in card_contours:
            if cv2.boundingRect(cnt) == box:
                sorted_contours.append(cnt)
                break

    for i, cnt in enumerate(sorted_contours):
        # Get rotated rectangle
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)

        # We need to sort the points in a consistent order for perspective transform
        # Top-left, top-right, bottom-right, bottom-left
        def order_points(pts):
            rect = np.zeros((4, 2), dtype="float32")
            s = pts.sum(axis=1)
            rect[0] = pts[np.argmin(s)]
            rect[2] = pts[np.argmax(s)]
            diff = np.diff(pts, axis=1)
            rect[1] = pts[np.argmin(diff)]
            rect[3] = pts[np.argmax(diff)]
            return rect

        src_pts = order_points(box)

        # Calculate new width and height
        (tl, tr, br, bl) = src_pts
        width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        max_width = max(int(width_a), int(width_b))

        height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        max_height = max(int(height_a), int(height_b))

        dst_pts = np.array([
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1]], dtype="float32")

        M = cv2.getPerspectiveTransform(src_pts, dst_pts)
        warped = cv2.warpPerspective(img, M, (max_width, max_height))

        # If warped is rotated 90 degrees compared to typical card aspect ratio, fix it
        if warped.shape[1] > warped.shape[0]:
            warped = cv2.rotate(warped, cv2.ROTATE_90_CLOCKWISE)

        # Slight crop to remove any border residue
        h_w, w_w = warped.shape[:2]
        crop_px = 4
        if h_w > 2*crop_px and w_w > 2*crop_px:
            warped = warped[crop_px:-crop_px, crop_px:-crop_px]

        # Advanced naming if suit_names provided
        if suit_names:
            row_idx = i // cards_per_row
            col_idx = i % cards_per_row
            if row_idx < len(suit_names):
                suit = suit_names[row_idx]
                filename = f"{suit}_{col_idx+1:02d}.png"
            else:
                filename = f"extra_{i - len(suit_names)*cards_per_row + 1:02d}.png"
        else:
            filename = f"card_{i+1:02d}.png"

        cv2.imwrite(os.path.join(output_dir, filename), warped)

    print(f"Saved {len(sorted_contours)} cards to {output_dir}")

if __name__ == "__main__":
    # Test on the three images
    # Braja Espanola: 10 columns, suits: oros, copas, espadas, bastos
    extract_cards("Braja Espanola/Baraja_española_completa.png", "unified_braja",
                  suit_names=["oros", "copas", "espadas", "bastos"], cards_per_row=10)

    # Modelo Cádiz: 12 columns, suits: oros, copas, espadas, bastos
    # Actually it found 45 cards, and looks like 12 columns might be wrong or it's missing some
    # Let's adjust to what it actually finds to get better naming
    extract_cards("Modelo Cádiz/Cádiz_pattern.png", "unified_cadiz",
                  suit_names=["oros", "copas", "espadas", "bastos"], cards_per_row=12)

    # Modelo Nacional: 12 columns, suits: oros, espadas, copas, bastos
    extract_cards("Modelo Nacional/Spanish_National_pattern.png", "unified_nacional",
                  suit_names=["oros", "espadas", "copas", "bastos"], cards_per_row=12)
