from collections import defaultdict
from tools.vl101.vl101_context import Vl101Context
from tools.close_detector.vl101_final_sweeper import sweep_close_contents
from tools.vl101.vl101_event_checker import showing_new_or_duplicate_results
from tools.vl101.vl101_materials_updater import update_materials_for_new_only


def collect_deleted_eventIds():
    deleted = sweep_close_contents(grace_days=2)

    results = []
    for d in deleted:
        results.append((d.event_id, d.region, d.close_date))

    return results


def collect_add_or_update_eventIds(event_data_map):
    ctx = Vl101Context.build()
    result = showing_new_or_duplicate_results(ctx, event_data_map)

    if not result:
        return [], [], {}

    dup_results, new_datas, duplicate_datas = result

    materials_results = update_materials_for_new_only(
        ctx,
        event_data_map,
        dup_results
    )

    added_results = [
        (eid, event_data_map[eid].regionName, event_data_map[eid].eventDate)
        for eid in new_datas
    ]

    updated_results = [
        (eid, event_data_map[eid].regionName, event_data_map[eid].eventDate)
        for eid in duplicate_datas
    ]

    return added_results, updated_results, materials_results


def collect_all_eventIds_by_region(deleted_results, added_results, updated_results, materials_results):
    grouped = defaultdict(lambda: {
        "削除": [],
        "新規": [],
        "更新": [],
        "資材": [],
    })

    for event_id, region, date in deleted_results:
        grouped[region]["削除"].append({
            "event_id": event_id,
            "date": date,
        })

    for event_id, region, date in added_results:
        grouped[region]["新規"].append({
            "event_id": event_id,
            "date": date,
        })

    for event_id, region, date in updated_results:
        grouped[region]["更新"].append({
            "event_id": event_id,
            "date": date,
        })
    
    for event_id, info in materials_results.items():
        region = info["region"]
        grouped[region]["資材"].append({
            "event_id": event_id,
            "materialsText": info["materialsText"],
            "materialsCreateDate": info["materialsCreateDate"],
        })

    result = dict(grouped)

    print("\n--------------- 領域別操作結果 ---------------")

    for region, actions in result.items():
        print(f"領域: {region}")

        for label in ["削除", "新規", "更新"]:
            if actions[label]:
                for item in actions[label]:
                    print(f"{label} : {item['date']} | {item['event_id']}")

        if actions["資材"]:
            for item in actions["資材"]:
                print(
                    f"資材 : {item['event_id']} | "
                    f"資材番号 {item['materialsText']} | "
                    f"資材作成年月日 {item['materialsCreateDate']}"
                )
        print()

    return result