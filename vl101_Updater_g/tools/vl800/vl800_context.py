from dataclasses import dataclass
from pathlib import Path
from typing import Any
from tools.common.path_utils import get_json, get_region_map


class NotListTargetError(Exception):
    """一覧追加対象外のeventIdが含まれている(例:listフォルダ無し)"""
    pass

# VL800処理に必要な前提情報をまとめた入れ物
# このクラスはデータ保持専用
# frozen=True : インスタンス作成後に値を書き換えられない
@dataclass(frozen=True)
class Vl800Context:
    base_path: Path
    region_map: dict[str, str]

    # クラス自体にぶら下がるメソッド
    @classmethod
    # build() : VL800処理を始める前に必要な前提を、ここで全部確定させる
    # cls : Vl800Context(クラス)
    def build(cls) -> "Vl800Context":
        cfg = get_json()
        vl800 = cfg.get("vl800_path")
        if not vl800:
            raise KeyError("data.json に 'vl800_path' がありません")
        return cls(base_path=Path(vl800), region_map=get_region_map())

    # self : このクラスのインスタンスそのもの
    # ctx = Vl800Context.build()
    # ctx.resolve_vl800_setting_json_path("20271111TEST")
    # つまり ctx が self
    def resolve_vl800_setting_json_path(self, eventId: str) -> Path | None: # 戻り値は Path または None
        # 1) eventId dir
        event_dir = self.base_path / eventId
        if not event_dir.is_dir():
            print()
            raise NotListTargetError(f"{eventId} : vl800配下に対象の eventId が存在しません。修正後に再トライしてください。")

        # 2) list dir
        list_dir = event_dir / "list"
        if not list_dir.is_dir():
            print()
            raise NotListTargetError(f"{eventId} : 一覧追加対象ではありません(list無し。修正後に再トライしてください。)")

        # 3) region dir (onc/im/ns/dmg のどれか)
        region_dir = None
        for key in self.region_map:
            p = list_dir / key
            if p.is_dir():
                region_dir = p
                break

        if region_dir is None:
            print()
            raise NotListTargetError(f"{eventId}/list : 領域フォルダが存在しません。修正後に再トライしてください。")

        # 4) setting.json
        setting_json = region_dir / "setting.json"
        if not setting_json.is_file():
            print()
            raise NotListTargetError(f"\n{eventId}/list/{region_dir.name} : setting.json が見つかりません。修正後に再トライしてください。")

        return setting_json


@dataclass(frozen=True)
class Vl800RequiredValues:
    materialsText: str | None
    materialsCreateDate: str | None
    list: list[dict[str, Any]]
    eventId: str | None
    eventDate: str | None
    regionName: str | None
    item: dict[str, Any] | None