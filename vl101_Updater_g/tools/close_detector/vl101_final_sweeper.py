from __future__ import annotations
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import List
from dataclasses import dataclass

from tools.common.json_loader import load_setting_json_file
from tools.vl101.vl101_context import Vl101Context
from tools.close_detector.vl101_extractor import delete_detect_from_vl101
from tools.close_detector.vl101_target_filter import filter_expired_delete_detector


@dataclass
class DeletedEvent:
    path: Path
    event_id: str
    region: str
    close_date: str


def list_all_vl101_setting_json_paths(ctx: Vl101Context) -> List[Path]:
    # region_map の値(cal_xxx)が重複しても安全に set で潰す
    paths = {
        ctx.vl101_path / cal_dir / "json" / "setting.json"
        for cal_dir in ctx.region_map.values()
    }

    # 存在するものだけ(事故防止)
    return sorted([p for p in paths if p.is_file()])


def ask_yes_no(prompt: str) -> bool:
    while True:
        print(prompt)
        ans = input("> ").strip().lower()
        if ans in ("y", "n"):
            return ans == "y"
        print("y または n を入力してください。")


def sweep_close_contents(ctx: Vl101Context, *, grace_days=2) -> list[DeletedEvent]:
    """
    全vl101 setting.json を走査して、期限切れ(close+grace_daysが過去)の event を削除する。
    戻り値: 実際に削除した (path, eventId)
    """
    target_paths = list_all_vl101_setting_json_paths(ctx)

    print("--------------- VL101 setting.json - Contents to be Deleted ---------------")
    now = datetime.now()

    expired_summary: list[tuple[Path, str, str, str]] = []

    for path in target_paths:
        items = delete_detect_from_vl101(path)
        expired = filter_expired_delete_detector(items, now=now, grace_days=grace_days)

        for e in expired:
            close_date = e.close_dt.strftime("%Y/%m/%d")

            print(f"Group：{e.region} | EventId：{e.eventId} | Event Date：{close_date}")
            expired_summary.append((path, e.eventId, e.region, close_date))

    if not expired_summary:
        print("該当なし")
        print()
        return []

    print()

    if not ask_yes_no("削除を実行しますか? Do you want to proceed with deletion? ( y / n ): "):
        print("\n--------------- 中断しました。Operation canceled. ---------------\n")
        return []

    region_map = {eid: region for _, eid, region, _ in expired_summary}
    close_date_map = {eid: close_date for _, eid, _, close_date in expired_summary}

    # pathごとにまとめて1回で書き戻す
    grouped: dict[Path, set[str]] = defaultdict(set)
    for path, eid, _, _ in expired_summary:
        grouped[path].add(eid)

    deleted: list[DeletedEvent] = []

    print("\n--------------- 削除実行 Execute Deletion ---------------")
    
    for path, eids in grouped.items():
        data = load_setting_json_file(path)
        before = list(data.get("list", []))

        data["list"] = [item for item in before if item.get("eventId") not in eids]

        if len(data["list"]) == len(before):
            continue  # 変化なし

        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        for eid in sorted(eids):
            print(f"target EventId: {eid} | Executable File: ...\\{ctx.short_path(path)}")

            deleted.append(
                DeletedEvent(
                    path=path,
                    event_id=eid,
                    region=region_map[eid],
                    close_date=close_date_map[eid],
                )
            )
    print()

    return deleted


if __name__ == "__main__":
    ctx = Vl101Context.build()
    sweep_close_contents(ctx, grace_days=2)