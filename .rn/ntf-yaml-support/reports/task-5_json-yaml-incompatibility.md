# 報告資料: NTF YAML移行における JSONフォーマット電文テストの失敗（nablarch-example-http-messaging-send）

- 作成日: 2026-10-02
- 訂正日: 2026-10-19（§0 を追加。§1〜§9 は 2026-10-02 時点の旧認識として残す）
- 対象ブランチ: `ntf-yaml-support`（`nablarch-example-http-messaging-send`、コミット `4ddd360`）
- 事象発生タスク: Task #5（Excelなしで `mvn clean test` を実行し全テストパスを確認する工程）

## 0. 訂正（2026-10-19）— 旧認識「nablarch-testing-yaml が JSON 電文を未サポート」は誤り

**§1〜§9 の根本原因・対応案は誤認であり、採用しない。** 真因は次の 2 点で、どちらも修正済み。framework（nablarch-testing-yaml）の改修は不要。

### 0.1 真因

| # | 真因 | 所在 | 修正 |
|---|---|---|---|
| 1 | **converter が名前行を取り違えていた。** `XlsFormatReader#skipToFirstNameRow` は「先頭セルを除いた残りがフィールド名一覧と一致する最初の行」を名前行としていた。フィールドが `JSON` の 1 つだけの電文では、ディレクティブ行 `file-type \| JSON` の残り `[JSON]` がフィールド名と一致し、これを名前行と誤認。続く `text-encoding \| UTF-8` を型行、`no \| JSON` を長さ行と読んだため、`record_type: "file-type"`／`type: "UTF-8"`／`length: "JSON"` という壊れた YAML が出力された | nablarch-testing-converter | `7a97049`（先頭セルがディレクティブ名の行を名前行の候補から除外。NTF 本体と同じ判断） |
| 2 | **アクション実行時の diConfig に YAML 用パーサが無かった。** リクエスト単体テストでは、アクション実行のたびにテストショットの `diConfig`（`http-messaging-send-boot.xml`）でリポジトリが作り直される。同期送信のモック `RequestTestingMessagingClient` はそのリポジトリから `testDataParser` を引くため、`unit-test.xml` にだけ `YamlTestDataParser` を置いていた状態では Excel 用パーサのまま削除済み `.xls` を探していた | 本リポジトリ（設定） | `70fe87a`（`YamlTestDataParser` と `yamlInterpreters` を `http-messaging-send-boot.xml` へ移設。`unit-test.xml` は boot を import するので両方の経路に効く） |

- §2 のスキーマ検証エラーは、真因 1 で壊れた YAML をスキーマが正しく拒否したもの。スキーマ側に問題は無い。
- §9.1 の実験（`length` を `"-"`／実バイト長に書き換え）が `couldn't find resource` で失敗したのは真因 2 による。スタックトレース（`reports/logs/task-5-experiment-length-dash-failure.log`）は `RequestTestingMessagingClient.sendSync` → `createReceivedMessage` → `RequestTestingSendSyncSupport.getMessages` → `TestSupport.getPathOf` であり、アクション実行中のモックが Excel を探していたことを示す。JSON 電文の扱いとは無関係で、「ランタイムが JSON 未対応」という §9 の結論は実験の前提（真因 2 が残った状態）を取り違えたもの。
- JSON 電文の実行時処理について: Excel 版 NTF も JSON 電文を「`file-type: JSON` のディレクティブを持つ、フィールド 1 つ・長さ `-` の固定長データ」として読み、比較時に file-type が `Fixed` 以外なら本文全体を文字列比較する（nablarch-testing `MessagePool`）。YAML 読み込みはディレクティブをそのまま渡すので、その先は Excel 版と同じ本体コードを通る。YAML 側に JSON 専用の実装は要らない（下の 0.2 で実証）。

### 0.2 修正後の検証（2026-10-13 再検証）

develop ベースラインへ戻し（`b4358f0`）、修正版 converter で設定・変換・削除をやり直した。

| STEP | 内容 | コミット | 結果 |
|---|---|---|---|
| 2 | pom / unit-test.xml / http-messaging-send-boot.xml に YAML 対応設定 | `891e406` | — |
| 3 | 修正版 converter（`7a97049`）で `.xls` → YAML | `a4011c4` | JSON 電文は `record_type: "no"`／`length: "-"`、`directives.file-type: "JSON"` で出力。`length: "JSON"`／`record_type: "file-type"` は 0 件 |
| 4 | 変換元 `.xls` を削除 | `e6f06e6` | `src` 配下の Excel 0 件 |
| 5 | Excel なしで `LANG=ja_JP.UTF-8 mvn clean test` | `e8fcdda` | `Tests run: 3, Failures: 0, Errors: 0` / BUILD SUCCESS。`YamlTestDataParser` の override ログが 2 経路（unit-test.xml 経由・boot 経由）で出力 |

### 0.3 対応案の扱い

- §7 の案A（framework に JSON 電文サポートを追加）・案B・案C・案E は**不要につき取り下げ**。
- 案D（本プロジェクトは Excel 継続）も**取り下げ**。YAML 移行は完了している。
- 移行手順書には「同期送信のモック（`RequestTestingMessagingClient`／`RequestTestingMessagingProvider`）を使う場合は、diConfig の起動用 XML にも `YamlTestDataParser` の上書きが必要」を追記する（nablarch-example-mom-sync-send-batch の事象と同じ）。

### 0.4 教訓

- スキーマ検証エラーは、まず入力（converter の出力）が壊れていないかを疑う。
- 同じ `couldn't find resource` でも、`RequestTestingMessagingClient` 経由ならアクション実行中、つまり diConfig 側の設定の問題。
- 実験は変数を 1 つずつ変え、別のエラーに変わったときは、その原因が同じ軸か確かめてから結論を出す。

---

> **以下 §1〜§9 は 2026-10-02 時点の旧認識（誤り）。経緯の記録として残す。**

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

### 5.0 観点別対比（スキーマ検証 / length:"JSON" / JSON電文の比較）

| 観点 | Excel（従来・全パス） | YAML（今回・全エラー） |
|---|---|---|
| スキーマ検証 | **行わない**。`BasicTestDataParser`（nablarch-testing）はテストデータに対するJSON Schema検証を持たない | **ロード時に行う**。`YamlLoader#load`（`YamlLoader.java:169` `JSON_SCHEMA.validate`）で検証し、不正なら `:171` で `YamlSchemaValidationException` を送出 → ここで失敗 |
| `length: "JSON"` | **許容**（JSON電文を表す規約値。バイト長としては使用しない） | **不正**。スキーマ `fields[].length` は `integer`／`^([0-9]+|-)$` 限定（`ntf-testdata-yaml-schema.json:512-528`、pattern :521）のため非数値 `"JSON"` を拒否 |
| JSON電文の比較 | **本文全体を文字列として比較**。file-type が `Fixed` 以外のとき `MessagePool#compareBody`（nablarch-testing）の `else` 分岐（`MessagePool.java:170-182`、判定 :160-162）で実施。`convertByFileType`（:243-244）が file-type に応じ変換 | **到達不可**。ロード時スキーマ検証で失敗するため比較工程に進めない。かつランタイムは電文を固定長としてのみ構築し（nablarch-testing-yaml の `YamlFileBuilder.java:85-87`／`MessageContent.java:19`／`YamlMessageBuilder.java:125-126`）、JSONを文字列全体として扱う相当処理が無い |

### 5.1 詳細対比

| 観点 | Excel（従来・全パス） | YAML（今回・全エラー） |
|---|---|---|
| テストデータ解析 | `BasicTestDataParser`（`nablarch-testing`） | `YamlTestDataParser`（`nablarch-testing-yaml`、`BasicTestDataParser` を継承） |
| ロード時のスキーマ検証 | **なし** | **あり**（`YamlLoader.java:169` でJSON Schema検証）→ ここで失敗 |
| `length="JSON"` の扱い | 規約値として許容（バイト長に未使用） | スキーマ `^([0-9]+|-)$` 違反で不正 |
| JSON電文の比較方式 | file-type が `Fixed` 以外のとき **本文全体を文字列として比較**（nablarch-testing。`MessagePool.java:162` の判定で `else` 分岐 `:170-182`）。`convertByFileType`（`:243-244` → `source.convertData`）が file-type に応じ変換 | ロード時点で失敗し到達しない。かつランタイムは電文を固定長としてのみ構築（JSON規約の相当処理なし） |
| 電文本文のモデル | `FixedLengthDataRecordFormatter`（nablarch-testing `MessagePool.java:36`）だが JSON は文字列全体比較で回避 | `FixedLengthFile` 固定（nablarch-testing-yaml `MessageContent.java:19` 他） |

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

## 9. 検証（実験）結果と総括

### 9.1 `length` 値を変えた3通りの実験（いずれも一時変更・コミットせず復元済み）

`length: "JSON"` を書き換えて `mvn clean test` を実行し、スキーマ検証とテスト実行の挙動を確認した。

| 実験（`length` の値） | スキーマ検証 | テスト結果 | 失敗の内訳・内容 |
|---|---|---|---|
| `"JSON"`（元の変換結果） | ✗ 失敗 | BUILD FAILURE | `Errors: 3` — ロード時 `YamlSchemaValidationException`（`^([0-9]+|-)$` 違反） |
| `"-"`（オンデマンド長） | ✓ 通過 | BUILD FAILURE | `Failures: 3` — `couldn't find resource [.../testXxx]` → `ComparisonFailure`（status/STATUS 不一致） |
| `<実バイト長の数値>`（20 / 285 / 313 等、JSON本文のUTF-8バイト長） | ✓ 通過 | BUILD FAILURE | `Failures: 3` — `"-"` と**完全に同じ**失敗（`couldn't find resource`） |

**考察**: `length` の値（`"JSON"`／`"-"`／実数値）は本質的な問題ではない。スキーマを通過させても、その先で電文リソース解決に失敗する（`couldn't find resource`）。これは nablarch-testing-yaml のランタイムが電文を固定長としてのみ構築し、JSON電文として処理する仕組みを持たないため。
→ 報告の **案B（スキーマ緩和のみ）・案E（テストデータの数値調整）では解決不可**、**案A（ランタイム＋スキーマで JSON電文を本サポート）が必須**であることが実機で確定。

### 9.2 総括 — ファイル変換 と 実行時処理 の切り分け

| 段階 | Excel 版 | YAML 版 | 差分の所在 |
|---|---|---|---|
| ① ファイル変換（Excel→YAML 書き出し） | （元ファイル） | **可能**。converter が `file-type: JSON` と本文を機械的に出力（YAMLファイルは生成済み） | 差なし（converter は JSON も出力できる） |
| ② 実行時のスキーマ検証 | 行わない（`BasicTestDataParser`、nablarch-testing） | **行う**。`length:"JSON"` を弾く（`YamlLoader.java:169,171`） | YAML のみ検証あり |
| ③ 実行時の電文処理（JSON電文） | **処理できる**。file-type=JSON を本文の文字列全体比較で扱う（nablarch-testing `MessagePool.java:170-182`） | **処理できない**。電文を固定長としてのみ構築（nablarch-testing-yaml `YamlMessageBuilder`/`MessageContent`）し JSON 相当処理なし → `couldn't find resource` | **ここが本質的な差分** |
| ④ テスト結果 | BUILD SUCCESS（Tests run: 3） | BUILD FAILURE（`length` を schema-valid にしても ③ で失敗） | YAML のみ失敗 |

**結論**: 「Excel は変換できて YAML は変換できない」ではなく（①のファイル変換はどちらも可能）、**Excel版 NTF は JSONフォーマット電文のテストデータを“実行”できるが、YAML版（YamlTestDataParser / nablarch-testing-yaml）は JSON電文の実行時処理に未対応で“実行”できない**。差分は③の実行時ランタイムにあり、`length` 値の調整では解消できない（9.1 で実証）。本リポジトリ（example）側では対応不可で、**案A（framework 側の JSON電文サポート）が必要**。
