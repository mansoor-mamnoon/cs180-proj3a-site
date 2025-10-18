#!/usr/bin/env python3
import os, sys, shutil, argparse, glob
from pathlib import Path

PAIR_TAGS = [
    # Left–Center pairs you used for mosaics
    ("1491_1492", "IMG_1491.jpg", "IMG_1492.jpg"),
    ("1495_1496", "IMG_1495.jpg", "IMG_1496.jpg"),
    ("1497_1498", "IMG_1497.jpg", "IMG_1498.jpg"),
    ("1511_1512", "IMG_1511.jpg", "IMG_1512.jpg"),
    ("1513_1514", "IMG_1513.jpg", "IMG_1514.jpg"),
]

# Rectification batch tags from your A.3 script
RECT_BATCH = [
    ("poster",     "data/converted/rect_poster/poster_right.jpg"),
    ("blackboard", "data/converted/rect_blackboard/blackboard_left.jpg"),
    ("macbook",    "data/converted/rect_macbook/macbook_right.jpg"),
    ("box",        "data/converted/rect_box/box_bottom.jpg"),
]

def safe_copy(src, dst):
    if not os.path.exists(src):
        print(f"[skip] {src} (missing)")
        return False
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print(f"[copy] {src} -> {dst}")
    return True

def find_first(root, patterns):
    for pat in patterns:
        hits = sorted(Path(root).glob(pat))
        if hits:
            return str(hits[0])
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="Path to cs180-proj3a repo (submission)")
    ap.add_argument("--dst", required=True, help="Path to cs180-proj3a-site repo (website)")
    args = ap.parse_args()

    SRC = os.path.abspath(args.src)
    DST = os.path.abspath(args.dst)

    subm = os.path.join(SRC, "submission")
    data = os.path.join(subm, "data")

    # --- Site assets root ---
    assets = os.path.join(DST, "assets")
    os.makedirs(assets, exist_ok=True)

    # ============ A.1 originals (the five pairs you used) ============
    a1_dir = os.path.join(assets, "a1")
    for tag, left_name, right_name in PAIR_TAGS:
        prefer = os.path.join(data, "converted", f"mosaic_{tag}")
        left_src  = os.path.join(prefer, left_name)
        right_src = os.path.join(prefer, right_name)
        # fallbacks (if your images live elsewhere)
        if not os.path.exists(left_src) or not os.path.exists(right_src):
            # recursive search
            for root, _d, fns in os.walk(os.path.join(subm, "data")):
                for fn in fns:
                    if fn == left_name:  left_src  = os.path.join(root, fn)
                    if fn == right_name: right_src = os.path.join(root, fn)
        safe_copy(left_src,  os.path.join(a1_dir, f"{tag}_left.jpg"))
        safe_copy(right_src, os.path.join(a1_dir, f"{tag}_center.jpg"))

    # ============ A.2 correspondences ============
    # We’ll show the matches visualization you save in A.2 (if you made one),
    # the matches figure you make in A.2/A.2-helpers, plus H_matrix.txt.
    for tag, _l, _r in PAIR_TAGS:
        a2_src_dir = os.path.join(data, "out", "a2", tag)
        a2_dst_dir = os.path.join(assets, "a2", tag)
        os.makedirs(a2_dst_dir, exist_ok=True)
        safe_copy(os.path.join(a2_src_dir, "matches.png"), os.path.join(a2_dst_dir, "matches.png"))
        safe_copy(os.path.join(a2_src_dir, "points.json"), os.path.join(a2_dst_dir, "points.json"))
        safe_copy(os.path.join(a2_src_dir, "H_matrix.txt"), os.path.join(a2_dst_dir, "H_matrix.txt"))
        # Optional linear system preview if present
        ab = os.path.join(a2_src_dir, "Ab_preview.txt")
        if os.path.exists(ab):
            safe_copy(ab, os.path.join(a2_dst_dir, "Ab_preview.txt"))

    # ============ A.3 rectifications ============
    a3_root = os.path.join(data, "out", "a3")
    for tag, src_img in RECT_BATCH:
        out_dir = os.path.join(a3_root, tag)
        dst_dir = os.path.join(assets, "a3", tag)
        os.makedirs(dst_dir, exist_ok=True)
        # original
        safe_copy(os.path.join(subm, src_img), os.path.join(dst_dir, f"{tag}_original.jpg"))
        # rectified outputs & comparison
        safe_copy(os.path.join(out_dir, f"{tag}_rect_nn.jpg"),           os.path.join(dst_dir, f"{tag}_rect_nn.jpg"))
        safe_copy(os.path.join(out_dir, f"{tag}_rect_bil.jpg"),          os.path.join(dst_dir, f"{tag}_rect_bil.jpg"))
        safe_copy(os.path.join(out_dir, f"{tag}_rectified_comparison.png"), os.path.join(dst_dir, f"{tag}_rectified_comparison.png"))
        # homography + meta
        safe_copy(os.path.join(out_dir, f"{tag}_H.txt"),                 os.path.join(dst_dir, f"{tag}_H.txt"))
        safe_copy(os.path.join(out_dir, f"{tag}_meta.json"),             os.path.join(dst_dir, f"{tag}_meta.json"))

    # timings CSV (summary table)
    safe_copy(os.path.join(a3_root, "a3_timings.csv"), os.path.join(assets, "a3", "a3_timings.csv"))

    # ============ A.4 mosaics (manual) ============
    a4_root = os.path.join(data, "out", "a4")
    for tag, _l, _r in PAIR_TAGS:
        src_dir = os.path.join(a4_root, tag)
        dst_dir = os.path.join(assets, "a4", tag)
        os.makedirs(dst_dir, exist_ok=True)
        safe_copy(os.path.join(src_dir, "mosaic.jpg"),     os.path.join(dst_dir, "mosaic.jpg"))
        safe_copy(os.path.join(src_dir, "mosaic_vis.png"), os.path.join(dst_dir, "mosaic_vis.png"))
        # optional debug/meta if present
        for extra in ["used_H.txt", "meta.json", "debug_canvas_bounds.json"]:
            p = os.path.join(src_dir, extra)
            if os.path.exists(p):
                safe_copy(p, os.path.join(dst_dir, extra))

    # ============ B.1 Harris + ANMS ============
    b1_root = os.path.join(data, "out", "b1")
    for tag, role in [
        ("1491_1492_left", "1491_1492_left"),
        ("1491_1492_center", "1491_1492_center"),
        ("1495_1496_left", "1495_1496_left"),
        ("1495_1496_center", "1495_1496_center"),
        ("1497_1498_left", "1497_1498_left"),
        ("1497_1498_center", "1497_1498_center"),
        ("1511_1512_left", "1511_1512_left"),
        ("1511_1512_center","1511_1512_center"),
        ("1513_1514_left", "1513_1514_left"),
        ("1513_1514_center","1513_1514_center"),
    ]:
        src_dir = os.path.join(b1_root, tag)
        dst_dir = os.path.join(assets, "b1", tag)
        os.makedirs(dst_dir, exist_ok=True)
        safe_copy(os.path.join(src_dir, "harris_overlay.png"), os.path.join(dst_dir, "harris_overlay.png"))
        safe_copy(os.path.join(src_dir, "anms_overlay.png"),   os.path.join(dst_dir, "anms_overlay.png"))

    # ============ B.2 descriptors ============
    b2_root = os.path.join(data, "out", "b2")
    # We’ll copy every tag folder that exists in b2/
    if os.path.isdir(b2_root):
        for tag_dir in sorted(os.listdir(b2_root)):
            src_dir = os.path.join(b2_root, tag_dir)
            if not os.path.isdir(src_dir): continue
            dst_dir = os.path.join(assets, "b2", tag_dir)
            os.makedirs(dst_dir, exist_ok=True)
            # grid + previews if present
            safe_copy(os.path.join(src_dir, "features_grid.png"),  os.path.join(dst_dir, "features_grid.png"))
            for extra in ["keypoints_xy.npy", "descs.npy", "descs_preview.txt"]:
                p = os.path.join(src_dir, extra)
                if os.path.exists(p):
                    safe_copy(p, os.path.join(dst_dir, extra))

    # ============ B.3 matches ============
    b3_root = os.path.join(data, "out", "b3")
    for tag, _l, _r in PAIR_TAGS:
        src_dir = os.path.join(b3_root, tag)
        dst_dir = os.path.join(assets, "b3", tag)
        os.makedirs(dst_dir, exist_ok=True)
        safe_copy(os.path.join(src_dir, "matches.png"), os.path.join(dst_dir, "matches.png"))

    # ============ B.4 RANSAC + auto-stitch ============
    b4_root = os.path.join(data, "out", "b4")
    for tag, _l, _r in PAIR_TAGS:
        src_dir = os.path.join(b4_root, tag)
        dst_dir = os.path.join(assets, "b4", tag)
        os.makedirs(dst_dir, exist_ok=True)
        for f in ["mosaic.jpg", "matches_inliers.png", "H.txt", "inliers_mask.npy"]:
            p = os.path.join(src_dir, f)
            if os.path.exists(p):
                safe_copy(p, os.path.join(dst_dir, f))

    print("\n[done] Assets copied into", assets)

if __name__ == "__main__":
    main()
