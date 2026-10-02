# 報告資料: NTF YAML移行における JSONフォーマット電文の非互換（nablarch-example-http-messaging-send）

- 作成日: 2026-10-02
- 対象ブランチ: `ntf-yaml-support`（`nablarch-example-http-messaging-send`、コミット `4ddd360`）
- 事象発生タスク: Task #5（Excelなしで `mvn clean test` を実行し全テストパスを確認する工程）

## 1. サマリ

ExcelテストデータをYAMLへ移行し `YamlTestDataParser` でテスト実行したところ、**JSONフォーマット電文**を含むテストデータ3件すべてが `YamlSchemaValidationException` で失敗した（`mvn clean test` → `Tests run: 3, Failures: 0, Errors: 3`、BUILD FAILURE）。Excel版（`BasicTestDataParser`）では同じデータで全パスしていた。

本件は **nablarch-testing-yaml が JSONフォーマット電文のテストデータを未サポート**であることに起因するフレームワーク側の非互換であり、example リポジトリ（設定・テストデータ変換のみ、テストクラス不変）の範囲では解消できない。

## 2. 事象（症状）

- コマンド: `LANG=ja_JP.UTF-8 mvn clean test`（Excelファイルは全削除済み、YAML配置済み、`unit-test.xml` で `testDataParser` を `YamlTestDataParser` に設定済み）
- 結果: `Tests run: 3, Failures: 0, Errors: 3, Skipped: 0` → **BUILD FAILURE**
- 例外（3テスト共通）:
  ```
  nablarch.test.core.reader.yaml.YamlSchemaValidationException:
  $.response_body_messages[0].records[0].fields[0].length: string が見つかりました、integer が予期されました
  $.response_body_messages[0].records[0].fields[0].length: 正規表現パターン ^([0-9]+|-)$ に一致しません
  $.expected_request_body_messages[0].records[0].fields[0].length: （同上）
  ```
- `YamlTestDataParser` が使用されていることはログで確認済み（`override component ... component name = testDataParser ... override component definition classname = nablarch.test.core.reader.YamlTestDataParser`）。設定は正しく、失敗はテストデータのロード時スキーマ検証に起因する。

## 3. 直接原因（Direct cause）

JSONフォーマット電文のフィールド定義が `length: "JSON"`（非数値の文字列）を持つが、nablarch-testing-yaml のスキーマは `fields[].length` を **整数** または **`^([0-9]+|-)$` に一致する文字列**に限定しているため、ロード時のJSON Schema検証で不正と判定され例外になる。

- スキーマ定義: `nablarch-testing-yaml` `src/main/resources/nablarch/test/ntf-testdata-yaml-schema.json:512-528`（`length` の `anyOf`: `integer`(minimum:0) または `string` `pattern: "^([0-9]+|-)$"`（:521））
- 検証・送出: `nablarch-testing-yaml` `src/main/java/nablarch/test/core/reader/yaml/YamlLoader.java:169`（`JSON_SCHEMA.validate(jsonNode)`）→ `:171`（`throw new YamlSchemaValidationException(...)`）
- 呼び出し元: `nablarch-testing-yaml` `src/main/java/nablarch/test/core/reader/YamlTestDataParser.java:151-152`（`getListMap` → `YamlLoader.load`）
- 該当データ（本リポジトリ生成YAML、`src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest/`）:
  - `testNormalEndExistAllFields.yaml:65`（`response_body_messages`）, `:102`（`expected_request_body_messages`）
  - `testNormalEndOnlyRequireFields.yaml:65`, `:102`
  - `testAbNormalEnd.yaml:95,106`（`response_body_messages` case1/case2）, `:157,171`（`expected_request_body_messages` case1/case2）
  - いずれも `- {name: "JSON", type: "UTF-8", length: "JSON"}`（直前に `file-type: "JSON"` ディレクティブ）

## 4. 根本原因（Root cause）

**nablarch-testing-yaml に JSONフォーマット電文という概念が実装されていない**（スキーマ・ランタイムの両面）。`length="JSON"` は Excel/NTF における「この1フィールドで JSON 本文全体を表す」という規約値であり、バイト長ではない。しかし YAML 実装は電文を固定長/可変長フラットレコードとしてのみモデル化している。

- スキーマ面: 上記のとおり `length` を数値/`-` に限定。`file-type` の説明も「固定長=Fixed/可変長=Variable」のみで JSON/XML の記述が無い（`ntf-testdata-yaml-schema.json:336` 付近）。
- ランタイム面: 電文本文を固定長ファイルとしてのみ構築する。
  - `nablarch-testing-yaml` `YamlFileBuilder.java:85-87`（`FILE_TYPE_FIXED` 以外は `VariableLengthFile`。JSON の分岐なし）
  - `nablarch-testing-yaml` `MessageContent.java:19`（`private final FixedLengthFile body;`）
  - `nablarch-testing-yaml` `YamlMessageBuilder.java:125-126`（`new FixedLengthFile(id)` で本文を構築）
- converter は値を素通ししているだけ（原因ではなく追従側）:
  - `nablarch-testing-converter` `xls/XlsFormatReader.java:419-420`（Excelの length セルを文字列として読み `FieldDef` を生成）
  - `nablarch-testing-converter` `yaml/YamlFormatWriter.java:401-402`（`length` が null でなければそのまま出力）
  - `nablarch-testing-converter` `model/FieldDef.java:53`（Javadoc: 「`XlsFormatWriter`／`YamlFormatWriter` に `length` の番人は無い」＝値の妥当性検査をしない設計）

→ 根本解決には **nablarch-testing-yaml（主）** が JSON電文をスキーマ・ランタイム両面でサポートし、**nablarch-testing-converter（従）** がその表現に追従する必要がある。

## 5. Excel と YAML の現状動作の違い

| 観点 | Excel（従来・全パス） | YAML（今回・全エラー） |
|---|---|---|
| テストデータ解析 | `BasicTestDataParser`（`nablarch-testing`） | `YamlTestDataParser`（`nablarch-testing-yaml`、`BasicTestDataParser` を継承） |
| ロード時のスキーマ検証 | **なし** | **あり**（`YamlLoader.java:169` でJSON Schema検証）→ ここで失敗 |
| `length="JSON"` の扱い | 規約値として許容（バイト長に未使用） | スキーマ `^([0-9]+|-)$` 違反で不正 |
| JSON電文の比較方式 | file-type が `Fixed` 以外のとき **本文全体を文字列として比較**（`MessagePool.java:162` の判定で `else` 分岐 `:170-182`）。`convertByFileType`（`:243-244` → `source.convertData`）が file-type に応じ変換 | ロード時点で失敗し到達しない。かつランタイムは電文を固定長としてのみ構築（JSON規約の相当処理なし） |
| 電文本文のモデル | `FixedLengthDataRecordFormatter`（`MessagePool.java:36`）だが JSON は文字列全体比較で回避 | `FixedLengthFile` 固定（`MessageContent.java:19` 他） |

補足: Excel で `.xls` が優先解決されること自体は `nablarch-testing` `PoiXlsReader.java:62-64` によるが、本件の本質は上記の「スキーマ検証の有無」と「JSON電文のモデル化の有無」の差である。

## 6. 該当箇所一覧（リポジトリ / ファイル / クラス・メソッド / 行 / コミット）

| 区分 | リポジトリ (HEAD) | ファイル | クラス/メソッド | 行 |
|---|---|---|---|---|
| 直接原因（スキーマ制約） | nablarch-testing-yaml (`d09566e`) | `src/main/resources/nablarch/test/ntf-testdata-yaml-schema.json` | `$defs...length`（anyOf: integer / string pattern） | 512-528（pattern :521） |
| 直接原因（検証・送出） | nablarch-testing-yaml (`d09566e`) | `src/main/java/nablarch/test/core/reader/yaml/YamlLoader.java` | `YamlLoader#load`（validate→throw） | 169, 171 |
| 失敗の呼び出し元 | nablarch-testing-yaml (`d09566e`) | `src/main/java/nablarch/test/core/reader/YamlTestDataParser.java` | `YamlTestDataParser#getListMap` | 151-152 |
| 根本原因（ランタイム: 固定長のみ） | nablarch-testing-yaml (`d09566e`) | `.../yaml/YamlFileBuilder.java` | `YamlFileBuilder`（Fixed/Variable分岐） | 85-87 |
| 根本原因（ランタイム: 本文=固定長） | nablarch-testing-yaml (`d09566e`) | `.../yaml/MessageContent.java` | `MessageContent#body` | 19 |
| 根本原因（ランタイム: 本文=固定長） | nablarch-testing-yaml (`d09566e`) | `.../yaml/YamlMessageBuilder.java` | `YamlMessageBuilder`（`new FixedLengthFile`） | 125-126 |
| Excel動作（検証なし・継承元） | nablarch-testing (`d309471`) | `src/main/java/nablarch/test/core/reader/BasicTestDataParser.java` | `BasicTestDataParser`（スキーマ検証なし） | － |
| Excel動作（JSONは文字列比較） | nablarch-testing (`d309471`) | `src/main/java/nablarch/test/core/messaging/MessagePool.java` | `Comparator#compareBody` 判定/else、`convertByFileType`、`getFileTypeFromDirective` | 160-182, 243-244, 192 |
| converter（length素通し: 読取） | nablarch-testing-converter (`4a59436`) | `src/main/java/nablarch/test/tool/converter/xls/XlsFormatReader.java` | `XlsFormatReader`（length セル→FieldDef） | 419-420 |
| converter（length素通し: 出力） | nablarch-testing-converter (`4a59436`) | `src/main/java/nablarch/test/tool/converter/yaml/YamlFormatWriter.java` | `YamlFormatWriter`（length出力） | 401-402 |
| converter（lengthの番人なし） | nablarch-testing-converter (`4a59436`) | `src/main/java/nablarch/test/tool/converter/model/FieldDef.java` | `FieldDef`（Javadoc 設計注記） | 53 |
| 症状データ | nablarch-example-http-messaging-send (`4ddd360`) | `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest/*.yaml` | `length: "JSON"` 行 | testNormalEndExistAllFields.yaml:65,102 / testNormalEndOnlyRequireFields.yaml:65,102 / testAbNormalEnd.yaml:95,106,157,171 |
| 対象テスト | nablarch-example-http-messaging-send (`4ddd360`) | `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest.java` | `@Test` 3件（`support.execute(...)`） | 21-41 |

## 7. 対応案（提案）

### 案A（推奨・根本解決）: nablarch-testing-yaml に JSONフォーマット電文サポートを追加
- スキーマ: `file-type: JSON`（必要なら XML も）を認識し、JSON電文の `fields[].length` に対する数値制約を免除（または JSON電文専用の表現を定義）。
- ランタイム: `YamlMessageBuilder` / `MessageContent` / `YamlFileBuilder` に、Excel/NTF の `MessagePool` と等価な「file-type が Fixed 以外のとき本文を文字列全体として扱う」挙動を実装。
- converter: 合意した JSON電文表現に追従（必要なら `length` を省略して出力等）。
- 長所: 本来の移行ゴールを達成でき、JSON/XML電文を含む他のメッセージング系PJも救済される。
- 短所: フレームワーク3リポジトリにまたがる改修で工数が大きい。表現仕様の合意が前提。

### 案B（framework小規模対応）: スキーマの `length` 制約のみ緩和
- `fields[].length` を JSON file-type のとき非数値許容にする（または任意文字列許容）。
- 長所: 変更が小さい。短所: ランタイムは依然 `FixedLengthFile` で構築するため、ロードは通っても **電文比較が正しく動く保証がない**（要検証）。案Aのランタイム対応とセットでないと不完全な可能性が高い。

### 案C（converter側対応）: schema-valid な JSON電文表現を converter が出力
- JSON電文では `length` を出力しない等、スキーマ・ランタイムが受理できる表現に変換。
- 長所: example 側の再変換で対応できる可能性。短所: 受理可能な表現を framework 側が定義していることが前提（案A/Bと連動）。単独では成立しない。

### 案D（暫定・現実解）: 本プロジェクトは当面 Excel を継続（YAML移行対象外）
- JSON電文を含むメッセージング系PJは、framework の JSON対応が入るまで Excel テストデータを維持する。
- 長所: 既存テストの品質を維持。短所: 当該PJのみ「AI対応（YAML化）」ゴールは未達。
- 実務: 本ブランチ `ntf-yaml-support` はマージせず保留（またはクローズ）し、本資料を framework チームへの要望根拠とする。

### 案E（非推奨・テストデータ側回避）
- JSON本文を固定長1フィールドとして `length` に実バイト数を記載する等でスキーマを通す。
- 非推奨理由: 元データの意味（JSON電文であること）が変わる、多バイト文字でバイト長計算が不安定、保守性低下。移行の目的（忠実な移行）に反する。

**推奨: 案A（根本解決）を framework チームへ要望。短期は案D（本PJは Excel 継続・ブランチ保留）で品質を維持。** 案B/Cは案Aの一部として実施されるべきで、単独採用は非推奨。

## 8. 再現手順

```
cd /home/k10949/workspace/nablarch-example-http-messaging-send
git checkout ntf-yaml-support   # 4ddd360
LANG=ja_JP.UTF-8 mvn clean test  # → BUILD FAILURE, Errors: 3, YamlSchemaValidationException
```

比較用に、Excel版（develop）では `LANG=ja_JP.UTF-8 mvn clean test` が BUILD SUCCESS（Tests run: 3）となる（Task #1 で確認済み）。
