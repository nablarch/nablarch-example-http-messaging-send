# task-3 Completion Check

## 変換実行結果

- 対象 Excel（所在確認）: `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest.xls`（49664B）／同名 `.xlsx`（26965B）が併存（下記「.xls/.xlsx 併存チェック」）。src 配下の Excel はこの2ファイルのみ
- 未使用の `.xlsx` を `git rm` で変換前に削除した後、`LANG=ja_JP.UTF-8 LC_ALL=ja_JP.UTF-8 mvn com.nablarch.framework:nablarch-testing-converter:1.0.0-SNAPSHOT:convert`（pom の `<configuration>`: from=xls / to=yaml / input=output=`${project.basedir}/src/test/java` / overwrite=true）を実行 → rc=0, BUILD SUCCESS
- 生成 YAML（`src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest/`）: `setUpDb.yaml`(0B) / `testAbNormalEnd.yaml` / `testNormalEndExistAllFields.yaml` / `testNormalEndOnlyRequireFields.yaml`（Excel の4シートに1対1対応）
- 生成 YAML は POMなし一時ディレクトリでの個別変換結果（`xls-xlsx-comparison/from-xls/`）と `diff -r` 差分なし。過去実施分（`f941f6a` 時点の YAML）ともバイト一致
- converter の警告（Excel 由来の既存データ特性。変換で生じたものではない）: `testAbNormalEnd` シートで `EXPECTED_TABLE[1]` の2ブロック目（Excel 78〜80行の `PROJECT_INS_REQ`）が別ブロックを挟んでいるため出力されない。NTF も Excel 形式で後ろのブロックを読まないため、挙動は Excel と同一
- `.xls` 本体は未削除（削除は Task #4）

## Scripts（本タスクで作成）

- `.rn/ntf-yaml-support/scripts/dump_xlsx_cells.py`: `.xlsx` の全シートのセル値を標準ライブラリのみ（zipfile + ElementTree）で TSV 出力する。converter（Apache POI）と独立した経路で Excel 側の値を目視確認するため（環境に xlrd / openpyxl なし）
- `.rn/ntf-yaml-support/scripts/compare_sampling.py`: `.xlsx` のセル値と生成 YAML の値を、ファイル毎に定義したサンプル箇所で自動突合する（結果: `checks/task-3-sampling.tsv`）。Excel 側には NTF が読み込み時に行う表記上の正規化のみ適用する: (1) 数値セルは `PoiXlsReader` の `Cell#toString()` により `"1.0"` 形式、(2) フィールド長 `-` の電文フィールドは `DataFileFragment#addValue` が `\s*[\r\n]\s*` を除去、(3) セル値 `null` は `nullInterpreter` が null と解釈
- Excel 側入力には `.xlsx` を用いた（`.xls` と `.xlsx` の変換結果がバイト一致であることを併存チェックで確認済みのため、`.xlsx` のセル値は `.xls` と同内容とみなせる）

## Completion Criteria

| Criterion | Self-check | Evidence | QA | QA Evidence |
|---|---|---|---|---|
| 変換対象の全 Excel に対応する YAML が生成されている | OK | 変換対象 `ProjectSaveMessageActionRequestTest.xls` の4シート（setUpDb / testNormalEndExistAllFields / testNormalEndOnlyRequireFields / testAbNormalEnd）に対応する YAML 4ファイルを生成。convert rc=0 | - | - |
| サンプリング比較で Excel と YAML の内容が一致している | OK | `compare_sampling.py` で 19件＋setUpDb を突合し NG 0（testNormalEndExistAllFields 7 / testNormalEndOnlyRequireFields 5 / testAbNormalEnd 7、setUpDb は元データ0件のため全件＝データブロックなしを確認）。差異なし | - | - |
| 変換後の YAML がコミットされている | OK | Task #3 コミットに YAML 4ファイル・`.xlsx` 削除・併存チェック結果・scripts を含める（`.xls` は含めない＝未削除） | - | - |

## Sampling Comparison（task-3 のみ）

| YAML ファイル | 比較件数 | レコードキー/行 | Excel 値 | YAML 値 | 一致 |
| --- | --- | --- | --- | --- | --- |
| `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest/testNormalEndExistAllFields.yaml` | 7 | testShots[no=1].description / Excel row4 | メッセージ送信成功 | メッセージ送信成功 | OK |
| `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest/testNormalEndExistAllFields.yaml` | 7 | SETUP_TABLE[1] PROJECT_INS_REQ_ID=1 PROJECT_NAME / Excel row10 | プロジェクト００１ | プロジェクト００１ | OK |
| `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest/testNormalEndExistAllFields.yaml` | 7 | SETUP_TABLE[1] PROJECT_INS_REQ_ID=1 CLIENT_ID(数値セル) / Excel row10 | 1.0 | 1.0 | OK |
| `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest/testNormalEndExistAllFields.yaml` | 7 | SETUP_TABLE[1] PROJECT_INS_REQ_ID=1 SALES / Excel row10 | 10000 | 10000 | OK |
| `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest/testNormalEndExistAllFields.yaml` | 7 | EXPECTED_TABLE[1] UPDATE_DATE / Excel row35 | ${systemTime} | ${systemTime} | OK |
| `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest/testNormalEndExistAllFields.yaml` | 7 | RESPONSE_BODY_MESSAGES[case1] JSON / Excel row27 | {"statusCode":"201"} | {"statusCode":"201"} | OK |
| `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest/testNormalEndExistAllFields.yaml` | 7 | EXPECTED_REQUEST_BODY_MESSAGES[case1] JSON(改行入りセル) / Excel row54 | {"projectName":"プロジェクト００１","projectType":"developm…（全文一致） | {"projectName":"プロジェクト００１","projectType":"developm…（全文一致） | OK |
| `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest/testNormalEndOnlyRequireFields.yaml` | 5 | testShots[no=1].description / Excel row4 | メッセージ送信成功(必須フィールドのみ) | メッセージ送信成功(必須フィールドのみ) | OK |
| `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest/testNormalEndOnlyRequireFields.yaml` | 5 | SETUP_TABLE[1] PROJECT_INS_REQ_ID=1 PROJECT_START_DATE(null) / Excel row10 | null | null | OK |
| `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest/testNormalEndOnlyRequireFields.yaml` | 5 | SETUP_TABLE[1] PROJECT_INS_REQ_ID=1 SALES(null) / Excel row10 | null | null | OK |
| `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest/testNormalEndOnlyRequireFields.yaml` | 5 | EXPECTED_REQUEST_HEADER_MESSAGES[case1] 再送要求フラグ / Excel row46 | 0 | 0 | OK |
| `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest/testNormalEndOnlyRequireFields.yaml` | 5 | EXPECTED_REQUEST_BODY_MESSAGES[case1] JSON(改行入りセル) / Excel row54 | {"projectName":"プロジェクト００１","projectType":"developm…（全文一致） | {"projectName":"プロジェクト００１","projectType":"developm…（全文一致） | OK |
| `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest/testAbNormalEnd.yaml` | 7 | testShots[no=2].description / Excel row5 | メッセージ送受信エラーが発生する場合 | メッセージ送受信エラーが発生する場合 | OK |
| `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest/testAbNormalEnd.yaml` | 7 | testShots[no=2].expectedMessageByClient / Excel row5 | case2 | case2 | OK |
| `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest/testAbNormalEnd.yaml` | 7 | LIST_MAP=expectedLog1 message1 / Excel row54 | メッセージの送信に失敗しました。 | メッセージの送信に失敗しました。 | OK |
| `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest/testAbNormalEnd.yaml` | 7 | EXPECTED_TABLE[1] STATUS / Excel row50 | 2 | 2 | OK |
| `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest/testAbNormalEnd.yaml` | 7 | RESPONSE_BODY_MESSAGES[case1] JSON / Excel row27 | errorMode:timeout | errorMode:timeout | OK |
| `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest/testAbNormalEnd.yaml` | 7 | RESPONSE_BODY_MESSAGES[case2] JSON / Excel row44 | errorMode:msgException | errorMode:msgException | OK |
| `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest/testAbNormalEnd.yaml` | 7 | EXPECTED_REQUEST_BODY_MESSAGES[case2] JSON(改行入りセル) / Excel row100 | {"projectName":"プロジェクト００１","projectType":"developm…（全文一致） | {"projectName":"プロジェクト００１","projectType":"developm…（全文一致） | OK |
| `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest/setUpDb.yaml` | 0（元データ0件のため全件=データブロック有無を確認） | 全行(2行・コメントのみ) / Excel row1,2 | データブロックなし | 空(0B) | OK |
（差異なし。全件の生値は `checks/task-3-sampling.tsv`）

## .xls/.xlsx 併存チェック（該当時のみ）

- 併存の有無: あり（`ProjectSaveMessageActionRequestTest.xls` 49664B / `ProjectSaveMessageActionRequestTest.xlsx` 26965B。いずれも develop に存在）。NTF の `PoiXlsReader` は `.xls` を優先解決するため `.xlsx` はシャドウされた未使用ファイル。converter は同名併存を "same-name Excel books coexist" で拒否する
- 差分確認結果の保存先: `.rn/ntf-yaml-support/xls-xlsx-comparison/`（`from-xls/`・`from-xlsx/` に POMなし一時ディレクトリで個別変換した YAML、`diff-result.txt` に `diff -r` 結果と md5）。**4ファイルともバイト一致（差分なし）**＝`.xlsx` は `.xls` と内容が同一の重複
- 未使用側（`.xlsx`）の削除: 変換前に削除済み（`git rm`）→ ユーザーへ報告・判断待ち（過去実施時の確定方針「①変換前に削除」と同じ扱い。全 task 完了後のまとめ報告で確認を仰ぐ）

## QA Expert Review

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Meaningful tests/verification | - | - |
| Edge case coverage | - | - |

## Expert Reviews (code changes only)

N/A — no code changes in this task.

## Overall Verdict

- Self-check: OK
- QA: -
- Language expert: N/A
- Software-engineering expert: N/A
- Ready for user review: -
