# Goal

NTF（Nablarch Testing Framework）のAI対応として、`nablarch-example-http-messaging-send` の既存のExcelテストデータをYAML形式に移行する。
`nablarch-testing-converter` を使ってExcelテストデータをYAMLに変換し、`nablarch-testing-yaml` を用いた設定変更のみで全テストがパスすることを確認する。
参照PR: https://github.com/Fintan-contents/nablarch-system-development-guide/pull/211

# Acceptance criteria

- `develop` ブランチから作成した `ntf-yaml-support` ブランチで全作業が行われている
- 作業前に既存の全テストがパスすることを確認済みである
- `pom.xml` に `nablarch-testing-yaml:1.0.0-SNAPSHOT` と `nablarch-testing-converter:1.0.0-SNAPSHOT` の依存関係が追加されている（スコープ: test）
- `src/test/resources/unit-test.xml` に `YamlTestDataParser` コンポーネントと `yamlInterpreters` リストが追加されている
- 変換対象の全てのテスト用ExcelファイルがそれぞれYAMLファイルに変換されている（サンプリングでExcelとYAMLの内容が一致することを確認済み）
- 変換後、変換対象だったExcelファイルが全て削除されている
- YAMLテストデータを使った状態で全テストがパスしている
- テストクラス本体（`.java`）の変更はなく、設定ファイルと依存関係・テストデータの変更のみで移行が完結している

# Assumptions

- `nablarch-testing-yaml:1.0.0-SNAPSHOT` と `nablarch-testing-converter:1.0.0-SNAPSHOT` はローカルMavenリポジトリ（`~/.m2`）に存在する
- テスト実行にはH2インメモリDBを使用し、`generate-resources` フェーズでDBセットアップとエンティティ生成が行われる
- YAMLファイルの出力先は `src/test/java` 配下（Excelと同じ場所）とし、`nablarch.test.resource-root` の設定変更は不要
- 変換ツール（`nablarch-testing-converter`）の実行手順は `/home/k10949/workspace/nablarch-testing-converter/README.md` に従う

# Environment / Build & Test

- JDK 17（Temurin 17.0.20）、Maven 3.9.16、H2 組み込み（別途DBサーバ不要）
- 本プロジェクトには `gsp` という専用プロファイルは存在しない。`gsp-dba-maven-plugin` の実行（generate-ddl / execute-ddl / load-data）は `generate-resources` フェーズに無条件バインドされているため、`mvn test`（`generate-resources` を内包）だけでDBセットアップ〜テストまで一括実行できる。
- **ビルド・テストコマンド**: `mvn clean test`
  - エンティティ生成のみ個別実行する場合: `mvn clean generate-resources`
  - 依存解決確認: `mvn dependency:resolve`
- **ロケール**: NTFのメッセージ解決のため `LANG=ja_JP.UTF-8`（および `LC_ALL=ja_JP.UTF-8`）必須。`C.UTF-8` だとメッセージ解決に失敗しテストが落ちる。
- README（`/home/k10949/workspace/nablarch-example-http-messaging-send/README.md`）では `mvn clean package`（generate-resources を内包）/ `mvn generate-resources` を案内。テストは上記 `mvn clean test` を使用する。

# Rules

- commit every change; one completion marker per task
- テストクラス（`.java`）は変更しない
- `develop` から新規作成した `ntf-yaml-support` ブランチで作業する
- steering.md は各タスクで更新し、当該タスクのコミットに含める
- テストはExcelファイルが存在しない状態で最終パスを確認する
- YAML変換後はサンプリングでExcelとYAMLの内容を比較してから削除する
- サンプリング比較で差異が見つかった場合は修正せずユーザーに報告して停止する
- QA / language / software-engineering の各レビューは Agent（`subagent_type: general-purpose` / `model: Opus 4.8`）でエキスパートペルソナを付与して実施する。software-engineering レビューの重複指摘はMD記載不要。

# 対象Excelテストデータ

本プロジェクトのテストクラスは1件のみ：
- `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest.java`（`@BatchRequestTest`、テスト3件）

同クラスのExcelテストデータが2ファイル存在する（いずれも `first commit` から追跡されている）：
- `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest.xls`（49664 bytes）
- `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest.xlsx`（26965 bytes）

**重要な調査結果**: NTF の `PoiXlsReader`（`nablarch-testing` `PoiXlsReader.java:62-64` / `264-266`）はテストデータ解決時に `.xls` を先に探し、存在しない場合のみ `.xlsx` にフォールバックする。両方存在する現状では **`.xls` のみが読み込まれ、`.xlsx` はシャドウされた未使用ファイル**である（ベースライン `mvn clean test` で Tests run: 3 全パスは `.xls` 由来）。
→ 同名で出力YAMLが衝突するため、2ファイルをそのまま変換するとYAML出力パスが競合する。`.xlsx` の扱いはユーザー判断事項（Decisions 参照）。

# Scripts

（必要になった場合に `.rn/ntf-yaml-support/scripts/` 配下へ格納し、用途をここと該当 task-N.md に記載する。現時点で作成したスクリプトはない。XLS/XLSX の変換・比較は `nablarch-testing-converter:convert` と `diff`/`md5sum` のアドホック実行で行った。）

# Evidence

- `.rn/ntf-yaml-support/xls-xlsx-comparison/from-xls/`・`from-xlsx/`: Task #3 の調査で `.xls`・`.xlsx` をそれぞれ単独変換したYAML（両者バイト一致）。`.xlsx` が内容重複であることの根拠。

# Tasks

### #1: 現状のビルド・テストで全PASSを確認する

**Purpose**: `develop` から `ntf-yaml-support` ブランチを作成し、変更前の状態で全テストがパスすることを確認する。

**Prerequisites**: none

**Steps**:

- [x] `develop` ブランチから `ntf-yaml-support` ブランチを新規作成する
- [x] README を確認し、ビルド・テストの実行手順を把握する（本プロジェクトは `gsp` プロファイル無し、`generate-resources` に gsp 実行がバインド。`mvn clean test` で一括実行可）
- [x] 隣接プロジェクトの `.rn/` を参照し steering.md の初版を作成する（ビルド・テスト手順を明記）
- [x] `mvn clean test` でエンティティ生成〜テストを実行し全パスを確認する
- [x] 結果を `checks/task-1.md` に記録する（self-check列）
- [x] 変更ファイル（check ファイルおよび steering.md）をコミットする
- [x] self-check
- [x] QA expert review (Agent: general-purpose / Opus 4.8)
- [x] user review（2026-10-02 承認）

**Completion criteria**:

- `ntf-yaml-support` ブランチが `develop` から作成されている
- `mvn clean test` が全テストパスで終了している（BUILD SUCCESS）

### #2: 設定変更 — pom.xml と unit-test.xml にYAML対応を追加

**Purpose**: `pom.xml` に `nablarch-testing-yaml` と `nablarch-testing-converter` の2つのtest依存関係を追加し、`unit-test.xml` に `yamlInterpreters` リストと `YamlTestDataParser` コンポーネントの設定を追加する。設定内容は隣接プロジェクト（nablarch-example-web / nablarch-example-batch）を参考にする。

**Prerequisites**: #1

**Steps**:

- [x] `pom.xml` に `nablarch-testing-yaml:1.0.0-SNAPSHOT`（test scope）を追加する
- [x] `pom.xml` の `<build><plugins>` に `nablarch-testing-converter:1.0.0-SNAPSHOT` をビルドプラグイン（plugin直下 configuration に変換パラメータを設定。CLIで convert ゴールを実行）として追加する
- [x] `unit-test.xml` に `yamlInterpreters` リストと `YamlTestDataParser` コンポーネントを追加する（batch方式）
- [x] `mvn validate` / `mvn dependency:resolve` / `mvn help:describe`（converter）で解決確認
- [x] 変更したファイルをコミットする（713f56a）
- [x] self-check
- [x] QA expert review (Agent: general-purpose / Opus 4.8) — OK
- [x] language expert review (Agent: general-purpose / Opus 4.8) — OK
- [x] software-engineering expert review (Agent: general-purpose / Opus 4.8) — OK（前回NG解消）
- [x] user review（2026-10-02 承認）

**Completion criteria**:

- `pom.xml` に `nablarch-testing-yaml:1.0.0-SNAPSHOT` が test スコープで追加されている
- `pom.xml` の `<build><plugins>` に `nablarch-testing-converter:1.0.0-SNAPSHOT` がビルドプラグイン（plugin直下 configuration に変換パラメータを設定。CLIで convert ゴールを実行）として追加されている
- `unit-test.xml` に `yamlInterpreters` リストと `testDataParser` コンポーネント（`YamlTestDataParser`）が追加されている
- `mvn dependency:resolve` 成功、converter プラグインの `convert` ゴールが `mvn help:describe` で解決できる

### #3: ExcelテストデータをYAMLに変換

**Purpose**: `nablarch-testing-converter` を使って Excel のテストデータをYAML形式に変換し、テストクラスと同じディレクトリに配置して、変換内容をサンプリングで確認する。

**Prerequisites**: #2、および `.xlsx` の扱いの決定（Decisions）→ ① 変換前に削除で確定

**Steps**:

- [x] `.xls`/`.xlsx` を個別にYAML変換して内容比較（`.rn/.../xls-xlsx-comparison/` に配置、バイト一致を確認）
- [x] 未使用の `.xlsx` を削除する（converter が同名併存を拒否するため変換前に必須）
- [x] 変換対象（`ProjectSaveMessageActionRequestTest.xls`）を `mvn ...:convert` でYAML変換する（rc=0）
- [x] 変換後、ExcelとYAMLの内容をサンプリングで比較し一致を確認する（各YAML 3件以上。setUpDbは空）
- [x] サンプリング比較結果を `checks/task-3.md` に記録する
- [x] 変換したYAMLファイルと `.xlsx` 削除をコミットする（`.xls` 本体はまだ削除しない）（91f32ec）
- [x] self-check
- [x] QA expert review (Agent: general-purpose / Opus 4.8) — OK
- [x] user review（2026-10-02 承認）

**Completion criteria**:

- 変換対象のExcelに対応するYAMLファイルが生成されている
- サンプリング比較でExcelとYAMLの内容が一致している（差異があれば報告して停止）
- 変換後のYAMLファイル（および未使用`.xlsx`の削除）がコミットされている

### #4: Excelを削除する

**Purpose**: 変換対象だった `.xls` を削除してコミットする。

**Prerequisites**: #3

**Steps**:

- [x] 変換対象となった `.xls`（`ProjectSaveMessageActionRequestTest.xls`）を削除する（`src` 配下の Excel 残存 0 件）
- [x] 削除結果を `checks/task-4.md` に記録する（テスト実行結果は Task #5 で記載）
- [x] Excelファイル削除をコミットする（140ae7f）
- [x] self-check
- [x] QA expert review (Agent: general-purpose / Opus 4.8) — OK
- [x] user review（2026-10-02 承認）

**Completion criteria**:

- 変換対象だった Excel ファイルが削除されている
- 削除がコミットされている

> Task #5 で Excelなし `mvn clean test` を実施する際、JSON電文のYAMLスキーマ非互換（Decisions 参照）により BUILD FAILURE となる見込み。その検証・判断は Task #5 で行う。

### #5: YAMLテストデータで全テストをパスさせる

**Purpose**: Excelなしで全テストがパスすることを確認する。

**Prerequisites**: #4

**Status**: ⛔ BLOCKED（JSON電文のYAMLスキーマ非互換で BUILD FAILURE。修正せずユーザー報告。詳細 `checks/task-5.md`・Decisions）

**Steps**:

- [x] `mvn clean test` を実行 → BUILD FAILURE（Tests run: 3, Errors: 3、YamlSchemaValidationException）
- [x] テストログで YamlTestDataParser が実際に使われていることを確認する（override ログで確認）
- [x] self-check — NG（BUILD SUCCESS 未達）
- [ ] QA expert review（保留。ブロッカー解消後）
- [ ] language expert review（保留）
- [ ] software-engineering expert review（保留）
- [ ] user review（ブロッカー判断待ち）

**Completion criteria**:

- `mvn clean test` が BUILD SUCCESS で終了する（全テストパス、Excel ファイルなし）→ **未達**
- テストログで YamlTestDataParser が実際に使われていることが確認できる → OK

# Decisions

- **[確定 2026-10-02] 同名の `.xls` / `.xlsx` の扱い（①）**: `.xls` を正データとしてYAML変換し、未使用の `.xlsx` は**変換前に削除**する。根拠: (1) `.xls`/`.xlsx` から独立変換したYAMLがバイト単位で完全一致（`.xlsx` は内容重複、情報損失なし）、(2) converter は同名の `.xls`/`.xlsx` 併存を "same-name Excel books coexist" エラーで拒否するため変換前の削除が必須。`.xlsx` 削除は Task #3 で実施（当初想定の Task #4 から前倒し）。比較エビデンスは `.rn/ntf-yaml-support/xls-xlsx-comparison/` に保存。
- **[ブロッカー確定 2026-10-02、Task #5 で顕在化] JSONフォーマット電文のYAMLスキーマ非互換**: 本プロジェクトのテストデータは JSON 電文（`file-type: JSON`、フィールド `length: "JSON"`）を含む。nablarch-testing-yaml のスキーマは `fields[].length` を数値/`-` に限定し JSON 電文を未サポートで、ランタイム（`YamlMessageBuilder`/`MessageContent`）も電文を固定長としてのみ構築する。一方 Excel/NTF（`BasicTestDataParser`→`MessagePool`）はスキーマ検証なし＋JSONは file-type により本文を文字列全体で比較（`MessagePool.java` の `else` 分岐）するため `length="JSON"` を規約として許容していた。よって `YamlTestDataParser` では全3テストが `YamlSchemaValidationException` で失敗する見込み。これは nablarch-testing-yaml（主）＋ converter（従）の JSON電文対応が必要で、example 側では解消不可。**検証と対応判断は Task #5 で実施**（Task #4 は削除のみ）。該当: 生成YAML `response_body_messages`/`expected_request_body_messages` の `length: "JSON"`（testNormalEndExistAllFields.yaml:65,102 / testNormalEndOnlyRequireFields.yaml:65,102 / testAbNormalEnd.yaml:95,106,157,171）。
- **[確定 2026-10-02] nablarch-testing-converter の宣言方式**: ビルドプラグイン（`<build><plugins>`、`convert` ゴール設定付き）とする。test依存にはしない。理由: converter は Maven プラグインでテスト実行時には不要、XLS→YAML 変換時のみ使用。test依存だと convert ゴール短縮形が使えず、POI/snakeyaml 等の推移依存がテストクラスパスに混入するリスク（language/SW 両レビュー指摘）。web/batch テンプレートに準拠。指示書 V1.1 の該当記載も「test依存→ビルドプラグイン」に修正済み。

# State

- **Status**: 🔁 再検証中（修正適用後。developベースラインからTask毎に再実施）
- **Date**: 2026-10-13
- **Last completed**: 再検証 STEP 0（資材をdevelopへ戻す, b4358f0）→ STEP 1（Excelベースライン全パス, Tests run: 3）→ STEP 2（YAML設定再適用, 891e406）→ STEP 3（修正版converterで変換、誤変換なし・確定版とバイト一致、`.xlsx`削除）。
- **Next**: STEP 4（`.xls`削除）→ STEP 5（Excelなしで `mvn clean test`、旧BLOCKED解消＝BUILD SUCCESS を確認）。
- **Notes**: 旧Task#5のBLOCKED（「JSON電文未サポート」）は誤認。真因は (1) converterの名前行誤認（nablarch-testing-converter 修正済み）, (2) YamlTestDataParser を起動設定(diConfig)に未配置（修正済み）。本再検証はその改善確認。report `task-5_json-yaml-incompatibility.md` の根本原因記述は旧認識のままで要更新。
