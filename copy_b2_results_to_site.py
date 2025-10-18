#!/usr/bin/env python3
"""
Copy all B.2 results (features_grid.png, descs.npy, keypoints_xy.npy, etc.)
from your project repo into the website assets folder for inclusion in your PDF.

Run this from the website repo:
    python3 copy_b2_results_to_site.py --src ../cs180-proj3a --dst .

Author: Mansoor Mamnoon
"""

import os
import shutil
import argparse

PAIR_TAGS = ["1491_1492", "1495_1496", "1497_1498", "1511_1512", "1513_1514"]

def copy_b2_results(src_root, dst_root):
    """
    Copy the B.2 result directories for all pairs into assets/b2/.
    """
    src_b2 = os.path.join(src_root, "submission", "data", "out", "b2")
    dst_b2 = os.path.join(dst_root, "assets", "b2")
    os.makedirs(dst_b2, exist_ok=True)

    for tag in PAIR_TAGS:
        for suffix in ["_left", "_center"]:
            src_dir = os.path.join(src_b2, f"{tag}{suffix}")
            dst_dir = os.path.join(dst_b2, f"{tag}{suffix}")
            if not os.path.exists(src_dir):
                print(f"[skip] {src_dir} not found.")
                continue
            os.makedirs(dst_dir, exist_ok=True)

            # copy relevant files only
            for fn in os.listdir(src_dir):
                if fn.endswith((".png", ".npy", ".txt")):
                    src_path = os.path.join(src_dir, fn)
                    dst_path = os.path.join(dst_dir, fn)
                    shutil.copy2(src_path, dst_path)
            print(f"[ok] Copied {tag}{suffix} → {dst_dir}")

    print("\n✅ All B.2 results copied to assets/b2/")

def main():
    ap = argparse.ArgumentParser(description="Copy B.2 results into website assets folder.")
    ap.add_argument("--src", type=str, required=True, help="Path to your cs180-proj3a repo.")
    ap.add_argument("--dst", type=str, default=".", help="Path to your website repo (default: current directory).")
    args = ap.parse_args()

    src_root = os.path.abspath(args.src)
    dst_root = os.path.abspath(args.dst)
    copy_b2_results(src_root, dst_root)

if __name__ == "__main__":
    main()
