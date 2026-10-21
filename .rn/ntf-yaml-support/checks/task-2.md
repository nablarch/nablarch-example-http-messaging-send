# task-2 Completion Check

## 配置先の判定

- 本テスト（`ProjectSaveMessageActionRequestTest`、`@BatchRequestTest`）はアクション `ProjectSaveMessageAction` が `MessageSender.sendSync` で同期送信を行い、テストデータに応答電文（`response_*`）を持つ同期送信系テストである。
- アクション実行中、同期送信モック `RequestTestingMessagingClient`（`src/test/resources/http-messaging-send-boot.xml` に定義）が `RequestTestingSendSyncSupport`（nablarch-testing `RequestTestingSendSyncSupport.java:156` → `TestSupport#getTestDataParser` = `SystemRepository.get("testDataParser")`）経由でテストデータを読む。アクション実行時は diConfig（`http-messaging-send-boot.xml`）で `SystemRepository` が再構築されるため、**該当**と判定。
- `unit-test.xml` は `http-messaging-send-boot.xml` を import している（`unit-test.xml:7`）ため、Rules の方針どおり **diConfig 側（`src/test/resources/http-messaging-send-boot.xml`）に集約**し、`unit-test.xml` には重複定義を置かない。本番用 `src/main/resources/http-messaging-send-boot.xml` は変更しない。
- 定義位置は `nablarch/test/test-data.xml` の import および `dbInfo` 定義より後。

## Completion Criteria

| Criterion | Self-check | Evidence | QA | QA Evidence |
|---|---|---|---|---|
| `pom.xml` に `nablarch-testing-yaml:1.0.0-SNAPSHOT` が test スコープで追加されている | OK | `<dependencies>` 末尾に groupId `com.nablarch.framework` / version `1.0.0-SNAPSHOT` / scope `test` で追加 | OK | `pom.xml` 120〜125行に groupId `com.nablarch.framework` / `1.0.0-SNAPSHOT` / scope `test`。resolve ログで `nablarch-testing-yaml:jar:1.0.0-SNAPSHOT:test` 解決・BUILD SUCCESS |
| `pom.xml` の `<build><plugins>` に `nablarch-testing-converter:1.0.0-SNAPSHOT` がビルドプラグインとして追加されている | OK | `<build><plugins>` 末尾に追加。plugin 直下 `<configuration>` に from=xls / to=yaml / input=output=`${project.basedir}/src/test/java` / overwrite=true（nablarch-example-batch と同一構成）。依存（`<dependencies>`）には含めない | OK | `<build><plugins>` 末尾に追加、plugin 直下 `<configuration>` に from/to/input/output/overwrite。`<executions>` なし・`<dependencies>` 非含有で CLI 実行専用 |
| `testDataParser`（`YamlTestDataParser`）が全フェーズで有効な設定ファイルに追加され、interpreters が設定例どおり | OK | `src/test/resources/http-messaging-send-boot.xml` に追加（unit-test.xml が import するためセットアップ/実行/検証の全フェーズに有効）。`dbInfo` ref、`interpreters` 内 `<list>` に `dateTimeInterpreter` → `compositeInterpreter` の2つのみ、`testDataReader` 指定なし | OK | `MainForRequestTesting` が diConfig でリポジトリ再構築、`RequestTestingSendSyncSupport.java:155` が `SystemRepository.get("testDataParser")` を使用。test-classes が classes より優先、本番 boot 差分なし。`<list>` 直接記載で2つのみ・順序正・`testDataReader` なし・定義順正（testdata.rst と一致） |
| `mvn dependency:resolve` 成功、converter の `convert` ゴールが `mvn help:describe` で解決できる | OK | `mvn validate` rc=0。`mvn dependency:resolve` BUILD SUCCESS（`nablarch-testing-yaml:jar:1.0.0-SNAPSHOT:test` を解決）。`mvn help:describe -Dplugin=com.nablarch.framework:nablarch-testing-converter:1.0.0-SNAPSHOT` BUILD SUCCESS（Goal Prefix `nablarch-testing-converter`、ゴール `convert`） | OK | resolve / describe ログとも BUILD SUCCESS、Goal Prefix `nablarch-testing-converter`・`convert` ゴール解決 |

## QA Expert Review

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Meaningful tests/verification | OK | 配置先判定を NTF の呼び出し経路まで追って裏付け、mvn 解決もログで再確認可能。補足: `RequestTestingSendSyncSupport` は取得パーサを `BasicTestDataParser` にキャストするが、`YamlTestDataParser` は `BasicTestDataParser` を継承し `getSendSyncMessage` も実装するため問題なし。YAML パーサの実使用は Task #5 のログで確認する |
| Edge case coverage | OK | 同名 boot のクラスパス優先順位・`unit-test.xml` との重複回避・参照解決の定義順・本番 boot 非変更を確認。改善: validate は `-q` 実行のためログに rc が残らない。test 側 boot が実際に読まれることを Task #5 のログ（パーサのクラス名）で確認する |

## Expert Reviews (code changes only)

### Language Expert

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Best practices | OK | yaml は test scope 依存、converter は `<executions>` なしのプラグインでライフサイクル非連動。bom（`6-NEXT-SNAPSHOT`）未登録のため version 明示は妥当。testDataParser は test-data.xml import・dbInfo 定義後で同名上書き、interpreters は公式例どおり。任意: SNAPSHOT 表記3か所は property 化するとリリース版差し替え時の漏れを防げる（テンプレート整合を優先し現状維持） |
| Codebase style consistency | OK | 2スペースインデント、dependency 間空行あり・plugin 間空行なし、改行コード（pom CRLF / boot LF）が既存と一致。任意: 和文と英字間のスペース表記の揺れ、コメントがやや長め（配置理由の記録として有用なため NG としない） |
| GWT test format | N/A | テストコード（Java）の変更なし |

### Software-engineering Expert

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Separation of concerns | OK | YamlTestDataParser はテスト用 boot のみに定義、本番 boot は無変更。converter は `<dependencies>` に無くテストクラスパス・本番成果物に混入しない |
| System integrity | OK | セットアップ/検証は unit-test.xml の import 経由、アクション実行中は `MainForRequestTesting#setUpSystemRepository` の再構築後に同 boot から取得。後勝ち上書き・参照先（test-data-interpreter.xml の interpreter、dbInfo）の解決順も問題なし。`messagingTestDataParser`（MockMessagingClient 用）は本プロジェクト未使用 |
| Maintainability | OK | 定義は boot 1か所に集約（Rules の単一ソース化どおり）、コメントは配置理由を正しく説明。任意: 「test-data.xml の import より後に置く（後勝ち上書きのため）」旨を一言添えると並べ替え時の事故を防げる |

## Overall Verdict

- Self-check: OK
- QA: OK
- Language expert: OK
- Software-engineering expert: OK
- Ready for user review: Yes
