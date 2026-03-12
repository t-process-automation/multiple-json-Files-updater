from pathlib import Path
from typing import Any, Dict, List
from dataclasses import dataclass

from tools.common.json_loader import load_setting_json_file


@dataclass(frozen=True)
class Vl101ContentsClose:
    eventId: str
    region: str
    contentsClose: str | None


def delete_detect_from_vl101(path: Path) -> List[Vl101ContentsClose]:

    data: Dict[str, Any] = load_setting_json_file(path)

    list_data = data.get("list")

    if not isinstance(list_data, list):
        raise ValueError('"list" が存在しない or list型ではありません')

    results: List[Vl101ContentsClose] = []

    for item in list_data:
        event_id = item.get("eventId")

        tag = item.get("tag") or {}
        region_value = tag.get("regionName") or ""
        
        delete_detector = item.get("contentsClose")

        results.append(
            Vl101ContentsClose(
                eventId=event_id,
                region=region_value,
                contentsClose=delete_detector
            )
        )

    return results