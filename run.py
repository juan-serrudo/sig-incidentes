"""Start the local example; create missing data and artifacts first."""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description="Run the support-request classification demo.")
    parser.add_argument("--rebuild", action="store_true", help="Regenerate data and retrain before starting.")
    parser.add_argument("--port", type=int, default=8991, help="Local HTTP port (default: 8991).")
    args = parser.parse_args()
    data_missing = not (ROOT / "data/tickets.csv").exists()
    if args.rebuild or data_missing:
        subprocess.run([sys.executable, "-m", "app.data"], cwd=ROOT, check=True)
    if args.rebuild or data_missing or not all((ROOT / "artifacts" / name).exists() for name in ["model.joblib", "metrics.json"]):
        subprocess.run([sys.executable, "-m", "app.train"], cwd=ROOT, check=True)
    print(f"Open http://127.0.0.1:{args.port}. Press Ctrl+C to stop.", flush=True)
    subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(args.port)], cwd=ROOT, check=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDemo stopped.")
    except subprocess.CalledProcessError as error:
        raise SystemExit(f"A step failed with exit code {error.returncode}. See the message above and README.md.") from None
