#!/usr/bin/env python3
"""
Create macOS Application Icon for Requirements to Test
Generates a high-resolution icon with a checklist design
"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_icon():
    """Create a modern icon for Requirements to Test"""

    # Create high-resolution image for icon (1024x1024 for macOS)
    size = 1024
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background with rounded corners and gradient effect
    margin = 80
    bg_rect = [margin, margin, size - margin, size - margin]

    # Draw rounded rectangle background
    corner_radius = 120
    draw.rounded_rectangle(bg_rect, corner_radius,
                           fill=(45, 55, 72, 255))  # Dark blue-gray

    # Add subtle border
    border_margin = margin - 10
    border_rect = [
        border_margin, border_margin, size - border_margin,
        size - border_margin
    ]
    draw.rounded_rectangle(border_rect,
                           corner_radius + 10,
                           outline=(200, 200, 200, 100),
                           width=8)

    # Draw a checklist sheet on the card
    sheet_w = 800
    sheet_h = 760
    sheet_x0 = (size - sheet_w) // 2
    sheet_y0 = (size - sheet_h) // 2 + 20
    sheet_x1 = sheet_x0 + sheet_w
    sheet_y1 = sheet_y0 + sheet_h

    # Sheet drop shadow
    shadow_offset = 14
    draw.rounded_rectangle(
        [sheet_x0 + shadow_offset, sheet_y0 + shadow_offset, sheet_x1 + shadow_offset, sheet_y1 + shadow_offset],
        40,
        fill=(0, 0, 0, 60),
    )

    # Paper sheet
    draw.rounded_rectangle([sheet_x0, sheet_y0, sheet_x1, sheet_y1], 36, fill=(255, 255, 255, 255))

    # Top header strip
    header_h = 70
    draw.rounded_rectangle([sheet_x0 + 24, sheet_y0 + 24, sheet_x1 - 24, sheet_y0 + 24 + header_h], 18, fill=(232, 238, 246, 255))

    # Checklist rows
    rows = 8
    row_gap = 76
    start_y = sheet_y0 + 150
    left_pad = 48
    checkbox_size = 48
    text_gap = 24
    text_height = 20
    text_color = (228, 234, 242, 255)

    for i in range(rows):
        y = start_y + i * row_gap
        # Checkbox
        cb_x0 = sheet_x0 + left_pad
        cb_y0 = y - checkbox_size // 2
        cb_x1 = cb_x0 + checkbox_size
        cb_y1 = cb_y0 + checkbox_size
        draw.rounded_rectangle([cb_x0, cb_y0, cb_x1, cb_y1], 10, outline=(140, 150, 165, 255), width=6, fill=(250, 252, 255, 255))

        # Check some rows
        if i in (0, 1, 3, 5):
            # Draw a green checkmark
            check_color = (34, 197, 94, 255)  # green
            # Coordinates for a stylized check
            cx0 = cb_x0 + 10
            cy0 = cb_y0 + checkbox_size // 2
            cx1 = cb_x0 + checkbox_size // 2
            cy1 = cb_y0 + checkbox_size - 12
            cx2 = cb_x1 - 10
            cy2 = cb_y0 + 12
            draw.line([(cx0, cy0), (cx1, cy1)], fill=check_color, width=10)
            draw.line([(cx1, cy1), (cx2, cy2)], fill=check_color, width=10)

        # Text lines to the right of checkbox
        tx0 = cb_x1 + text_gap
        tx1 = sheet_x1 - left_pad
        # Primary long line
        draw.rounded_rectangle([tx0, y - text_height // 2, tx1, y - text_height // 2 + text_height], 10, fill=text_color)
        # Secondary shorter line below for rhythm
        sub_y = y + 22
        draw.rounded_rectangle([tx0, sub_y - 8, tx0 + (tx1 - tx0) * 0.55, sub_y + 8], 8, fill=(236, 240, 247, 255))

    return img


def create_icon_set():
    """Create a complete icon set for macOS"""

    base_icon = create_icon()

    # Icon sizes for macOS
    sizes = [16, 32, 64, 128, 256, 512, 1024]

    # Create icons directory
    if not os.path.exists("icons"):
        os.makedirs("icons")

    for size in sizes:
        # Resize image with high quality
        resized = base_icon.resize((size, size), Image.Resampling.LANCZOS)

        # Save as PNG
        filename = f"icons/requirements_to_test_{size}x{size}.png"
        resized.save(filename, "PNG")
        print(f"Created {filename}")

    # Save the main icon
    base_icon.save("icons/requirements_to_test.png", "PNG")
    print("Created icons/requirements_to_test.png")

    # Create ICO file for cross-platform compatibility
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128),
                 (256, 256)]
    ico_images = []

    for size in ico_sizes:
        resized = base_icon.resize(size, Image.Resampling.LANCZOS)
        ico_images.append(resized)

    # Save as ICO
    ico_images[0].save("icons/requirements_to_test.ico", format="ICO", sizes=ico_sizes)
    print("Created icons/requirements_to_test.ico")

    print("\nIcon set created successfully!")
    print("For macOS app bundle, use the PNG files.")
    print("For cross-platform compatibility, use the ICO file.")


if __name__ == "__main__":
    create_icon_set()
