# task-5 Completion Check

> **報告用資料**: 詳細（直接原因・根本原因・Excel/YAML動作差・該当リポジトリ/クラス/メソッド/行・対応案）は `.rn/ntf-yaml-support/reports/task-5_json-yaml-incompatibility.md` を参照。

## Status: BLOCKED（YAMLスキーマ非互換により BUILD SUCCESS 未達。修正せずユーザー報告）

Excelなしの状態で `mvn clean test`（LANG=ja_JP.UTF-8）を実行した結果、**JSONフォーマット電文のYAMLスキーマ非互換**により全3テストが失敗した。ルールに従い**修正せずユーザーに報告・停止**する。

## 実行結果

- `mvn clean test`: `Tests run: 3, Failures: 0, Errors: 3, Skipped: 0` → **BUILD FAILURE**
- 例外: `nablarch.test.core.reader.yaml.YamlSchemaValidationException`（`YamlTestDataParser.getListMap:152` / `YamlLoader.load:171`）
- 検証エラー（3テスト共通、`length: "JSON"` がスキーマ `^([0-9]+|-)$` に不一致）:
  - `$.response_body_messages[0].records[0].fields[0].length: string が見つかりました、integer が予期されました`
  - `$.expected_request_body_messages[0].records[0].fields[0].length: 正規表現パターン ^([0-9]+|-)$ に一致しません`

## Completion Criteria

| Criterion | Self-check | Evidence | QA | QA Evidence |
|---|---|---|---|---|
| mvn clean test が BUILD SUCCESS（全テストパス、Excelなし） | NG | `Tests run: 3, Errors: 3` / BUILD FAILURE。YamlSchemaValidationException（JSON電文の `length:"JSON"`） | | |
| テストログで YamlTestDataParser が使われている | OK | ログに `override component ... component name = testDataParser ... override component definition classname = nablarch.test.core.reader.YamlTestDataParser` と `YamlTestDataParser does not use TestDataReader; the injected value is ignored.` を確認 | | |

## 根本原因（Decisions 参照）

本プロジェクトのテストデータは **JSONフォーマット電文**（`directives.file-type: JSON`、フィールド `- {name: "JSON", type: "UTF-8", length: "JSON"}`）を含む。

- **Excel/NTF**（`BasicTestDataParser`→`MessagePool`）: JSON Schema 検証なし。file-type が `Fixed` 以外（＝JSON）のときは本文を文字列全体で比較（`MessagePool.java` の `else` 分岐）するため、`length="JSON"` は実バイト長として使われず規約として許容されていた。→ ベースライン全パス。
- **YAML/nablarch-testing-yaml**（`YamlTestDataParser`）: `YamlLoader.load()` がロード時に JSON Schema 検証を実行。スキーマ `ntf-testdata-yaml-schema.json` の `fields[].length` は `integer`／`^([0-9]+|-)$` 限定で **JSON電文を未サポート**。さらにランタイム（`YamlMessageBuilder`/`MessageContent`）も電文を固定長としてのみ構築。→ ロード時点で失敗。

→ **nablarch-testing-yaml（主）＋ converter（従）の JSON電文対応が必要**であり、本リポジトリ（example。設定・データ変換のみ、テストクラス不変）の範囲では解消できない。

該当YAML（`length: "JSON"`）:
- `ProjectSaveMessageActionRequestTest/testNormalEndExistAllFields.yaml`:65,102
- `同/testNormalEndOnlyRequireFields.yaml`:65,102
- `同/testAbNormalEnd.yaml`:95,106,157,171

## 対応方針（ユーザー判断待ち）

修正せず停止。想定選択肢:
1. フレームワーク未サポートとして本プロジェクトの移行を中断し、nablarch-testing-yaml メンテナに JSON電文対応（スキーマの `length` 制約緩和＋`YamlMessageBuilder`/converter の JSON電文表現）を要望する。
2. nablarch-testing-yaml の JSON電文対応版が別途あれば `~/.m2` に入れて再試行する（現 `feature/ntf-yaml` には形跡なし）。
3. converter 側で schema-valid な JSON電文表現にすべきか framework/converter チームへ確認する。

## Overall Verdict

- Self-check: NG（BUILD SUCCESS 未達。JSON電文のYAMLスキーマ非互換）
- QA / Language / Software-engineering: 保留（ブロッカー解消後に実施）
- Ready for user review: Yes（ブロッカーのユーザー判断を仰ぐ）

## 再検証（2回目: 修正適用後に BLOCKED 解消）

旧BLOCKEDは「JSON電文未サポート」という**誤認**であり、真因は2点だった:
(1) nablarch-testing-converter の名前行誤認（単一フィールド電文でディレクティブ行を名前行と誤認）→ converter 側で修正済み。
(2) `YamlTestDataParser` をアクション実行時の diConfig(`http-messaging-send-boot.xml`)に未配置 → 起動設定へ移設して修正済み。

修正を適用し、developベースラインから再変換・Excel削除のうえ Excelなしで実行:

| Criterion | Self-check | Evidence |
|---|---|---|
| mvn clean test が BUILD SUCCESS（Excelなし） | OK | `Tests run: 3, Failures: 0, Errors: 0` / BUILD SUCCESS |
| YamlTestDataParser が使用されている | OK | override ログが2回（テスト自身のリポジトリ＝unit-test.xml 経由、アクション実行時リポジトリ＝boot.xml 経由）。原因2の修正が有効 |
| JSON電文のスキーマ検証 | OK | 誤変換解消済みYAML（`length:"-"`）でロード時 `YamlSchemaValidationException` が発生しない |

- 再検証 Overall: OK（旧BLOCKED解消。Excelなしで全テストパス）
