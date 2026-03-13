【複数の JSON ファイル処理ツール】<br>
Scroll down for the English version.

  このツールは、複数の独立した JSON ファイル（vl800 配下）に含まれる要素を、ひとつの集約 JSON ファイル（vl101）へ自動で転記・更新する CLI ツールです。
  イベントデータの同期・更新処理を自動化し、以下の作業を実行します。

  1 vl101 の JSON ファイルを読み込み、期限切れ要素を検出して削除
  2 vl800 から新規イベントを追加（vl800 → vl101）
  3 既存イベントがある場合は内容を更新
  4 vl800 配下で最も日付が未来のデータから materialsText と materialsCreateDate をvl101へ転記
  5 操作結果の通知テキスト生成

  本ツールは vl800 と vl101 の 2 つのデータ構造を対象に処理を行います。

【主な機能】
 1. 期限切れ要素の削除
  vl101 の JSON ファイルを読み込み、contentsClose が期限を過ぎたイベントを自動検出して削除します。

  期限判定は次の条件で行われます。contentsClose + grace_days
  
  対象イベントは削除前に一覧表示され、削除実行前にユーザー確認が行われます。
  Do you want to proceed with deletion? (y/n)
　
  削除処理は sweep_close_contents() により実行されます。 

2. イベントID入力
　CLI で vl800 配下のフォルダ名（イベント ID）を入力します。
　・複数入力が可能
　・入力バリデーションあり

3. vl800 setting.json 解析
　入力されたフォルダ名から、次のファイルを取得して必要な値を抽出します。
　vl800/{eventId}/list/{region}/setting.json

　取得項目<br>
　- eventId<br>
　- eventDate<br>
　- regionName<br>
　- materialsText<br>
　- materialsCreateDate<br>

　抽出処理は get_values_from_vl800_setting_json() で実装されています。 
 
4. 重複チェック
　vl101の一覧ページに同じeventIdが存在するかを確認します。
　判定結果に応じて次の処理を行います。

　・存在しない場合 → 新規追加
　・存在する場合 → 既存データを更新
5. vl101 setting.json 更新
　新規または更新対象のイベントを次のファイルへ反映します。
　vl101/{region}/json/setting.json
　
　処理内容
　・期限切れ要素の削除
　・新規追加の場合は先頭に挿入。
　・更新があれば一度削除し先頭挿入。

6. 資材情報更新
　新規追加されたイベントの中から最も eventDate が新しいイベントを基準として更新します。
　・materialsText
　・materialsCreateDate

7. 操作結果通知テキスト生成
　処理結果から通知テキストを生成します。

　生成される内容
　・新規追加イベント
　・更新イベント
　・削除イベント

materialsText 更新
materialsCreateDate 更新

結果は logs/ ディレクトリに保存されます。

【実行方法】
　python tools/main.py または run_app.bat

【必要環境】
　Python 3.10+

　使用ライブラリ
　・json
　・pathlib
　・dataclasses
　・collections

　外部ライブラリは使用していません。



【Processing Multiple JSON Files】
Multiple JSON File Processing Tool

This CLI tool automatically transfers and updates elements from multiple independent JSON files (stored under vl800) into a single aggregated JSON file (vl101).
It automates the synchronization and maintenance of event data by performing the following tasks:

1.Read the vl101 JSON file, detect expired elements, and remove them
2.Add new events from vl800 → vl101
3.Update existing events if the same event already exists
4.Copy materialsText and materialsCreateDate from the event with the latest date in vl800 to vl101
5.Generate notification text describing the operation results

This tool operates on two data structures:
・vl800
・vl101

【Main Features】
1. Expired Event Cleanup
The tool reads the vl101 JSON file and automatically detects events whose contentsClose date has expired.
The expiration condition is determined as follows:contentsClose + grace_days
Target events are displayed before deletion, and user confirmation is required before executing the deletion.
Do you want to proceed with deletion? (y/n)
The deletion process is executed by:sweep_close_contents()

2. Event ID Input
Users enter vl800 folder names (event IDs) via the CLI.
・Multiple IDs can be entered
・Input validation is implemented

3. vl800 setting.json Parsing

The tool retrieves the following file based on the input folder name and extracts the required values:vl800/{eventId}/list/{region}/setting.json

Extracted fields:
・eventId
・eventDate
・regionName
・materialsText
・materialsCreateDate

The extraction process is implemented in:get_values_from_vl800_setting_json()

4. Duplicate Check
The tool checks whether the same eventId already exists in the vl101 event list.

Processing logic:
・If it does not exist → Add as a new event
・If it exists → Update the existing event

5. vl101 setting.json Update
New or updated events are written to the following file:vl101/{region}/json/setting.json

Processing steps:
・Remove expired elements
・Insert new events at the top of the list
・If updating, remove the existing entry and insert the updated entry at the top

6. Materials Information Update
Among newly added events, the event with the latest eventDate is used as the reference to update:
・materialsText
・materialsCreateDate

7. Operation Result Notification
The tool generates notification text based on the processing results.

The generated notification includes:
・Newly added events
・Updated events
・Deleted events
・Updates to materialsText
・Updates to materialsCreateDate

The results are saved in the following directory: logs/

【Run】
run_app.bat

【Requirements】
Python 3.10+

Standard libraries used:
・json
・pathlib
・dataclasses
・collections
