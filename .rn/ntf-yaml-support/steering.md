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

（必要になった場合に `.rn/ntf-yaml-support/scripts/` 配下へ格納し、用途をここと該当 task-N.md に記載する。現時点で作成したスクリプトはない。）

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
- [ ] user review

**Completion criteria**:

- `ntf-yaml-support` ブランチが `develop` から作成されている
- `mvn clean test` が全テストパスで終了している（BUILD SUCCESS）

### #2: 設定変更 — pom.xml と unit-test.xml にYAML対応を追加

**Purpose**: `pom.xml` に `nablarch-testing-yaml` と `nablarch-testing-converter` の2つのtest依存関係を追加し、`unit-test.xml` に `yamlInterpreters` リストと `YamlTestDataParser` コンポーネントの設定を追加する。設定内容は隣接プロジェクト（nablarch-example-web / nablarch-example-batch）を参考にする。

**Prerequisites**: #1

**Steps**:

- [ ] `pom.xml` に `nablarch-testing-yaml:1.0.0-SNAPSHOT`（test scope）を追加する
- [ ] `pom.xml` に `nablarch-testing-converter:1.0.0-SNAPSHOT`（test scope）を追加する
- [ ] `unit-test.xml` に `yamlInterpreters` リストと `YamlTestDataParser` コンポーネントを追加する（隣接プロジェクトを参考）
- [ ] `mvn dependency:resolve` 等で依存関係が解決できることを確認する
- [ ] 変更したファイルをコミットする
- [ ] self-check
- [ ] QA expert review (Agent: general-purpose / Opus 4.8)
- [ ] language expert review (Agent: general-purpose / Opus 4.8)
- [ ] software-engineering expert review (Agent: general-purpose / Opus 4.8)
- [ ] user review

**Completion criteria**:

- `pom.xml` に `nablarch-testing-yaml:1.0.0-SNAPSHOT` と `nablarch-testing-converter:1.0.0-SNAPSHOT` が test スコープで追加されている
- `unit-test.xml` に `yamlInterpreters` リストと `testDataParser` コンポーネント（`YamlTestDataParser`）が追加されている
- `mvn dependency:resolve -Dclassifier=test` が成功する（依存関係解決エラーなし）

### #3: ExcelテストデータをYAMLに変換

**Purpose**: `nablarch-testing-converter` を使って Excel のテストデータをYAML形式に変換し、テストクラスと同じディレクトリに配置して、変換内容をサンプリングで確認する。

**Prerequisites**: #2、および `.xlsx` の扱いの決定（Decisions）

**Steps**:

- [ ] 変換対象（`ProjectSaveMessageActionRequestTest.xls`）をYAML変換する
- [ ] 変換後、ExcelとYAMLの内容をサンプリングで比較し一致を確認する（最低3件、元データが3件未満なら元データ件数分）
- [ ] サンプリング比較結果を `checks/task-3.md` に記録する（差異があれば原因を調査しユーザーに報告し、修正せずに止める）
- [ ] 変換したYAMLファイルをコミットする（Excelはまだ削除しない）
- [ ] self-check
- [ ] QA expert review (Agent: general-purpose / Opus 4.8)
- [ ] user review

**Completion criteria**:

- 変換対象のExcelに対応するYAMLファイルが生成されている
- サンプリング比較でExcelとYAMLの内容が一致している（差異があれば報告して停止）
- 変換後のYAMLファイルがコミットされている

### #4: Excelを削除する

**Purpose**: 変換対象だった Excel（および未使用の `.xlsx`。扱いは Decisions に従う）を削除してコミットする。

**Prerequisites**: #3

**Steps**:

- [ ] 変換対象となった Excel ファイルを削除する（`.xlsx` の扱いは Decisions の決定に従う）
- [ ] 結果を `checks/task-4.md` に記録する
- [ ] Excelファイル削除をコミットする
- [ ] self-check
- [ ] QA expert review (Agent: general-purpose / Opus 4.8)
- [ ] user review

**Completion criteria**:

- 変換対象だった Excel ファイルが削除されている
- 削除がコミットされている

### #5: YAMLテストデータで全テストをパスさせる

**Purpose**: Excelなしで全テストがパスすることを確認する。

**Prerequisites**: #4

**Steps**:

- [ ] `mvn clean test` が BUILD SUCCESS になることを確認する
- [ ] テストログで YamlTestDataParser が実際に使われていることを確認する
- [ ] self-check
- [ ] QA expert review (Agent: general-purpose / Opus 4.8)
- [ ] language expert review (Agent: general-purpose / Opus 4.8)
- [ ] software-engineering expert review (Agent: general-purpose / Opus 4.8)
- [ ] user review

**Completion criteria**:

- `mvn clean test` が BUILD SUCCESS で終了する（全テストパス、Excel ファイルなし）
- テストログで YamlTestDataParser が実際に使われていることが確認できる

# Decisions

- **[未決] 同名の `.xls` / `.xlsx` の扱い**: NTF は `.xls` のみ使用し `.xlsx` はシャドウされた未使用ファイル。変換は正データである `.xls` を YAML 化する方針。`.xlsx` は (a) 変換対象外として Task #4 で単純削除する / (b) 変換対象に含めるが出力YAMLが衝突するため不可、のいずれか。→ ユーザーに確認する。

# State

- **Status**: in progress
- **Date**: 2026-10-02
- **Last completed**: #1 ベースライン全パス確認（self-check / QA 済み、user review 待ち）
- **Next**: #1 の user review → `.xlsx` 扱いの決定 → #2 設定変更
- **Notes**: ブランチ `ntf-yaml-support`（develop 起点）。全テストは1クラス3件のみ。
