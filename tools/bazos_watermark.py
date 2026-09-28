#!/usr/bin/env python3
"""Remove the "@( Bazos.sk" watermark that Bazoš stamps into listing photos.

    python3 tools/bazos_watermark.py OUT_DIR photo.jpg [photo.jpg ...]

The watermark always sits at the same pixel offset from the bottom-right
corner. bazos_watermark_template.png holds its shape: the median high-pass
response over 35 watermarked photos, stored as 128 + signed value. When a
photo's corner matches the template, the glyph pixels are refilled with
OpenCV's frequency-selective inpainting and the photo is saved with the
source JPEG's quantisation tables, so size and quality stay close to the
original. Photos without the watermark are copied unchanged.

Needs: pip install opencv-contrib-python-headless pillow numpy
"""
import os
import shutil
import sys

import cv2
import numpy as np
from PIL import Image, JpegImagePlugin

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = cv2.imread(os.path.join(HERE, "bazos_watermark_template.png"),
                      cv2.IMREAD_GRAYSCALE).astype(np.float32) - 128
BH, BW = TEMPLATE.shape
PAD = 60  # surrounding context handed to the inpainter


def _glyph_mask():
    strokes = (np.abs(TEMPLATE) > 6).astype(np.uint8)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(strokes, 8)
    keep = np.zeros_like(strokes)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] >= 25:
            keep[labels == i] = 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    return cv2.dilate(keep, kernel).astype(bool)


MASK = _glyph_mask()
TEMPLATE_Z = (TEMPLATE - TEMPLATE.mean()) / TEMPLATE.std()


def has_watermark(bgr):
    h, w = bgr.shape[:2]
    corner = cv2.cvtColor(bgr[h - BH:, w - BW:], cv2.COLOR_BGR2GRAY)
    detail = corner.astype(np.float32) - cv2.medianBlur(corner, 21).astype(np.float32)
    detail = (detail - detail.mean()) / (detail.std() + 1e-6)
    return float((detail * TEMPLATE_Z).mean()) > 0.1


def clean(src, dst):
    bgr = cv2.imread(src)
    if bgr is None:
        raise SystemExit(f"cannot read {src}")
    h, w = bgr.shape[:2]
    if h < BH + PAD or w < BW + PAD or not has_watermark(bgr):
        shutil.copyfile(src, dst)
        return False

    y0, x0 = h - BH - PAD, w - BW - PAD
    region = bgr[y0:, x0:].copy()
    known = np.full(region.shape[:2], 255, np.uint8)  # 0 marks pixels to fill
    known[PAD:, PAD:][MASK] = 0
    filled = np.zeros_like(region)
    cv2.xphoto.inpaint(region, known, filled, cv2.xphoto.INPAINT_FSR_BEST)

    original = Image.open(src)
    patched = original.convert("RGB")
    patched.paste(Image.fromarray(cv2.cvtColor(filled, cv2.COLOR_BGR2RGB)), (x0, y0))
    if original.format == "JPEG":
        sampling = JpegImagePlugin.get_sampling(original)
        patched.save(dst, "JPEG", qtables=original.quantization, optimize=True,
                     subsampling=sampling if sampling >= 0 else 2)
    else:
        patched.save(dst)
    return True


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)
    for src in sys.argv[2:]:
        dst = os.path.join(out_dir, os.path.basename(src))
        print(("cleaned " if clean(src, dst) else "copied  ") + dst)


if __name__ == "__main__":
    main()
