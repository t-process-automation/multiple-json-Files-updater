from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Any, List, Iterable

from tools.common.json_loader import load_setting_json_file
from tools.vl101.vl101_context import Vl101Context
from tools.vl800.vl800_context import Vl800RequiredValues
from tools.common.result_open_folders import open_folders_in_explorer


def pick_item_from_list(rv: Vl800RequiredValues, event_id: str) -> dict[str, Any]:
    """vl800 の setting.json から eventId が一致する dict(= list内1要素) を返す。"""
    for item in rv.list:
        if item.get("eventId") == event_id:
            return item
    raise ValueError(f"{event_id}: vl800側setting.json内の'list'に該当eventIdが見つかりません")


def final_updates_to_vl101_setting_json(
    ctx: Vl101Context,
    event_data_map: Dict[str, Vl800RequiredValues],
) -> list[Path]:
    """
    vl101_setting_json を更新する関数
    event_data_map の各 eventId について、
    - vl800側の list 内要素(dict) を丸ごと取得
    - vl101側 setting.json["list"] の先頭に挿入
    - 既に同じ eventId があれば置換(古い要素は削除して先頭に入れ直す)
    """

    updated_paths: list[Path] = []

    # by_path の中身はつまりこんな感じ
    # {
    #     Path("onc/setting.json"): [
    #         ("20271111TEST", {...}),
    #         ("20272222TEST", {...})
    #     ],
    #     Path("im/setting.json"): [
    #         ("20273333TEST2", {...})
    #     ]
    # }
    by_path: dict[Path, list[tuple[str, dict[str, Any]]]] = defaultdict(list)

    # どのvl101 setting.jsonを更新するかを決める
    for event_id, rv in event_data_map.items():
        region = rv.regionName
        if not region:
            raise ValueError(f"{event_id}: regionName がありません")

        # vl101側の setting.json パス
        path = ctx.resolve_vl101_setting_json_path(region)

        # 差し込みたい dict(list内1要素)
        item = pick_item_from_list(rv, event_id)

        if path is None:
            # regionが不正 / パス解決不能、など
            continue  # or raise ValueError
        by_path[path].append((event_id, item))

    # path  = Path("onc/setting.json")
    # items = [
    #     ("20271111TEST", {...}),
    #     ("20272222TEST", {...})
    # ]
    for path, items in by_path.items():
        data = load_setting_json_file(path)
        # lst = 元のlistのコピー、つまり vl101 setting.json の "list":[]のコピー
        lst: List[dict[str, Any]] = list(data.get("list", []))

        # vl101 setting.json の "list":[] の中にある eventId を index 化
        def rebuild_index():
            return {x.get("eventId"): i for i, x in enumerate(lst)}

        idx = rebuild_index()

        # 入力順を保ちつつ先頭に積みたいので reverse して insert(0)
        for event_id, item in reversed(items):
            if event_id in idx:
                # vl101 list内にある既存の eventId を含む塊ごと削除する、つまり「置換」のための削除。
                lst.pop(idx[event_id])

            # 先頭に追加
            lst.insert(0, item)
            idx = rebuild_index()

        data["list"] = lst

        # 書き戻し（indentは好みでOK）
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        updated_paths.append(path)

        print(f"更新完了: ...\\{ctx.short_path(path)} (+{len(items)} items)")

    return updated_paths


# def open_updated_vl101_folders(paths: Iterable[Path]) -> None:
#     """
#     vl101 setting.json を更新したフォルダを開く。
#     """
#     open_folders_in_explorer(paths)