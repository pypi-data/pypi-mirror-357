"""Img2dataset"""

import argparse
from typing import List, Optional, Union
import logging
from .logger import LoggerProcess
from .resizer import Resizer
from .blurrer import BoundingBoxBlurrer
from .writer import (
    WebDatasetSampleWriter,
    FilesSampleWriter,
    ParquetSampleWriter,
    TFRecordSampleWriter,
    DummySampleWriter,
)
from .reader import Reader
from .downloader import Downloader
from .distributor import (
    multiprocessing_distributor,
    pyspark_distributor,
    ray_distributor,
)
import fsspec
import sys
import signal
import os
from loguru import logger
from .export import clean, export

logging.getLogger("exifread").setLevel(level=logging.CRITICAL)


def arguments_validator(params):
    """Validate the arguments"""
    if params["compute_hash"] not in [None, "md5", "sha256", "sha512"]:
        hash_type = params["compute_hash"]
        raise ValueError(f"Unsupported hash to compute: {hash_type}")

    if params["verify_hash"] is not None:
        _, verify_hash_type = params["verify_hash"]
        if verify_hash_type != params["compute_hash"]:
            raise ValueError(
                "verify_hash and compute_hash must be the same "
                f"but got {verify_hash_type} and {params['compute_hash']}"
            )

    if params["save_additional_columns"] is not None:
        save_additional_columns_set = set(params["save_additional_columns"])

        forbidden_columns = set(
            [
                "key",
                "caption",
                "url",
                "width",
                "height",
                "original_width",
                "original_height",
                "status",
                "error_message",
                "exif",
                "md5",
                "sha256",
                "sha512",
            ]
        )
        intersection = save_additional_columns_set.intersection(forbidden_columns)
        if intersection:
            raise ValueError(
                f"You cannot use in save_additional_columns the following columns: {intersection}."
                + "img2dataset reserves these columns for its own use. Please remove them from save_additional_columns."
            )


def download(
    url_list: list[str] = [],
    image_size: int = 256,
    output_folder: str = "images",
    processes_count: int = 1,
    resize_mode: str = "border",
    resize_only_if_bigger: bool = False,
    upscale_interpolation: str = "lanczos",
    downscale_interpolation: str = "area",
    encode_quality: int = 95,
    encode_format: str = "jpg",
    skip_reencode: bool = False,
    output_format: str = "files",
    input_format: str = "txt",
    url_col: str = "url",
    caption_col: Optional[str] = None,
    bbox_col: Optional[str] = None,
    thread_count: int = 256,
    number_sample_per_shard: int = 10000,
    extract_exif: bool = True,
    save_additional_columns: Optional[List[str]] = None,
    timeout: int = 10,
    enable_wandb: bool = False,
    wandb_project: str = "img2dataset",
    oom_shard_count: int = 5,
    compute_hash: Optional[str] = "sha256",
    verify_hash: Optional[List[str]] = None,
    distributor: str = "multiprocessing",
    subjob_size: int = 1000,
    retries: int = 0,
    disable_all_reencoding: bool = False,
    min_image_size: int = 0,
    max_image_area: float = float("inf"),
    max_aspect_ratio: float = float("inf"),
    incremental_mode: str = "incremental",
    max_shard_retry: int = 1,
    user_agent_token: Optional[str] = None,
    disallowed_header_directives: Optional[List[str]] = None,
):
    """Download is the main entry point of img2dataset, it uses multiple processes and download multiple files"""
    if disallowed_header_directives is None:
        disallowed_header_directives = ["noai", "noimageai", "noindex", "noimageindex"]
    if len(disallowed_header_directives) == 0:
        disallowed_header_directives = None

    config_parameters = dict(locals())
    arguments_validator(config_parameters)

    def make_path_absolute(path):
        fs, p = fsspec.core.url_to_fs(path)
        if fs.protocol == "file":
            return os.path.abspath(p)
        return path

    logger.info(f"request url files: {url_list}")
    output_folder = make_path_absolute(output_folder)
    if isinstance(url_list, list):
        url_list = url_list[0]
    url_list = make_path_absolute(url_list)

    logger_process = LoggerProcess(
        output_folder, enable_wandb, wandb_project, config_parameters
    )

    tmp_path = output_folder + "/_tmp"
    fs, tmp_dir = fsspec.core.url_to_fs(tmp_path)
    if not fs.exists(tmp_dir):
        fs.mkdir(tmp_dir)

    def signal_handler(signal_arg, frame):  # pylint: disable=unused-argument
        try:
            fs.rm(tmp_dir, recursive=True)
        except Exception as _:  # pylint: disable=broad-except
            pass
        logger_process.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    save_caption = caption_col is not None

    fs, output_path = fsspec.core.url_to_fs(output_folder)
    start_shard_id = 0

    if not fs.exists(output_path):
        fs.mkdir(output_path)
        done_shards = set()
    else:
        if incremental_mode == "incremental":
            done_shards = set(
                int(x.split("/")[-1].split("_")[0])
                for x in fs.glob(output_path + "/*.json")
                if x.split("/")[-1].split("_")[0].isdigit()
            )
        elif incremental_mode == "overwrite":
            fs.rm(output_path, recursive=True)
            fs.mkdir(output_path)
            done_shards = set()
        elif incremental_mode == "extend":
            existing_shards = [
                int(x.split("/")[-1].split("_")[0])
                for x in fs.glob(output_path + "/*.json")
            ]
            start_shard_id = max(existing_shards, default=-1) + 1
            done_shards = set()
        else:
            raise ValueError(f"Unknown incremental mode {incremental_mode}")
    logger.info(f"done_shards: {done_shards}")
    logger_process.done_shards = done_shards
    logger_process.start()

    if bbox_col is not None:
        if save_additional_columns is None:
            save_additional_columns = [bbox_col]
        else:
            save_additional_columns.append(bbox_col)

    if verify_hash is not None:
        verify_hash_col, verify_hash_type = verify_hash
    else:
        verify_hash_col = None
        verify_hash_type = None

    reader = Reader(
        url_list,
        input_format,
        url_col,
        caption_col,
        verify_hash_col,
        verify_hash_type,
        save_additional_columns,
        number_sample_per_shard,
        done_shards,
        tmp_path,
        start_shard_id,
    )

    if output_format == "webdataset":
        sample_writer_class = WebDatasetSampleWriter
    elif output_format == "parquet":
        sample_writer_class = ParquetSampleWriter  # type: ignore
    elif output_format == "files":
        sample_writer_class = FilesSampleWriter  # type: ignore
    elif output_format == "tfrecord":
        sample_writer_class = TFRecordSampleWriter  # type: ignore
    elif output_format == "dummy":
        sample_writer_class = DummySampleWriter  # type: ignore
    else:
        raise ValueError(f"Invalid output format {output_format}")

    if bbox_col is not None:
        blurrer = BoundingBoxBlurrer()
    else:
        blurrer = None

    resizer = Resizer(
        image_size=image_size,
        resize_mode=resize_mode,
        resize_only_if_bigger=resize_only_if_bigger,
        upscale_interpolation=upscale_interpolation,
        downscale_interpolation=downscale_interpolation,
        encode_quality=encode_quality,
        encode_format=encode_format,
        skip_reencode=skip_reencode,
        disable_all_reencoding=disable_all_reencoding,
        min_image_size=min_image_size,
        max_image_area=max_image_area,
        max_aspect_ratio=max_aspect_ratio,
        blurrer=blurrer,
    )

    downloader = Downloader(
        sample_writer_class=sample_writer_class,
        resizer=resizer,
        thread_count=thread_count,
        save_caption=save_caption,
        extract_exif=extract_exif,
        output_folder=output_folder,
        column_list=reader.column_list,
        timeout=timeout,
        number_sample_per_shard=number_sample_per_shard,
        oom_shard_count=oom_shard_count,
        compute_hash=compute_hash,
        verify_hash_type=verify_hash_type,
        encode_format=encode_format,
        retries=retries,
        user_agent_token=user_agent_token,
        disallowed_header_directives=disallowed_header_directives,
        blurring_bbox_col=bbox_col,
    )

    print("Starting the downloading of this file")
    if distributor == "multiprocessing":
        distributor_fn = multiprocessing_distributor
    elif distributor == "pyspark":
        distributor_fn = pyspark_distributor
    elif distributor == "ray":
        distributor_fn = ray_distributor
    else:
        raise ValueError(f"Distributor {distributor} not supported")

    distributor_fn(
        processes_count,
        downloader,
        reader,
        subjob_size,
        max_shard_retry,
    )
    logger_process.join()

    if not hasattr(fs, "s3"):
        fs.rm(tmp_dir, recursive=True)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download images with img2dataset-style parameters, or export via mllmdata"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    download_parser = subparsers.add_parser(
        "download",
        help="Download images using img2dataset-style parameters",
        description="Download images using img2dataset-style parameters",
    )
    # copy & paste all your existing arguments onto download_parser:
    download_parser.add_argument(
        "--url_list",
        nargs="+",
        required=True,
        help="List of URLs or file paths to process",
    )
    download_parser.add_argument(
        "--image_size",
        type=int,
        default=256,
        help="Resize image to this size (px)",
    )
    download_parser.add_argument(
        "--output_folder",
        type=str,
        default="images",
        help="Output directory",
    )
    download_parser.add_argument(
        "--processes_count",
        type=int,
        default=1,
        help="Number of parallel processes",
    )
    download_parser.add_argument(
        "--resize_mode",
        type=str,
        default="border",
        choices=["border", "center", "no"],
        help="Resize strategy",
    )
    download_parser.add_argument(
        "--resize_only_if_bigger",
        action="store_true",
        help="Only resize if image is larger than target",
    )
    download_parser.add_argument(
        "--upscale_interpolation",
        type=str,
        default="lanczos",
        help="Interpolation when upscaling",
    )
    download_parser.add_argument(
        "--downscale_interpolation",
        type=str,
        default="area",
        help="Interpolation when downscaling",
    )
    download_parser.add_argument(
        "--encode_quality",
        type=int,
        default=95,
        help="JPEG quality for encoding",
    )
    download_parser.add_argument(
        "--encode_format",
        type=str,
        default="jpg",
        choices=["jpg", "png", "webp"],
        help="Image format for re-encoding",
    )
    download_parser.add_argument(
        "--skip_reencode",
        action="store_true",
        help="Skip re-encoding if not needed",
    )
    download_parser.add_argument(
        "--output_format",
        type=str,
        default="files",
        choices=["files", "lmdb", "webdataset"],
        help="How to store output",
    )
    download_parser.add_argument(
        "--input_format",
        type=str,
        default="txt",
        help="Format of input URL list (txt|parquet|json)",
    )
    download_parser.add_argument(
        "--url_col",
        type=str,
        default="url",
        help="Column name for URLs (in parquet/json)",
    )
    download_parser.add_argument(
        "--caption_col",
        type=str,
        default=None,
        help="Column name for captions",
    )
    download_parser.add_argument(
        "--bbox_col",
        type=str,
        default=None,
        help="Column name for bounding boxes",
    )
    download_parser.add_argument(
        "--thread_count",
        type=int,
        default=256,
        help="Threads per process",
    )
    download_parser.add_argument(
        "--number_sample_per_shard",
        type=int,
        default=10000,
        help="Samples per shard",
    )
    download_parser.add_argument(
        "--extract_exif",
        action="store_true",
        help="Extract EXIF metadata",
    )
    download_parser.add_argument(
        "--save_additional_columns",
        nargs="+",
        default=None,
        help="List of extra dataframe columns to save",
    )
    download_parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Network timeout (s)",
    )
    download_parser.add_argument(
        "--enable_wandb",
        action="store_true",
        help="Log runs to Weights & Biases",
    )
    download_parser.add_argument(
        "--wandb_project",
        type=str,
        default="img2dataset",
        help="W&B project name",
    )
    download_parser.add_argument(
        "--oom_shard_count",
        type=int,
        default=5,
        help="Shards to split on OOM",
    )
    download_parser.add_argument(
        "--compute_hash",
        type=str,
        default="sha256",
        help="Hash algorithm (or none)",
    )
    download_parser.add_argument(
        "--verify_hash",
        nargs="+",
        default=None,
        help="List of hash algorithms to verify against",
    )
    download_parser.add_argument(
        "--distributor",
        type=str,
        default="multiprocessing",
        help="Job distribution backend",
    )
    download_parser.add_argument(
        "--subjob_size",
        type=int,
        default=1000,
        help="Work chunk size",
    )
    download_parser.add_argument(
        "--retries",
        type=int,
        default=0,
        help="Number of download retries",
    )
    download_parser.add_argument(
        "--disable_all_reencoding",
        action="store_true",
        help="Turn off all re-encoding",
    )
    download_parser.add_argument(
        "--min_image_size",
        type=int,
        default=0,
        help="Minimum image dimension",
    )
    download_parser.add_argument(
        "--max_image_area",
        type=float,
        default=float("inf"),
        help="Max allowed image area",
    )
    download_parser.add_argument(
        "--max_aspect_ratio",
        type=float,
        default=float("inf"),
        help="Max width/height ratio",
    )
    download_parser.add_argument(
        "--incremental_mode",
        type=str,
        default="incremental",
        help="Mode for incremental runs",
    )
    download_parser.add_argument(
        "--max_shard_retry",
        type=int,
        default=1,
        help="Retries per shard on failure",
    )
    download_parser.add_argument(
        "--user_agent_token",
        type=str,
        default=None,
        help="Custom User-Agent header token",
    )
    download_parser.add_argument(
        "--disallowed_header_directives",
        nargs="+",
        default=None,
        help="HTTP header directives not to forward",
    )

    # ── “export” subcommand ───────────────────────────────────────────────────────
    export_parser = subparsers.add_parser(
        "export",
        help="Export dataset in mllmdata format",
        description="Export your_dataset/ into a supported 'mllmdata' format",
    )
    export_parser.add_argument(
        "dataset_path",
        type=str,
        help="Path to the dataset directory (e.g. your_dataset/)",
    )
    export_parser.add_argument(
        "--format",
        type=str,
        required=True,
        choices=["llava", "alpaca", "vicuna"],
        help="Which mllmdata export format to use",
    )
    export_parser.add_argument(
        "--clean",
        action="store_true",
    )

    clean_parser = subparsers.add_parser(
        "clean",
        help="Clean dataset in mllmdata format",
        description="Clean your_dataset/ into a supported 'mllmdata' format",
    )
    clean_parser.add_argument(
        "dataset_path",
        type=str,
        help="Path to the dataset directory (e.g. your_dataset/)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.command == "download":
        # all your existing flags live in args.__dict__
        delattr(args, "command")
        download(**vars(args))
    elif args.command == "export":
        # you'll implement export(dataset_path, fmt, **maybe_other_args)
        export(args.dataset_path, fmt=args.format, clean_files=args.clean)
    elif args.command == "clean":
        clean(args.dataset_path)
    else:
        # argparse’s `required=True` on subparsers should prevent this
        raise RuntimeError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
