"""
traversing the dataset and exporting to certain format, such  as:

- llava training format;

also, cleaning the txt files and parquet files saved previously and 
not needed anymore
"""

import json
import os
from pathlib import Path
from loguru import logger


def export(dataset_path: str, fmt: str, clean_files: bool = False):
    """
    Export a dataset folder into a specified mllmdata format.

    Currently supports:
      - llava: outputs a JSON list of image/text pairs in llava format.

    Args:
        dataset_path (str): Path to the dataset directory.
        fmt (str): Export format, e.g., 'llava'.
    """
    ds = Path(dataset_path)
    if not ds.is_dir():
        raise ValueError(f"Dataset path '{dataset_path}' is not a directory")

    logger.info(f"start export dataset {dataset_path} to {fmt} format")

    logger.info(f"start export to {fmt} format")

    if fmt == "llava":
        records = []
        # Traverse subdirectories for images and txts
        for sub in sorted(ds.iterdir()):
            if not sub.is_dir():
                continue
            # For each image file in this subfolder
            for img_file in sorted(sub.iterdir()):
                if img_file.suffix.lower() not in [".jpg", ".jpeg", ".png", ".webp"]:
                    continue
                txt_file = img_file.with_suffix(".txt")
                if not txt_file.exists():
                    print(f"Warning: no text for image {img_file}")
                    continue
                # Relative path from dataset root
                rel_img = img_file.relative_to(ds).as_posix()
                rec = {
                    "id": rel_img,
                    "image": rel_img,
                    "conversations": [
                        {
                            "from": "human",
                            "value": "Provide a detailed description of the image using both visual and caption cues. Expand with meaningful insights beyond the caption.",
                        },
                        {
                            "from": "gpt",
                            "value": txt_file.read_text(encoding="utf-8").strip(),
                        },
                    ],
                }
                records.append(rec)

        logger.info(f"export {len(records)} records to {fmt} format")
        # Write output JSON
        out_path = ds / f"export_{fmt}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        print(f"Exported {len(records)} records to {out_path}")

    else:
        raise NotImplementedError(f"Export format '{fmt}' is not supported yet")

    # Cleanup old root-level .txt and .parquet files (e.g., input lists)
    if clean_files:
        logger.info("cleanup old root-level.txt and.parquet files (e.g., input lists)")
        confirm = input(
            "Are you sure you want to delete all .txt files under the data directory? (y/n): "
        )
        if confirm.lower() == "yes" or confirm.lower() == "y":
            for file in ds.rglob("*.txt"):
                if file.is_file():
                    try:
                        file.unlink()
                        # print(f"Removed: {file}")
                    except Exception as e:
                        logger.warning(f"Warning: failed to remove {file}: {e}")
        else:
            print("Deletion canceled.")
    logger.info(f"export dataset {dataset_path} to {fmt} format finished!")


def clean(dataset_path: str):

    ds = Path(dataset_path)
    if not ds.is_dir():
        raise ValueError(f"Dataset path '{dataset_path}' is not a directory")
    logger.info(
        "cleanup old root-level .txt .json and.parquet files (e.g., input lists)"
    )

    json_files = ds.glob("*/*.json")
    json_files = [f for f in json_files if f.name.split(".")[0].isdigit()]
    txt_files = list(ds.rglob("*.txt"))

    logger.info(f"found: {len(json_files)} json files, {len(txt_files)} txt files")
    logger.info("start remove these files")

    confirm = input(
        "Are you sure you want to delete all .txt .json files under the data directory? (y/n): "
    )
    if confirm.lower() == "yes" or confirm.lower() == "y":

        for file in txt_files + json_files:
            if file.is_file():
                try:
                    file.unlink()
                    # print(f"Removed: {file}")
                except Exception as e:
                    logger.warning(f"Warning: failed to remove {file}: {e}")
    else:
        print("Deletion canceled.")
