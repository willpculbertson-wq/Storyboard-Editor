"""
make_icon.py -- generates the application icon and preview for Storyboard Editor.

Generates:
  - storyboard_editor.ico: Multi-resolution Windows icon (16, 24, 32, 48, 64, 128, 256)
    saved in BMP format for crisp alpha rendering on all Windows shell surfaces.
  - icon_preview.png: Visual preview displaying the 256 render alongside 64, 32, 24,
    and 16 actual-size renders on a mid-grey canvas.

Artwork:
  Visual novel storyline metaphor:
  - Rounded-square dark tile background (#1a1a1a to #111111).
  - Three landscape image panels staggered lower-left to upper-right.
    * Panel 1: Mountain landscape with warm golden sun (#eab308 highlight).
    * Panel 2: Character silhouette with evening violet backlight glow.
    * Panel 3: Crescent moon over night horizon with sea reflection.
  - Accent blue (#3b82f6) sequential storyline path connecting the panels
    with round nodes (1 -> 2 -> 3) and terminating with an arrowhead.
  - At sizes 16, 24, and 32, simplified rendering uses solid slate panels
    with light borders and a thicker story path for maximum small-scale clarity.
"""

import math
import sys
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ICO_PATH = HERE / "storyboard_editor.ico"
PREVIEW_PATH = HERE / "icon_preview.png"

SIZES = [16, 24, 32, 48, 64, 128, 256]
PREVIEW_SIZES = [256, 64, 32, 24, 16]


def draw_arrow(d, tip, angle, length, width, fill):
    """Draw a filled triangular arrowhead at tip pointing in direction of angle."""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    back_x = tip[0] - length * cos_a
    back_y = tip[1] - length * sin_a
    left_x = back_x - width * 0.5 * sin_a
    left_y = back_y + width * 0.5 * cos_a
    right_x = back_x + width * 0.5 * sin_a
    right_y = back_y - width * 0.5 * cos_a
    d.polygon([tip, (left_x, left_y), (right_x, right_y)], fill=fill)


def render_icon(target_size):
    """
    Render icon for target_size using 4x supersampling and LANCZOS downsampling.
    Renders simplified artwork for sizes <= 32 (solid panels, thicker path).
    """
    S = target_size
    scale = 4
    SS = S * scale
    img = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))

    # 1. Dark tile background filling the canvas
    pad = max(1, int(0.02 * SS))
    radius = int(0.22 * SS)

    tile = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
    td = ImageDraw.Draw(tile)
    td.rounded_rectangle(
        [pad, pad, SS - 1 - pad, SS - 1 - pad],
        radius=radius,
        fill=(20, 20, 23, 255),
        outline=(42, 42, 48, 255),
        width=max(1, int(1.2 * scale)),
    )
    img = Image.alpha_composite(img, tile)
    d = ImageDraw.Draw(img)

    is_simplified = S <= 32

    if is_simplified:
        # Simplified mode: solid panels without tiny pictures, thicker path
        pw = int(0.36 * SS)
        ph = int(0.24 * SS)

        c1 = (int(0.25 * SS), int(0.74 * SS))
        c2 = (int(0.50 * SS), int(0.50 * SS))
        c3 = (int(0.75 * SS), int(0.26 * SS))
        centers = [c1, c2, c3]
        boxes = [(c[0] - pw // 2, c[1] - ph // 2, c[0] + pw // 2, c[1] + ph // 2) for c in centers]

        panel_rad = max(1, int(0.02 * SS))
        s_off = max(1, int(1.2 * scale))
        for box in boxes:
            d.rounded_rectangle(
                [box[0] + s_off, box[1] + s_off, box[2] + s_off, box[3] + s_off],
                radius=panel_rad,
                fill=(8, 8, 10, 140),
            )

        for box in boxes:
            d.rounded_rectangle(box, radius=panel_rad, fill=(45, 58, 82, 255))
            bw = max(1, int(0.85 * scale))
            d.rounded_rectangle(box, radius=panel_rad, outline=(230, 238, 250, 240), width=bw)

        blue = (59, 130, 246, 255)
        arrow_tip = (int(0.91 * SS), int(0.10 * SS))
        angle = math.atan2(arrow_tip[1] - c1[1], arrow_tip[0] - c1[0])

        if S == 16:
            path_w = int(1.3 * scale)
            node_r = int(1.3 * scale)
            arrow_len = int(2.8 * scale)
            arrow_w = int(2.2 * scale)
            d.line([c1, c2, c3, arrow_tip], fill=blue, width=path_w, joint="curve")
            draw_arrow(d, arrow_tip, angle, length=arrow_len, width=arrow_w, fill=blue)
            for c in centers:
                d.ellipse([c[0] - node_r, c[1] - node_r, c[0] + node_r, c[1] + node_r], fill=blue)
                d.ellipse(
                    [c[0] - int(0.4 * scale), c[1] - int(0.4 * scale), c[0] + int(0.4 * scale), c[1] + int(0.4 * scale)],
                    fill=(255, 255, 255, 255),
                )
        elif S == 24:
            path_w = int(1.5 * scale)
            node_r = int(1.6 * scale)
            arrow_len = int(3.8 * scale)
            arrow_w = int(2.8 * scale)
            d.line([c1, c2, c3, arrow_tip], fill=blue, width=path_w, joint="curve")
            draw_arrow(d, arrow_tip, angle, length=arrow_len, width=arrow_w, fill=blue)
            for c in centers:
                d.ellipse([c[0] - node_r, c[1] - node_r, c[0] + node_r, c[1] + node_r], fill=blue)
                d.ellipse(
                    [c[0] - int(0.6 * scale), c[1] - int(0.6 * scale), c[0] + int(0.6 * scale), c[1] + int(0.6 * scale)],
                    fill=(255, 255, 255, 255),
                )
        else:  # S == 32
            path_w = int(1.8 * scale)
            node_r = int(2.0 * scale)
            arrow_len = int(4.8 * scale)
            arrow_w = int(3.6 * scale)
            outline_w = path_w + max(2, int(1.5 * scale))
            d.line([c1, c2, c3, arrow_tip], fill=(12, 16, 26, 200), width=outline_w, joint="curve")
            d.line([c1, c2, c3, arrow_tip], fill=blue, width=path_w, joint="curve")
            draw_arrow(d, arrow_tip, angle, length=arrow_len, width=arrow_w, fill=blue)
            for c in centers:
                d.ellipse([c[0] - node_r, c[1] - node_r, c[0] + node_r, c[1] + node_r], fill=(12, 16, 26, 255))
                rim_w = max(1, int(0.8 * scale))
                d.ellipse(
                    [c[0] - node_r + rim_w, c[1] - node_r + rim_w, c[0] + node_r - rim_w, c[1] + node_r - rim_w],
                    fill=blue,
                )
                d.ellipse(
                    [c[0] - int(0.7 * scale), c[1] - int(0.7 * scale), c[0] + int(0.7 * scale), c[1] + int(0.7 * scale)],
                    fill=(255, 255, 255, 255),
                )

    else:
        # Detailed mode: 48, 64, 128, 256
        pw = int(0.36 * SS)
        ph = int(0.23 * SS)

        c1 = (int(0.26 * SS), int(0.72 * SS))
        c2 = (int(0.50 * SS), int(0.49 * SS))
        c3 = (int(0.74 * SS), int(0.27 * SS))
        centers = [c1, c2, c3]
        boxes = [(c[0] - pw // 2, c[1] - ph // 2, c[0] + pw // 2, c[1] + ph // 2) for c in centers]

        panel_rad = max(1, int(0.025 * SS))
        s_off_x = max(1, int(2.0 * scale * (S / 256.0)))
        s_off_y = max(1, int(3.0 * scale * (S / 256.0)))
        for box in boxes:
            d.rounded_rectangle(
                [box[0] + s_off_x, box[1] + s_off_y, box[2] + s_off_x, box[3] + s_off_y],
                radius=panel_rad,
                fill=(8, 8, 10, 150),
            )

        for i, box in enumerate(boxes):
            d.rounded_rectangle(box, radius=panel_rad, fill=(18, 22, 30, 255))
            inset = max(1, int(2.2 * scale * (S / 256.0)))
            ibox = [box[0] + inset, box[1] + inset, box[2] - inset, box[3] - inset]
            rad = max(1, int(1.8 * scale * (S / 256.0)))

            if i == 0:
                # Panel 1: Mountain landscape with warm golden sun (#eab308)
                d.rounded_rectangle(ibox, radius=rad, fill=(30, 41, 59, 255))
                sun_c = (box[0] + int(pw * 0.28), box[1] + int(ph * 0.32))
                sun_r = int(ph * 0.20)
                d.ellipse([sun_c[0] - sun_r, sun_c[1] - sun_r, sun_c[0] + sun_r, sun_c[1] + sun_r], fill=(234, 179, 8, 255))
                m1 = [(ibox[0], ibox[3]), (box[0] + int(pw * 0.48), box[1] + int(ph * 0.35)), (box[0] + int(pw * 0.88), ibox[3])]
                d.polygon(m1, fill=(71, 85, 105, 255))
                m2 = [(box[0] + int(pw * 0.32), ibox[3]), (box[0] + int(pw * 0.72), box[1] + int(ph * 0.46)), (ibox[2], ibox[3])]
                d.polygon(m2, fill=(100, 116, 139, 255))

            elif i == 1:
                # Panel 2: Character silhouette against evening glow
                d.rounded_rectangle(ibox, radius=rad, fill=(30, 27, 75, 255))
                glow_c = (box[0] + int(pw * 0.38), box[1] + int(ph * 0.44))
                glow_r = int(ph * 0.36)
                d.ellipse(
                    [glow_c[0] - int(pw * 0.28), glow_c[1] - glow_r, glow_c[0] + int(pw * 0.28), glow_c[1] + glow_r],
                    fill=(99, 102, 241, 220),
                )
                head_c = (box[0] + int(pw * 0.36), box[1] + int(ph * 0.36))
                head_r = int(ph * 0.17)
                d.ellipse([head_c[0] - head_r, head_c[1] - head_r, head_c[0] + head_r, head_c[1] + head_r], fill=(15, 23, 42, 255))
                sh_w = int(pw * 0.46)
                sh_top = head_c[1] + int(head_r * 0.7)
                # Top half of an ellipse, so the shoulders stop at the panel's bottom edge.
                sh_bottom = ibox[3] + (ibox[3] - sh_top)
                d.pieslice([head_c[0] - sh_w // 2, sh_top, head_c[0] + sh_w // 2, sh_bottom], 180, 360, fill=(15, 23, 42, 255))

            elif i == 2:
                # Panel 3: Moon over night horizon
                d.rounded_rectangle(ibox, radius=rad, fill=(15, 23, 42, 255))
                moon_c = (box[0] + int(pw * 0.28), box[1] + int(ph * 0.33))
                moon_r = int(ph * 0.18)
                d.ellipse([moon_c[0] - moon_r, moon_c[1] - moon_r, moon_c[0] + moon_r, moon_c[1] + moon_r], fill=(248, 250, 252, 255))
                crescent_bite = max(1, int(5 * scale * (S / 256.0)))
                d.ellipse(
                    [moon_c[0] - moon_r + crescent_bite, moon_c[1] - moon_r - crescent_bite // 2,
                     moon_c[0] + moon_r + crescent_bite, moon_c[1] + moon_r - crescent_bite // 2],
                    fill=(15, 23, 42, 255),
                )
                horiz_y = box[1] + int(ph * 0.62)
                d.rectangle([ibox[0], horiz_y, ibox[2], ibox[3]], fill=(30, 41, 59, 255))
                d.line([ibox[0], horiz_y, ibox[2], horiz_y], fill=(56, 189, 248, 180), width=max(1, int(1.2 * scale * (S / 256.0))))
                d.line(
                    [box[0] + int(pw * 0.20), horiz_y + int(3 * scale * (S / 256.0)),
                     box[0] + int(pw * 0.48), horiz_y + int(3 * scale * (S / 256.0))],
                    fill=(56, 189, 248, 180),
                    width=max(1, int(1.2 * scale * (S / 256.0))),
                )

            b_width = max(1, int(1.8 * scale * (S / 256.0)))
            d.rounded_rectangle(box, radius=panel_rad, outline=(226, 232, 240, 240), width=b_width)

        blue = (59, 130, 246, 255)
        arrow_tip = (int(0.89 * SS), int(0.12 * SS))
        angle = math.atan2(arrow_tip[1] - c1[1], arrow_tip[0] - c1[0])

        path_w = max(int(1.2 * scale), int(SS * 0.022))
        node_r = max(int(2.0 * scale), int(SS * 0.046))
        arrow_len = int(SS * 0.08)
        arrow_w = int(SS * 0.065)

        outline_w = path_w + max(2, int(2.0 * scale * (S / 256.0)))
        d.line([c1, c2, c3, arrow_tip], fill=(12, 16, 26, 255), width=outline_w, joint="curve")
        d.line([c1, c2, c3, arrow_tip], fill=blue, width=path_w, joint="curve")
        draw_arrow(d, arrow_tip, angle, length=arrow_len, width=arrow_w, fill=blue)

        for c in centers:
            d.ellipse([c[0] - node_r, c[1] - node_r, c[0] + node_r, c[1] + node_r], fill=(12, 16, 26, 255))
            rim_w = max(1, int(1.2 * scale * (S / 256.0)))
            d.ellipse(
                [c[0] - node_r + rim_w, c[1] - node_r + rim_w, c[0] + node_r - rim_w, c[1] + node_r - rim_w],
                fill=blue,
            )
            core_r = max(1, int(node_r * 0.40))
            d.ellipse([c[0] - core_r, c[1] - core_r, c[0] + core_r, c[1] + core_r], fill=(255, 255, 255, 255))

    return img.resize((S, S), Image.Resampling.LANCZOS)


def main():
    print("Rendering Storyboard Editor icons...")
    rendered = {}
    for s in SIZES:
        rendered[s] = render_icon(s)
        print(f"  Rendered {s}x{s} frame (supersampled 4x)")

    # Save .ico file with bitmap_format='bmp' and all sizes
    ico_sizes = [(s, s) for s in SIZES]
    append_frames = [rendered[s] for s in SIZES if s != 256]
    rendered[256].save(
        ICO_PATH,
        format="ICO",
        sizes=ico_sizes,
        append_images=append_frames,
        bitmap_format="bmp",
    )
    print(f"Wrote {ICO_PATH}")

    # Verify and confirm sizes by reopening
    with Image.open(ICO_PATH) as ico:
        reopened_sizes = sorted(ico.info.get("sizes", []))
        entry_dims = [e.dim for e in ico.ico.entry]
        print(f"Reopened {ICO_PATH.name}:")
        print(f"  Primary size: {ico.size}")
        print(f"  Contained sizes ({len(entry_dims)}): {entry_dims}")
        print(f"  info['sizes']: {reopened_sizes}")

    # Build icon_preview.png: 256 render, then 64, 32, 24, 16 on mid-grey canvas
    pad = 24
    gap = 20
    small_total_w = sum(s for s in PREVIEW_SIZES if s != 256) + gap * (len(PREVIEW_SIZES) - 2)
    canvas_w = pad + 256 + gap + small_total_w + pad
    canvas_h = pad + 256 + pad
    mid_grey = (105, 105, 110)

    preview_img = Image.new("RGB", (canvas_w, canvas_h), mid_grey)
    preview_img.paste(rendered[256], (pad, pad), rendered[256])

    curr_x = pad + 256 + gap
    for s in [64, 32, 24, 16]:
        y = pad + (256 - s) // 2
        preview_img.paste(rendered[s], (curr_x, y), rendered[s])
        curr_x += s + gap

    preview_img.save(PREVIEW_PATH, format="PNG")
    print(f"Wrote {PREVIEW_PATH} ({canvas_w}x{canvas_h})")


if __name__ == "__main__":
    main()
