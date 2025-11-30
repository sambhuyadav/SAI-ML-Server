from __future__ import annotations

import argparse
from pathlib import Path

from src.models.loader import load_movenet
from src.pipelines.rater import VideoRater


def main() -> None:
    parser = argparse.ArgumentParser(description="Quickly score a movement video.")
    parser.add_argument("video", type=Path, help="Path to an MP4 file.")
    parser.add_argument("--test-name", default="benchmark", help="Name of the test performed.")
    parser.add_argument(
        "--model",
        default=Path("models/movenet.tflite"),
        type=Path,
        help="Path to MoveNet TFLite model.",
    )
    args = parser.parse_args()

    model = load_movenet(args.model)
    rater = VideoRater(model=model, default_test=args.test_name)
    rating = rater.rate(args.video, test_name=args.test_name)
    print(rating.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
