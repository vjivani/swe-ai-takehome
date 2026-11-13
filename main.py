"""Command-line entry point for the OpenAI time-and-motion analyzer."""

import json
from datetime import datetime
from pathlib import Path

from analyzer import analyze_study


def _rotate_output_if_exists(output_path: Path) -> None:
    if not output_path.exists():
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = output_path.with_name(f"output_old_{timestamp}.json")
    counter = 1
    while backup_path.exists():
        backup_path = output_path.with_name(f"output_old_{timestamp}_{counter}.json")
        counter += 1
    output_path.rename(backup_path)


def main() -> None:
    study_path = Path(__file__).resolve().parent / "data" / "time_motion_study.md"
    output_path = Path(__file__).resolve().parent / "output.json"
    _rotate_output_if_exists(output_path)
    result = analyze_study(study_path)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
