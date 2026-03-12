from __future__ import annotations
from dataclasses import dataclass
import re
from datetime import datetime, date, timedelta
from typing import Iterable, List, Optional
from tools.close_detector.vl101_extractor import Vl101ContentsClose


FMT = "%Y/%m/%d %H:%M:%S"

@dataclass(frozen=True)
class Vl101ExpiredContentsClose:
    eventId: str
    contentsClose: str
    region: str
    close_dt: date


def _parse_close_date(s: str) -> date:
    """
    2026/05/01 19:40:00 → 2026/05/01
    2026/03/1 19:40:00 → 2026/03/1
    日付だけ取り出す
    """
    s = s.strip()

    m = re.match(r"^(\d{4})/(\d{1,2})/(\d{1,2})", s)
    if not m:
        raise ValueError(f"contentsCloseの形式が壊れています: {s}")

    # groups() は以下を取り出す。
    # (\d{4})
    # (\d{1,2})
    # (\d{1,2})
    y, mo, d = m.groups()

    return date(int(y), int(mo), int(d))


def filter_expired_delete_detector(
    items: Iterable[Vl101ContentsClose], # Vl101ContentsClose のリスト。
    *, # Pythonのキーワード専用引数
    now: Optional[datetime] = None, # 現在時刻
    grace_days: int = 2, # 猶予期間
) -> List[Vl101ExpiredContentsClose]:
    """
    contentsClose が期限切れのものだけ抽出
    """
    if now is None:
        now = datetime.now()

    threshold_date = (now.date() - timedelta(days=grace_days))

    expired: List[Vl101ExpiredContentsClose] = []

    for it in items:
        if not it.eventId or not it.contentsClose:
            continue

        close_dt = _parse_close_date(it.contentsClose)

        # ★ 日付のみ比較
        if close_dt <= threshold_date:
            expired.append(
                Vl101ExpiredContentsClose(
                    eventId=it.eventId,
                    contentsClose=it.contentsClose,
                    close_dt=close_dt,
                    region=it.region,
                )
            )

    return expired