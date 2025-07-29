import argparse
import pandas as pd
import torch
from medscan.pipeline import Pipeline
from medscan.config import PreprocessConfig, TrainConfig
from pathlib import Path

def main(args):
    img_dir = Path(args.img_dir)
    exts = {".png", ".jpg", ".jpeg", ".dcm"}
    files = [p for p in img_dir.rglob("*") if p.suffix.lower() in exts]
    if not files:
        raise ValueError(f"No images found in {img_dir}")

    df = pd.DataFrame({"img_path": [str(p) for p in files]})
    device = "cuda" if torch.cuda.is_available() and not args.force_cpu else "cpu"

    dummy_pre = PreprocessConfig()
    dummy_train = TrainConfig(device=device)
    pipe = Pipeline(dummy_pre, dummy_train, targets=[])
    pipe.load(args.model_path)

    # override labels if provided
    if args.labels and args.labels.lower() != "all":
        pipe.targets = [l.strip() for l in args.labels.split(',') if l.strip()]

    # ensure required columns exist
    for t in pipe.targets:
        if t not in df.columns:
            df[t] = pd.NA

    result = pipe.predict(df, return_confidence=args.confidence)
    if isinstance(result, dict):
        result_df = result.get("best")
    else:
        result_df = result

    result_df.to_csv(args.output_csv, index=False)
    print(f"Saved predictions to {args.output_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run inference using a saved MedScan model")
    parser.add_argument("--img_dir", required=True, help="Directory containing DICOM or PNG images")
    parser.add_argument("--model_path", default="", help="Path to the saved model directory or checkpoint")
    parser.add_argument("--labels", default="all", help="Comma-separated labels to predict or 'all'")
    parser.add_argument("--output_csv", default="predictions.csv", help="Where to store predictions")
    parser.add_argument("--confidence", action="store_true", help="Include confidence scores")
    parser.add_argument("--force_cpu", action="store_true", help="Force CPU even if GPU available")
    main(parser.parse_args())