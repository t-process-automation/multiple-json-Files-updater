from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from tools.common.path_utils import get_paths, get_region_map

# VL101処理に必要な前提情報をまとめた入れ物
# このクラスはデータ保持専用
# frozen=True : インスタンス作成後に値を書き換えられない
@dataclass(frozen=True)
class Vl101Context:
    vl101_path: Path
    region_map: dict[str, str]

    # クラス自体にぶら下がるメソッド
    @classmethod
    # build() : VL101処理を始める前に必要な前提を、ここで全部確定させる
    # cls : Vl101Context(クラス)
    # -> "Vl101Context" : この関数は Vl101Context を返すという宣言。
    def build(cls) -> "Vl101Context":
        paths = get_paths()
        return cls(
            vl101_path = paths.vl101_path,
            region_map = get_region_map(),
        )

    # self : このクラスのインスタンスそのもの
    # ctx = Vl800Context.build()
    # ctx.resolve_vl800_setting_json_path("20271111TEST")
    # つまり ctx が self
    def resolve_vl101_setting_json_path(self, region_name: str) -> Path:
        key = (region_name or "").strip()
        if not key:
            raise ValueError("regionName が空です")

        cal_dir = self.region_map.get(key)
        if not cal_dir:
            raise KeyError(f"未知の regionName: {key} (region_mapに存在しない)")

        return self.vl101_path / cal_dir / "json" / "setting.json"


    def short_path(self, p: Path) -> Path:
        try:
            return p.relative_to(self.vl101_path)
        except ValueError:
            return p
