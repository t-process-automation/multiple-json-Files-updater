from __future__ import annotations

from pathlib import Path
from datetime import datetime
import os


def build_notice_text(result: dict[str, dict]) -> str:
    blocks: list[str] = []

    for region, actions in result.items():
        lines: list[str] = []

        lines.append(f"{region}領域")
        lines.append("一覧ページへの追加と削除を行いました。")
        lines.append("ご確認とサーバーアップのご対応をよろしくお願い致します。")
        lines.append("")

        # event_id -> 資材情報
        materials_map = {
            item["event_id"]: item
            for item in actions.get("資材", [])
        }

        # 追加
        for item in actions.get("新規", []):
            event_id = item["event_id"]
            date = item["date"]
            mat = materials_map.get(event_id)

            if mat:
                lines.append(
                    f"追加　{date}　{event_id}　{mat['materialsText']}　{mat['materialsCreateDate']}"
                )
            else:
                lines.append(f"追加　{date}　{event_id}")

        # 更新
        for item in actions.get("更新", []):
            event_id = item["event_id"]
            date = item["date"]
            mat = materials_map.get(event_id)

            if mat:
                lines.append(
                    f"更新　{date}　{event_id}　{mat['materialsText']}　{mat['materialsCreateDate']}"
                )
            else:
                lines.append(f"更新　{date}　{event_id}")

        # 削除
        for item in actions.get("削除", []):
            event_id = item["event_id"]
            date = item["date"]
            lines.append(f"削除　{date}　{event_id}")

        lines.append("")

        # 採用した資材番号・資材作成年月日
        if actions.get("資材"):
            adopted = actions["資材"][0]
            lines.append(
                f"資材番号、資材作成年月日は "
                f"{adopted['event_id']} の {adopted['materialsText']}、{adopted['materialsCreateDate']} "
                f"を採用"
            )

        blocks.append("\n".join(lines))

    return "\n\n".join(blocks)


def set_text_widget(text_widget, result: dict[str, dict]) -> None:
    """
    Tkinter の Text ウィジェットに貼り付ける
    """
    notice_text = build_notice_text(result)
    text_widget.delete("1.0", "end")
    text_widget.insert("1.0", notice_text)


def save_notice_text(result: dict[str, dict]) -> Path:
    """
    logs フォルダに通知テキストを保存する
    例: logs/2026030800301234.text
    """

    text = build_notice_text(result)

    # このスクリプトのディレクトリ
    base_dir = Path(__file__).resolve().parent.parent.parent

    # logsフォルダ
    log_dir = base_dir / "logs"
    log_dir.mkdir(exist_ok=True)

    # タイムスタンプ
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:16]

    file_path = log_dir / f"{timestamp}.text"

    file_path.write_text(text, encoding="utf-8")

    os.startfile(log_dir)

    print(f"通知テキストを保存しました: {log_dir}\n\n")

    return file_path