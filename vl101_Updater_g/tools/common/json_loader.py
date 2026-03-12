import json
from pathlib import Path
from typing import Dict, Any

THIS_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = THIS_DIR / "data.json"

def load_json() -> dict:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"data.json が存在しません: {DATA_PATH}")

    with DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def load_vl800_settingJson() -> dict:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"setting.json が存在しません: {DATA_PATH}")

    with DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


# 任意の一覧ページ用 setting.json を読み込む
def load_setting_json_file(path: str | Path) -> Dict[str, Any]:
    p = Path(path)

    if not p.exists():
        raise FileNotFoundError(f"jsonファイルが存在しません: {p}")

    # if p.is_dir():
    #     raise IsADirectoryError(f"ディレクトリが指定されました: {p}")

    with p.open(encoding="utf-8") as f:
        return json.load(f)