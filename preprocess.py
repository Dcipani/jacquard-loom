from PIL import Image
import numpy as np
import colour


def rgb_to_oklab(rgb):
    rgb = np.array(rgb) / 255.0
    xyz = colour.sRGB_to_XYZ(rgb)
    return colour.XYZ_to_Oklab(xyz)


def resize_image(img, pixels_per_unit=3):
    width, height = img.size
    return img.resize(
        (width // pixels_per_unit, height // pixels_per_unit),
        Image.Resampling.NEAREST
    )


def quantize_two_colors(img_array, color_a, color_b):
    img_oklab = rgb_to_oklab(img_array)

    palette_rgb = np.array([color_a, color_b])
    palette_oklab = rgb_to_oklab(palette_rgb)

    diff = img_oklab[:, :, None, :] - palette_oklab[None, None, :, :]
    distances = np.sum(diff ** 2, axis=-1)

    nearest = np.argmin(distances, axis=-1)

    return palette_rgb[nearest]


def image_to_jacquard_matrix(input_path, color_a, color_b, pixels_per_unit=3):
    img = Image.open(input_path).convert("RGB")
    img_array = np.array(img)

    quantized = quantize_two_colors(
        img_array,
        color_a,
        color_b
    )

    # convert back to image for resizing
    quantized_img = Image.fromarray(
        quantized.astype(np.uint8)
    )
    resized_img = resize_image(
        quantized_img,
        pixels_per_unit
    )

    quantized = np.array(resized_img)

    resized_img.save("output.png")


    flat = quantized.reshape(-1, 3)

    unique, counts = np.unique(flat, axis=0, return_counts=True)

    if len(unique) != 2:
        raise ValueError("Expected exactly 2 colors after quantization")

    warp_idx = np.argmax(counts)
    weft_idx = 1 - warp_idx

    warp_color = tuple(unique[warp_idx])
    weft_color = tuple(unique[weft_idx])

    # 1 = warp visible
    # 0 = weft visible
    binary = np.all(quantized == warp_color, axis=-1).astype(np.uint8)

    return binary, warp_color, weft_color


if __name__ == "__main__":
    matrix, warp_color, weft_color = image_to_jacquard_matrix(
        "input.png",
        (20, 20, 20),
        (240, 238, 230)
    )

    print(matrix)
    print("warp color:", warp_color)
    print("weft color:", weft_color)
