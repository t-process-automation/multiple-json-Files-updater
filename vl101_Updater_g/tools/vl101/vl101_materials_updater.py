from __future__ import annotations

import json
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, Optional
from collections import defaultdict

from tools.common.json_loader import load_setting_json_file
from tools.vl101.vl101_context import Vl101Context
from tools.vl800.vl800_context import Vl800RequiredValues


def _parse_event_date(dt: str | None) -> Optional[date]:
    if not dt:
        return None

    try:
        return datetime.strptime(dt.strip(), "%Y/%m/%d").date()
    except ValueError:
        raise ValueError(f"eventDate の形式が不正です (YYYY/MM/DD): {dt}")


def update_materials_for_new_only(
    ctx: Vl101Context,
    event_data_map: Dict[str, Vl800RequiredValues],
    dup_results: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, str]]:
    
    # region の setting.json ごとに候補を集める
    groups: dict[Path, list[tuple[str, Vl800RequiredValues, date]]] = defaultdict(list)

    for eid, rv in event_data_map.items():
        info = dup_results.get(eid)
        # is_duplicate は dup_results という辞書の中に入っているキー
        if not info or info.get("is_duplicate"):
            continue  # 新規のみ

        region = rv.regionName
        if not region:
            raise ValueError(f"{eid}: regionName がありません")

        path = ctx.resolve_vl101_setting_json_path(region)

        if path is None:
            # regionが不正 / パス解決不能、など
            continue  # or raise ValueError

        dt = _parse_event_date(rv.eventDate)
        if dt is None:
            continue  # openがパース不能なら候補から除外（=代表になれない）
        
        # groups はこんな構造↓
        # groups = {
        #     Path("onc/setting.json"): [
        #         ("E1", rv1, date(2026,4,1)),
        #         ("E2", rv2, date(2026,5,1)),
        #         ("E3", rv3, date(2026,3,1)),
        #     ],

        #     Path("im/setting.json"): [
        #         ("E4", rv4, date(2026,6,1)),
        #         ("E5", rv5, date(2026,4,1)),
        #     ]
        # }
        groups[path].append((eid, rv, dt))

    # 各 setting.json(region) ごとに eventDate が一番新しいイベントを1つ選ぶ
    selected: dict[Path, tuple[str, Vl800RequiredValues]] = {
        path: max(items, key=lambda x: x[2])[:2]
        for path, items in groups.items()
    }

    results_materials = {}

    # 実際にファイルを書き換える
    for path, (eid, rv) in selected.items():
        data = load_setting_json_file(path)

        if rv.materialsText is not None:
            data["materialsText"] = rv.materialsText
        if rv.materialsCreateDate is not None:
            data["materialsCreateDate"] = rv.materialsCreateDate

        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        
        results_materials[eid] = {
            "region": rv.regionName,
            "path": path,
            "materialsText": rv.materialsText,
            "materialsCreateDate": rv.materialsCreateDate
        }
    
    return results_materials