VL Event Updater

このツールは、Web講演会イベントの setting.json を自動更新する CLIツールです。
以下の処理を自動化します。

1 期限切れイベントの削除
2 新規イベントの追加
3 既存イベントの更新
4 資材情報の更新
5 操作結果の通知テキスト生成

ツールは vl800 と vl101 の2つのデータ構造を対象に処理します。

【主な機能】
1. 期限切れイベント削除
contentsClose が期限を過ぎたイベントを自動検出し削除します。

期限判定は以下で行われます。
contentsClose + grace_days

該当イベントは削除前に一覧表示されます。

削除実行前に確認が表示されます。

Do you want to proceed with deletion? (y/n)

削除処理は sweep_close_contents() により実行されます。 


2. イベントID入力

ユーザーは追加対象のイベントIDを入力します。

複数入力可能
入力バリデーション有り

で実装されています。 

vl800_confirm_target_data


3. vl800 setting.json 解析

入力されたイベントIDから vl800/{eventId}/list/{region}/setting.json を取得し必要な値を抽出します。

取得項目
・eventId
・eventDate
・regionName
・materialsText
・materialsCreateDate

抽出処理は get_values_from_vl800_setting_json() で実装されています。 


4. 重複チェック

vl101の一覧ページに同じイベントIDが存在するか確認します。

・新規追加
・上書き更新

の判定を行います。


5. vl101 setting.json 更新

新規または更新対象イベントを vl101/{region}/json/setting.json に反映します。

処理内容
・既存イベント削除
・新イベント追加
・先頭挿入

実装
final_updates_to_vl101_setting_json()
vl101_setting_json_writer


6. 資材情報更新

新規イベントの中から最も新しい eventDate のイベントを基準として

materialsText
materialsCreateDate

を更新します。


実装
update_materials_for_new_only()
vl101_materials_updater


7. 操作結果通知テキスト生成

処理結果から通知テキストを生成します。

追加
更新
削除
資材

結果は logs/ に保存されます。

実装
save_notice_text()
get_text


【実行方法】
python tools/main.py または run_app.bat


【設定ファイル】
data.json

{
  "regionName": {
    "regionA": "sample_aaa",
    "regionB": "sample_bbb",
    "regionC": "sample_ccc",
    "regionD": "sample_ddd"
  },

  "vl800_path": "./sample_result/vl800",

  "vl101_path": "./sample_result/vl101"
}


【必要環境】
Python 3.10+

使用ライブラリ
json
pathlib
dataclasses
collections

外部ライブラリは使用していません。

