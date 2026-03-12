from __future__ import annotations

from pathlib import Path
import os
from typing import Iterable


def open_folders_in_explorer(paths: Iterable[Path]) -> None:
    """
    paths（ファイル or フォルダ）の親フォルダをエクスプローラーで開く。
    重複は除外。
    """
    folders = []
    seen = set()

    for p in paths:
        p = Path(p)
        folder = p if p.is_dir() else p.parent
        try:
            folder = folder.resolve()
        except Exception:
            # resolve失敗しても開ける可能性はあるのでそのまま
            pass

        key = str(folder)
        if key in seen:
            continue
        seen.add(key)
        folders.append(folder)

    for folder in folders:
        # 1) 開くだけならこれでOK（通常表示）
        os.startfile(str(folder))
        # 2) もし “setting.json を選択状態” にしたいならこっち：
        # subprocess.Popen(["explorer", "/select,", str(folder / "setting.json")])