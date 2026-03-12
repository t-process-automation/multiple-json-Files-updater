from __future__ import annotations
import sys

from tools.common.result_open_folders import open_folders_in_explorer

from tools.vl800.vl800_confirm_target_data import (
    collect_event_data,
    read_add_for_vl800_event_ids,
    print_target_event_summary,
    print_target_setting_json_paths
)
from tools.vl101.vl101_event_checker import showing_new_or_duplicate_results
from tools.vl101.vl101_context import Vl101Context
from tools.vl800.vl800_context import NotListTargetError
from tools.vl101.vl101_setting_json_writer import final_updates_to_vl101_setting_json
from tools.close_detector.vl101_final_sweeper import sweep_close_contents
from tools.vl101.vl101_materials_updater import update_materials_for_new_only
from tools.text_generator.eventIds_collecter import collect_all_eventIds_by_region
from tools.text_generator.get_text import save_notice_text


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


if __name__ == "__main__":
    ctx = Vl101Context.build()

    # sweep_close_contents(grace_days=2)

    deleted = sweep_close_contents(ctx, grace_days=2)
    deleted_results = [(d.event_id, d.region, d.close_date) for d in deleted]

    if deleted:
        open_folders_in_explorer(d.path for d in deleted)

    while True:
        try:
            add_ids = read_add_for_vl800_event_ids(max_items=10)

            # qだけで終わった(空入力)なら、もう一回入力へ戻す
            if not add_ids:
                eprint("\n入力が空です。もう一度入力してください。\n\n")
                continue

            event_data_map = collect_event_data(add_ids)

            print_target_event_summary(event_data_map)
            print_target_setting_json_paths(ctx, event_data_map)

            # 念のため : 対象ゼロなら戻す(空でy/nまで行くのを防ぐ)
            if not event_data_map:
                eprint("処理対象のEventIdがありません。最初からやり直してください。\n")
                continue

            result = showing_new_or_duplicate_results(ctx, event_data_map)
            if not result:
                continue

            dup_results, new_datas, duplicate_datas = result

            added_results = [
                (eid, region, event_data_map[eid].eventDate)
                for eid, region in new_datas.items()
            ]

            updated_results = [
                (eid, region, event_data_map[eid].eventDate)
                for eid, region in duplicate_datas.items()
            ]

            materials_results = update_materials_for_new_only(
                ctx,
                event_data_map,
                dup_results
            )

            open_folders_in_explorer(final_updates_to_vl101_setting_json(ctx, event_data_map))

            text_result = collect_all_eventIds_by_region(
                deleted_results,
                added_results,
                updated_results,
                materials_results
            )

            save_notice_text(text_result)

        except NotListTargetError as e:
            # NGを出して最初の入力に戻す
            eprint(f"NG : {e}")
            eprint("")  # 空行
            continue

        except Exception as e:
            # それ以外は従来通り停止
            eprint(f"\nエラー: {e}")
            eprint("Enterキーで終了します...")
            input()
            break
