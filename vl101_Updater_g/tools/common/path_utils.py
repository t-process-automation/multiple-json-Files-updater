from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from functools import lru_cache
from tools.common.json_loader import load_json


@lru_cache(maxsize=1)
def get_json() -> dict:
    return load_json()

def _require(d: dict, key: str):
    if key not in d:
        raise KeyError(f"data.json に '{key}' がありません")
    return d[key]

# パス構造を改変不可にする
@dataclass(frozen=True)
class ResolvedPaths:
    vl800_dir: Path
    vl101_path: Path

# maxsize=1:最新の1つだけ保存する
# 関数の結果をメモする仕組み(キャッシュ) data.json を何度も読み込まない。1度で十分
@lru_cache(maxsize=1)
def get_paths() -> ResolvedPaths: # 戻り値の型は ResolvedPaths 型ヒント
    json = get_json()

    vl800_dir = Path(_require(json, "vl800_path")).resolve()
    vl101_path = Path(_require(json, "vl101_path")).resolve()

    return ResolvedPaths(vl800_dir=vl800_dir, vl101_path=vl101_path)

def get_region_map() -> dict[str, str]:
    json = get_json()
    return dict(_require(json, "regionName"))