Processing multiple JSON files
複数の JSON ファイル処理ツール

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

　期限判定は次の条件で行われます。
　contentsClose + grace_days

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

　取得項目
　・eventId
　・eventDate
　・regionName
　・materialsText
　・materialsCreateDate

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

