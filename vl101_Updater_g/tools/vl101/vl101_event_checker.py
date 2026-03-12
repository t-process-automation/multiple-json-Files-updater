from collections import defaultdict
from typing import Dict, Any
from tools.common.json_loader import load_setting_json_file
from tools.vl101.vl101_context import Vl101Context
from tools.vl800.vl800_context import Vl800RequiredValues


def check_event_duplicates(
    ctx: Vl101Context,
    event_data_map: Dict[str, Vl800RequiredValues]
) -> Dict[str, Dict[str, Any]]:
    """vl800から抽出したイベント情報(eventId)が、vl101側の一覧setting.jsonに既に入ってないか?を領域(region)ごとに重複チェックする"""
    # キー : Path(vl101のsetting.jsonパス)
    # 値 : event_idのリスト
    # の辞書を作る
    # キーが初登場したら、自動で空の list を作ってくれる辞書
    region_events = defaultdict(list)

    for event_id, required_values in event_data_map.items():
        region = required_values.regionName

        if not region:
            raise ValueError(f"{event_id}: regionName が取得できません(setting.jsonのlist/regionNameを確認)")

        path = ctx.resolve_vl101_setting_json_path(region)
        # イメージはこれ↓ vl101パス単位でイベントをまとめる
        # region_events =
        # {
        #     Path("cal_onc/json/setting.json"): ["E1","E2"],
        #     Path("cal_im/json/setting.json"): ["E3"]
        # }
        region_events[path].append(event_id)

    duplicate_results: Dict[str, Dict[str, Any]] = {}
    
    # regionごとにVL101のsetting.jsonを読み込み、各eventIdが既に存在するか判定して結果を作る
    for path, ids in region_events.items():
        setting_json = load_setting_json_file(path)

        existing_ids = {
            item.get("eventId")
            for item in setting_json.get("list", [])
        }

        full_path = path
        short_path = ctx.short_path(path)

        for eid in ids:
            duplicate_results[eid] = {
                "path": full_path,
                "short_path": short_path,
                "is_duplicate": eid in existing_ids
            }

    return duplicate_results


def ask_yes_no(prompt: str) -> bool:
    while True:
        print(prompt)
        ans = input("> ").strip().lower()
        if ans in ("y", "n"):
            return ans == "y"
        print("y または n を入力してください。")


def showing_new_or_duplicate_results(ctx: Vl101Context, event_data_map: Dict[str, Vl800RequiredValues]):
    dup_results = check_event_duplicates(ctx, event_data_map)

    print("\n--------------- 重複チェック結果 Duplicate Check Results ---------------")

    duplicate_datas = {}
    new_datas = {}

    for eid, info in dup_results.items():
        if info["is_duplicate"]:
            duplicate_datas[eid] = event_data_map[eid].regionName
        else:
            new_datas[eid] = event_data_map[eid].regionName

    if duplicate_datas:
        print(f"書き換え {len(duplicate_datas)}件 : {' '.join(duplicate_datas)}")
    if new_datas:
        print(f"新規追加 {len(new_datas)}件 : {' '.join(new_datas)}")

    if not ask_yes_no("\n処理を続けますか? ( y / n ): "):
        print("\n--------------- 中断しました。Operation canceled. ---------------\n")
        return
    print()

    return dup_results, new_datas, duplicate_datas