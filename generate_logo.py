"""Generate a minimalistic pizza logo with a bite taken out."""

from PIL import Image, ImageDraw
import math


def create_pizza_logo(size=256, output_path="logo.png"):
    """Create a circular pizza with a bite taken out and save as PNG."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    center = size // 2
    radius = size // 2 - 10

    # Pizza base (circle)
    draw.ellipse(
        [center - radius, center - radius, center + radius, center + radius],
        fill="#F4A460",  # Sandy brown for pizza
        outline="#D2691E",  # Chocolate outline
        width=3,
    )

    # Toppings (small circles for pepperoni)
    topping_positions = [
        (center - 30, center - 30),
        (center + 20, center - 40),
        (center - 40, center + 20),
        (center + 30, center + 30),
        (center, center - 50),
        (center - 50, center),
        (center + 40, center),
    ]
    for x, y in topping_positions:
        draw.ellipse([x - 8, y - 8, x + 8, y + 8], fill="#C41E3A")

    # Create bite effect (cut out a circular chunk on the top-right)
    bite_mask = Image.new("L", (size, size), 0)
    bite_draw = ImageDraw.Draw(bite_mask)

    # Full pizza circle
    bite_draw.ellipse(
        [center - radius, center - radius, center + radius, center + radius],
        fill=255,
    )

    # Bite circle (remove this part)
    bite_x = center + radius // 2
    bite_y = center - radius // 2
    bite_radius = radius // 2
    bite_draw.ellipse(
        [
            bite_x - bite_radius,
            bite_y - bite_radius,
            bite_x + bite_radius,
            bite_y + bite_radius,
        ],
        fill=0,
    )

    # Apply mask
    img.putalpha(bite_mask)

    img.save(output_path, "PNG")
    print(f"Pizza logo saved to {output_path}")


if __name__ == "__main__":
    create_pizza_logo()
