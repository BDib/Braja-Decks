import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from PIL import Image

def main():
    # Change this to whatever pattern sheet you want to inspect
    image_path = "Spanish_National_pattern.png" 

    img = Image.open(image_path)
    w, h = img.size

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(img)

    # Put a grid line every 50 pixels for precise coordinate reading
    ax.xaxis.set_major_locator(ticker.MultipleLocator(50))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(50))
    
    # Add minor ticks every 10 pixels for fine-tuning
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(10))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(10))

    ax.grid(True, which='both', color='red', linestyle='-', linewidth=0.5, alpha=0.7)
    
    print(f"Loaded {image_path} ({w}x{h})")
    print("Close the window when you're done inspecting the boundaries.")
    plt.show()

if __name__ == "__main__":
    main()