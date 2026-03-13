Processing multiple JSON files

このツールは、複数の独立したJSONファイル（vl800に格納）の要素を、ひとまとめに集積したJSONファイル（vl101）に自動で転記CLIツールです。
以下の処理を自動化します。

1 JSONファイル（vl101）を読込、期限切れの要素を抽出し削除
2 新規要素を追加（vl800→vl01）
3 既にある場合は既存の要素を更新
4 vl800配下で最も日付が未来のデータのmaterialsText、materialsCreateDateをvl101へ転記
5 操作結果の通知テキスト生成

このツールは vl800 と vl101 の2つのデータ構造を対象に処理します。

【主な機能】
1. 期限切れ要素の削除
　vl101のJSONファイルを読み込み、contentsClose が期限を過ぎたイベントを自動検出し削除します。

　期限判定は以下で行われます。
　contentsClose + grace_days

　該当する要素は削除前に一覧表示されます。
　削除実行前に確認が表示されます。Do you want to proceed with deletion? (y/n)
　削除処理は sweep_close_contents() により実行されます。 

2. イベントID入力
　vl800配下のフォルダ名をCLIで入力。
　複数入力可能。入力バリデーション有り。

3. vl800 setting.json 解析
　入力されたフォルダ名から vl800/{eventId}/list/{region}/setting.json を取得し必要な値を抽出します。

　取得項目
　・eventId
　・eventDate
　・regionName
　・materialsText
　・materialsCreateDate

　抽出処理は get_values_from_vl800_setting_json() で実装されています。 

4. 重複チェック
　vl101の一覧ページに同じeventIdが存在するかを確認。

　・なければ新規追加
　・あれば上書き更新

　の判定を行います。

5. vl101 setting.json 更新
　新規または更新対象イベントを vl101/{region}/json/setting.json に反映します。
　処理内容
　　・期限切れの既存要素を削除
　　・新規追加の場合は先頭挿入。
　　・更新があれば一度削除し先頭挿入。

6. 資材情報更新
　新規追加分の中から最も新しい eventDate のイベントを基準として materialsText、materialsCreateDate を更新します。

7. 操作結果通知テキスト生成
　処理結果から通知テキストを生成します。

　更新内容（新規追加、更新、削除、materialsText、materialsCreateDate）を生成。
　結果は logs/ に保存されます。

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
　・json
　・pathlib
　・dataclasses
　・collections

　外部ライブラリは使用していません。
