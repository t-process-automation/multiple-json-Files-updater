【複数の JSON ファイル処理ツール】<br>
Scroll down for the English version.<br>

このツールは、複数の独立した JSON ファイル（vl800 配下）に含まれる要素を、ひとつの集約 JSON ファイル（vl101）へ自動で転記・更新する CLI ツールです。<br><br>
イベントデータの同期・更新処理を自動化し、以下の作業を実行します。<br>
1 vl101 の JSON ファイルを読み込み、期限切れ要素を検出して削除<br>
2 vl800 から新規イベントを追加（vl800 → vl101）<br>
3 既存イベントがある場合は内容を更新<br>
4 vl800 配下で最も日付が未来のデータから materialsText と materialsCreateDate をvl101へ転記<br>
5 操作結果の通知テキスト生成<br>
<br>
本ツールは vl800 と vl101 の 2 つのデータ構造を対象に処理を行います。<br>
<br>
【主な機能】<br>
1. 期限切れ要素の削除<br>
vl101 の JSON ファイルを読み込み、contentsClose が期限を過ぎたイベントを自動検出して削除します。<br>
期限判定は次の条件で行われます。contentsClose + grace_days<br> 
対象イベントは削除前に一覧表示され、削除実行前にユーザー確認が行われます。<br>
Do you want to proceed with deletion? (y/n)<br>
削除処理は sweep_close_contents() により実行されます。<br>
<br>
2. イベントID入力<br>
CLI で vl800 配下のフォルダ名（イベント ID）を入力します。<br>
　- 複数入力が可能<br>
　- 入力バリデーションあり
<br>
3. vl800 setting.json 解析<br>
入力されたフォルダ名から、次のファイルを取得して必要な値を抽出します。<br>
vl800/{eventId}/list/{region}/setting.json<br>
<br>
取得項目<br>
　- eventId<br>
　- eventDate<br>
　- regionName<br>
　- materialsText<br>
　- materialsCreateDate<br>
<br>
抽出処理は get_values_from_vl800_setting_json() で実装されています。<br>
<br>
4. 重複チェック<br>
vl101の一覧ページに同じeventIdが存在するかを確認します。<br>
判定結果に応じて次の処理を行います。<br>
　- 存在しない場合 → 新規追加<br>
　- 存在する場合 → 既存データを更新<br>
<br>
5. vl101 setting.json 更新<br>
新規または更新対象のイベントを次のファイルへ反映します。<br>
vl101/{region}/json/setting.json<br>
　
処理内容<br>
　- 期限切れ要素の削除<br>
　- 新規追加の場合は先頭に挿入。<br>
　- 更新があれば一度削除し先頭挿入。<br>
<br>
6. 資材情報更新<br>
新規追加されたイベントの中から最も eventDate が新しいイベントを基準として更新します。<br>
　- materialsText<br>
　- materialsCreateDate<br>
<br>
7. 操作結果通知テキスト生成<br>
処理結果から通知テキストを生成します。<br>

生成される内容<br>
　- 新規追加イベント<br>
　- 更新イベント<br>
　- 削除イベント<br>
　- materialsText 更新<br>
　- materialsCreateDate 更新<br>

結果は logs/ ディレクトリに保存されます。<br>
<br>
【実行方法】<br>
python tools/main.py または run_app.bat<br>
<br>
【必要環境】<br>
Python 3.10+<br>
<br>
使用ライブラリ<br>
　- json<br>
　- pathlib<br>
　- dataclasses<br>
　- collections<br>
<br>
外部ライブラリは使用していません。<br>
<br><br><br>


【Processing Multiple JSON Files】<br>
Multiple JSON File Processing Tool<br>

This CLI tool automatically transfers and updates elements from multiple independent JSON files (stored under vl800) into a single aggregated JSON file (vl101).<br><br>
It automates the synchronization and maintenance of event data by performing the following tasks:<br>
1.Read the vl101 JSON file, detect expired elements, and remove them<br>
2.Add new events from vl800 → vl101<br>
3.Update existing events if the same event already exists<br>
4.Copy materialsText and materialsCreateDate from the event with the latest date in vl800 to vl101<br>
5.Generate notification text describing the operation results<br>
<br>
This tool operates on two data structures:<br>
　- vl800<br>
　- vl101<br>
<br>
【Main Features】<br>
1. Expired Event Cleanup<br>
The tool reads the vl101 JSON file and automatically detects events whose contentsClose date has expired.<br>
The expiration condition is determined as follows:contentsClose + grace_days<br>
Target events are displayed before deletion, and user confirmation is required before executing the deletion.<br>
Do you want to proceed with deletion? (y/n)<br>
The deletion process is executed by:sweep_close_contents()<br>
<br>
2. Event ID Input<br>
Users enter vl800 folder names (event IDs) via the CLI.<br>
　- Multiple IDs can be entered<br>
　- Input validation is implemented<br>
<br>
3. vl800 setting.json Parsing<br>
The tool retrieves the following file based on the input folder name and extracts the required<br>values:vl800/{eventId}/list/{region}/setting.json<br>
<br>
Extracted fields:<br>
　- eventId<br>
　- eventDate<br>
　- regionName<br>
　- materialsText<br>
　- materialsCreateDate<br>
<br>
The extraction process is implemented in: get_values_from_vl800_setting_json()<br>
<br>
4. Duplicate Check<br>
The tool checks whether the same eventId already exists in the vl101 event list.<br>
<br>
Processing logic:<br>
　- If it does not exist → Add as a new event<br>
　- If it exists → Update the existing event<br>
<br>
5. vl101 setting.json Update<br>
New or updated events are written to the following file: vl101/{region}/json/setting.json<br>
<br>
Processing steps:<br>
　- Remove expired elements<br>
　- Insert new events at the top of the list<br>
　- If updating, remove the existing entry and insert the updated entry at the top<br>
<br>
6. Materials Information Update<br>
Among newly added events, the event with the latest eventDate is used as the reference to update:<br>
　- materialsText<br>
　- materialsCreateDate<br>
<br>
7. Operation Result Notification<br>
The tool generates notification text based on the processing results.<br>
<br>
The generated notification includes:<br>
　- Newly added events<br>
　- Updated events<br>
　- Deleted events<br>
　- Updates to materialsText<br>
　- Updates to materialsCreateDate<br>
<br>
The results are saved in the following directory: logs/<br>
<br>
【Run】<br>
run_app.bat<br>
<br>
【Requirements】<br>
Python 3.10+<br>
<br>
Standard libraries used:<br>
　- json<br>
　- pathlib<br>
　- dataclasses<br>
　- collections
