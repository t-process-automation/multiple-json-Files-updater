from __future__ import annotations
import re
import sys
from pathlib import Path
from typing import Dict, List, Any
from tools.common.json_loader import load_setting_json_file
from tools.vl101.vl101_context import Vl101Context
from tools.vl800.vl800_context import Vl800Context, Vl800RequiredValues


DEFAULT_EVENT_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def read_add_for_vl800_event_ids(max_items: int = 10) -> List[str]:
    print("---------- イベントデータの取得 vl800 setting.json ----------")
    eprint("追加するイベントIDを入力してください。Please enter the Event ID to add.")
    eprint("If there are multiple IDs, press Enter after each one.")
    eprint("入力が終われば q を入力してください。Enter `q` when finished.\n")

    result: List[str] = []
    while True:
        # プロンプトを stderr に出してから input()（promptは使わない）
        sys.stderr.write("> ")
        sys.stderr.flush()
        raw = input().strip()

        if raw.lower() == "q":
            break

        if not raw:
            continue

        if not DEFAULT_EVENT_ID_PATTERN.match(raw):
            eprint("形式エラー：半角英数、_、- のみ使用可能です | Format error: Only alphanumeric characters, _, and - are allowed.")
            continue

        if raw in result:
            eprint("既に入力済みです | Already entered.")
            continue

        if len(result) >= max_items:
            eprint(f"最大{max_items}件までです")
            break

        result.append(raw)

    return result


def create_dict_for_vl800_event_ids(eventIds: List[str]) -> Dict[str, Path]:
    """
    vl800 の eventId/list/領域/setting.json までのパスを確定
    例: こんなdictを作る。
        {
            "20271111TEST": Path(r"\\fs03\\...\vl800\\list\\onc\20271111TEST\\setting.json"),
            "20272222TEST": Path(r"\\fs03\\...\vl800\\list\\im\20272222TEST\\setting.json")
        }
    """
    ctx = Vl800Context.build()
    # found : キーが文字列(str)、値がPathの辞書。型宣言付きの空辞書。
    found: Dict[str, Path] = {}

    for eventId in eventIds:
        setting_json = ctx.resolve_vl800_setting_json_path(eventId)
        if setting_json is None:
            raise ValueError(f"{eventId}: vl800 setting.json が見つかりません")
        found[eventId] = setting_json

    return found


def get_values_from_vl800_setting_json(data: Dict[str, Any], target_eventId: str | None = None) -> Vl800RequiredValues:
    list_data = data.get("list")

    if not isinstance(list_data, list) or len(list_data) == 0:
        raise ValueError('vl800 setting.json の "list" が空 or 存在しません。')

    item = list_data[0]  # 仕様：list は必ず 1 件

    event_id = item.get("eventId")
    if target_eventId is not None and event_id != target_eventId:
        raise ValueError(f"イベントIDが無いか合致しません: expected={target_eventId}, actual={event_id}")

    event_date = item.get("eventDate")
    if event_date is None:
        raise ValueError(f"講演会日が設定されていません: eventDate={event_date}")

    region_name = (item.get("tag") or {}).get("regionName")

    # list は [ {item} ]、item は {item}
    return Vl800RequiredValues(
        materialsText=data.get("materialsText"),
        materialsCreateDate=data.get("materialsCreateDate"),
        list=list_data,
        eventId=event_id,
        eventDate=event_date,
        regionName=region_name,
        item=item
    )


def collect_event_data(eventIds: List[str]) -> Dict[str, Vl800RequiredValues]:
    paths = create_dict_for_vl800_event_ids(eventIds)

    results: Dict[str, Vl800RequiredValues] = {}
    for eventId, path in paths.items():
        data = load_setting_json_file(path)
        results[eventId] = get_values_from_vl800_setting_json(data, eventId)

    return results


def print_target_event_summary(results: Dict[str, Vl800RequiredValues]) -> None:
    print("\n--------------- 処理対象イベントID | Target Event IDs ---------------")
    for event_id, rv in results.items():
        print(
            f"OK : {event_id} : "
            f"{rv.eventDate}, "
            f"{rv.regionName}, "
            f"{rv.materialsText}, "
            f"{rv.materialsCreateDate}"
        )


def print_target_setting_json_paths(
    vl101_ctx: Vl101Context,
    results: Dict[str, Vl800RequiredValues],
) -> None:
    print("\n--------------- 操作対象 setting.json | Target setting.json File---------------")

    unique: set[Path] = set()

    for event_id, rv in results.items():
        region = rv.regionName
        if not region:
            raise ValueError(f"{event_id}: regionName がありません")

        p = vl101_ctx.resolve_vl101_setting_json_path(region)
        if p:
            unique.add(p)

    for path in sorted(unique):
        print(path)