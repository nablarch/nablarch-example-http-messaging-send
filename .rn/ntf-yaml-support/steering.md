# nablarch-example-http-messaging-send NTF YAML 対応 steering

## Overview
- 目的・背景: NTF（Nablarch Testing Framework）のAI対応として、AIが読み書きできないバイナリ形式のExcelテストデータをYAML形式へ移行する（背景資料: https://github.com/Fintan-contents/nablarch-system-development-guide/pull/211）。
- Acceptance criteria 要約:
  - 既存 `ntf-yaml-support` ブランチの履歴（過去の移行コミット）を維持したまま、先端の上に develop 一致ツリーのベースラインコミットを積み、task-1〜5 を**再実施**する（スキップ禁止）
  - ベースライン（develop 同一）で全テストがパスすることを確認済み
  - `pom.xml` に `nablarch-testing-yaml:1.0.0-SNAPSHOT`（test 依存）と `nablarch-testing-converter:1.0.0-SNAPSHOT`（`<build><plugins>` のビルドプラグイン）を追加
  - `YamlTestDataParser`（`testDataParser`）を、`testDataParser` が参照される全フェーズで有効な設定ファイルに追加（`interpreters` は `dateTimeInterpreter` → `compositeInterpreter` の2つのみを直接記載）
  - 全 Excel を YAML に変換（サンプリング一致確認）→ Excel 削除 → YAML で全テストパス
- 対象プロジェクト名: nablarch-example-http-messaging-send
- 指示書: `.rn/ntf-yaml-support/ntf-yaml-support-instructions_http-messaging-send_V1.6.md`（原本: `/home/k10949/instructions/ntf-yaml-support-instructions_http-messaging-send_V1.6.md`）

## Build / Test
- 環境: Maven 3.9.16 / JDK 17（Temurin 17.0.20、Maven 実行時の Java）、H2 組み込み（別途DBサーバ不要）
- README の記載: ビルドは `mvn clean package`。DBセットアップ及びエンティティクラスの作成は `mvn package` に含まれ、`mvn generate-resources` で個別実行も可能。
- 本プロジェクトに `gsp` プロファイルは存在しない（pom の profile は `dev-deploy` のみ）。`gsp-dba-maven-plugin`（execution id `gsp`: generate-ddl / execute-ddl / load-data）は `generate-resources` フェーズに無条件バインドされているため、`-P gsp` 指定は不要。
- **テストコマンド**: `LANG=ja_JP.UTF-8 LC_ALL=ja_JP.UTF-8 mvn clean test`（`generate-resources` を内包し、DBセットアップ・エンティティ生成〜テストまで一括実行）
  - エンティティ生成のみ: `mvn clean generate-resources`
  - ロケール: NTF のメッセージ解決のため `ja_JP.UTF-8` を指定する（`C.UTF-8` ではメッセージ解決に失敗しテストが落ちることを過去作業で確認済み）
- 依存解決確認: `mvn dependency:resolve` / converter プラグイン確認: `mvn help:describe -Dplugin=com.nablarch.framework:nablarch-testing-converter:1.0.0-SNAPSHOT`
- 変換: `mvn com.nablarch.framework:nablarch-testing-converter:1.0.0-SNAPSHOT:convert`（pom の plugin `<configuration>` に from/to/input/output/overwrite を設定）

## 対象テスト・Excel
- テストクラス: `src/test/java/com/nablarch/example/ProjectSaveMessageActionRequestTest.java`（`@BatchRequestTest` のリクエスト単体テスト、テスト3件。**ベースライン基準値: Tests run: 3** — 移行後に件数が減っていないことを確認する）
- Excel: 同名の `.xls`（49664B）と `.xlsx`（26965B）が**併存**。NTF の `PoiXlsReader` は `.xls` を優先解決するため `.xlsx` はシャドウされた未使用ファイル。Task #3 で併存チェックを行う。

## Scripts
- `.rn/ntf-yaml-support/scripts/` 配下に格納する。作成時は用途をここと該当 `checks/task-N.md` に記載する。
- （現時点で作成したスクリプトなし）

## Tasks

### #1: ベースライン化（developと同一状態）し、全PASSを確認する
**Purpose**: 既存の `ntf-yaml-support` ブランチ（履歴維持）の先端の上に、ワーキングツリー全体を `develop` と同一内容へ揃えるコミットを1つ新規に積み、その状態で全テストがパスすることを確認する（過去の移行コミットがあっても必ず再実施）。
**Prerequisites**: none
**Steps**:
- [x] 既存の `ntf-yaml-support` ブランチ上で作業する（新規作成なし。先端 `f941f6a` を維持）
- [x] 巻き戻さず現在の先端の上に処理を積む（rebase / reset --hard / amend 不使用）
- [x] `develop` の存在を確認し、`git read-tree -u --reset develop` → `git commit` でベースラインコミット `e52219e` を積む（tree `80792e0` が develop と一致）
- [x] README を確認し、ビルド・テスト手順を把握する（上記 Build / Test）
- [x] steering.md の初版を作成する（本ファイル。scripts は現時点で不要）
- [x] 本指示書を `.rn/ntf-yaml-support/` へ同名コピーし、`cmp` で原本と同一を確認する
- [x] エンティティ生成（`generate-resources` に gsp 実行がバインド。`mvn clean test` に内包）
- [x] `LANG=ja_JP.UTF-8 LC_ALL=ja_JP.UTF-8 mvn clean test` → BUILD SUCCESS（Tests run: 3, Failures: 0, Errors: 0）
- [x] 結果を `checks/task-1.md` に記録する
- [x] 変更ファイルをコミットする
- [x] self-check
- [x] QA expert review (Agent: general-purpose / Opus)
- [ ] user review（全 task 完了後にまとめて実施）
**Completion criteria**:
- 既存の `ntf-yaml-support` ブランチ上で作業しており、コミット履歴が維持されている
- ブランチの既存先端の上に、ワーキングツリー全体が `develop` と同一内容になる新規コミットが1つ積まれている
- `mvn test` が全テストパスで終了している（BUILD SUCCESS）
- 本指示書のコピーが `.rn/ntf-yaml-support/` 配下に原本と同一内容で配置され、コミットされている

### #2: 設定変更 — pom.xml と unit-test.xml にYAML対応を追加
**Purpose**: `pom.xml` に `nablarch-testing-yaml`（test 依存）と `nablarch-testing-converter`（ビルドプラグイン）を追加し、`YamlTestDataParser`（`testDataParser`）を `testDataParser` が参照される全フェーズで有効になる設定ファイルへ追加する（interpreters は testdata.html の設定例どおり）。
**Prerequisites**: #1
**Steps**:
- [ ] `pom.xml` に `nablarch-testing-yaml:1.0.0-SNAPSHOT`（test scope）を追加する
- [ ] `pom.xml` の `<build><plugins>` に `nablarch-testing-converter:1.0.0-SNAPSHOT` をビルドプラグインとして追加する（from=xls / to=yaml / input / output / overwrite）
- [ ] 同期送信系（応答電文あり）でアクション実行中にモックが `testDataParser` を参照する構成かを判定する
- [ ] 判定結果に応じて `YamlTestDataParser` を配置する（interpreters: `dateTimeInterpreter` → `compositeInterpreter`）
- [ ] `mvn validate` / `mvn dependency:resolve` / `mvn help:describe`（converter）で解決確認
- [ ] 変更したファイルをコミットする
- [ ] self-check
- [ ] QA expert review (Agent: general-purpose / Opus)
- [ ] language expert review (Agent: general-purpose / Opus)
- [ ] software-engineering expert review (Agent: general-purpose / Opus)
- [ ] user review
**Completion criteria**:
- `pom.xml` に `nablarch-testing-yaml:1.0.0-SNAPSHOT` が test スコープで追加されている
- `pom.xml` の `<build><plugins>` に `nablarch-testing-converter:1.0.0-SNAPSHOT` がビルドプラグイン（plugin直下 `<configuration>` に変換パラメータを設定し、CLIで `convert` ゴールを実行）として追加されている
- `testDataParser`（`YamlTestDataParser`）が全フェーズで有効になる設定ファイルに追加され、`interpreters` は `<list>` に `dateTimeInterpreter` → `compositeInterpreter` の2つのみ
- `mvn dependency:resolve` が成功し、converter プラグインの `convert` ゴールが `mvn help:describe` で解決できる

### #3: ExcelテストデータをYAMLに変換
**Purpose**: `nablarch-testing-converter` で Excel テストデータを YAML に変換し、テストのソースツリー内に配置して、変換内容をサンプリングで確認する。
**Prerequisites**: #2
**Steps**:
- [ ] 対象 Excel ファイルの所在を確認する
- [ ] 同名 `.xls` / `.xlsx` の併存を確認し、該当時は POMなし一時ディレクトリで個別変換・差分確認（結果を `.rn/` 配下に保存）のうえ未使用側を変換前に削除する
- [ ] converter README の手順で全対象 Excel を YAML 変換する
- [ ] 各 YAML について Excel とサンプリング比較する（各ファイル最低3件）
- [ ] 比較結果を `checks/task-3.md` に記録する
- [ ] 変換した YAML をコミットする（Excel はまだ削除しない）
- [ ] self-check
- [ ] QA expert review (Agent: general-purpose / Opus)
- [ ] user review
**Completion criteria**:
- 変換対象の全 Excel に対応する YAML が生成されている
- サンプリング比較で Excel と YAML の内容が一致している
- 変換後の YAML がコミットされている

### #4: Excelを削除する
**Purpose**: 変換対象だった Excel を削除してコミットする。
**Prerequisites**: #3
**Steps**:
- [ ] 変換対象となった Excel ファイルを削除する
- [ ] 削除結果（残存 Excel 0件）を `checks/task-4.md` に記録する
- [ ] Excel 削除をコミットする
- [ ] self-check
- [ ] QA expert review (Agent: general-purpose / Opus)
- [ ] user review
**Completion criteria**:
- 変換対象だった全 Excel ファイルが削除されている
- 削除がコミットされている

### #5: YAMLテストデータで全テストをパスさせる
**Purpose**: Excel なしで全テストがパスすることを確認する。
**Prerequisites**: #4
**Steps**:
- [ ] `mvn clean test` が BUILD SUCCESS になることを確認する
- [ ] テストログで YamlTestDataParser が実際に使われていることを確認する
- [ ] self-check
- [ ] QA expert review (Agent: general-purpose / Opus)
- [ ] language expert review (Agent: general-purpose / Opus)
- [ ] software-engineering expert review (Agent: general-purpose / Opus)
- [ ] user review
**Completion criteria**:
- `mvn test` が BUILD SUCCESS で終了する（全テストパス、Excel ファイルなし）
- テストログで YamlTestDataParser が実際に使われていることが確認できる

## State
- Status: Task #1 完了（self-check OK / QA OK）、Task #2 実施中
- Next: Task #2
- Notes: テストログ先頭には実行時の `git rev-parse HEAD` を記録する（Task #1 QA 改善点）
