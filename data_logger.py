# data_logger.py
# Very small, focused logger: append one JSON entry per line (NDJSON).
# Stores only the fields necessary: timestamp, user_id, test_id, test_type, array.
# This keeps the implementation minimal and avoids reading/writing a full JSON array.

import json
import os
from datetime import datetime
from typing import Any, Dict, List

LOG_FILE = os.environ.get("LOG_FILE", "test_data_logs.ndjson")


def _utc_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def log_test_data(
    user_id: str,
    test_id: str,
    test_type: str,
    input_data: Dict[str, Any],
    output_array: List[Any],
    extra_data: Dict[str, Any] | None = None
) -> None:
    """
    Append a minimal log entry to LOG_FILE as one JSON object per line.

    Only the API-generated array (output_array) is required to be stored;
    we also save a small header (timestamp, ids, type) so entries are useful later.
    This function will create the file (and parent dir) if needed and will
    never raise — errors are printed and swallowed so logging won't break the API.
    """
    entry = {
        "timestamp": _utc_iso(),
        "user_id": user_id,
        "test_id": test_id,
        "test_type": test_type,
        "array": output_array
    }
    if extra_data is not None:
        entry["extra_data"] = extra_data

    try:
        # ensure directory exists
        dirpath = os.path.dirname(LOG_FILE)
        if dirpath:
            os.makedirs(dirpath, exist_ok=True)

        # append one JSON object per line (NDJSON)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False))
            f.write("\n")
    except Exception as e:
        # keep logging non-fatal for the API; print the error for debugging
        print(f"⚠️ data_logger: failed to write log entry: {e}")