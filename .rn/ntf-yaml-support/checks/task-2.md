# task-2 Completion Check

## 配置先の判定

- 本テスト（`ProjectSaveMessageActionRequestTest`、`@BatchRequestTest`）はアクション `ProjectSaveMessageAction` が `MessageSender.sendSync` で同期送信を行い、テストデータに応答電文（`response_*`）を持つ同期送信系テストである。
- アクション実行中、同期送信モック `RequestTestingMessagingClient`（`src/test/resources/http-messaging-send-boot.xml` に定義）が `RequestTestingSendSyncSupport`（nablarch-testing `RequestTestingSendSyncSupport.java:156` → `TestSupport#getTestDataParser` = `SystemRepository.get("testDataParser")`）経由でテストデータを読む。アクション実行時は diConfig（`http-messaging-send-boot.xml`）で `SystemRepository` が再構築されるため、**該当**と判定。
- `unit-test.xml` は `http-messaging-send-boot.xml` を import している（`unit-test.xml:7`）ため、Rules の方針どおり **diConfig 側（`src/test/resources/http-messaging-send-boot.xml`）に集約**し、`unit-test.xml` には重複定義を置かない。本番用 `src/main/resources/http-messaging-send-boot.xml` は変更しない。
- 定義位置は `nablarch/test/test-data.xml` の import および `dbInfo` 定義より後。

## Completion Criteria

| Criterion | Self-check | Evidence | QA | QA Evidence |
|---|---|---|---|---|
| `pom.xml` に `nablarch-testing-yaml:1.0.0-SNAPSHOT` が test スコープで追加されている | OK | `<dependencies>` 末尾に groupId `com.nablarch.framework` / version `1.0.0-SNAPSHOT` / scope `test` で追加 | - | - |
| `pom.xml` の `<build><plugins>` に `nablarch-testing-converter:1.0.0-SNAPSHOT` がビルドプラグインとして追加されている | OK | `<build><plugins>` 末尾に追加。plugin 直下 `<configuration>` に from=xls / to=yaml / input=output=`${project.basedir}/src/test/java` / overwrite=true（nablarch-example-batch と同一構成）。依存（`<dependencies>`）には含めない | - | - |
| `testDataParser`（`YamlTestDataParser`）が全フェーズで有効な設定ファイルに追加され、interpreters が設定例どおり | OK | `src/test/resources/http-messaging-send-boot.xml` に追加（unit-test.xml が import するためセットアップ/実行/検証の全フェーズに有効）。`dbInfo` ref、`interpreters` 内 `<list>` に `dateTimeInterpreter` → `compositeInterpreter` の2つのみ、`testDataReader` 指定なし | - | - |
| `mvn dependency:resolve` 成功、converter の `convert` ゴールが `mvn help:describe` で解決できる | OK | `mvn validate` rc=0。`mvn dependency:resolve` BUILD SUCCESS（`nablarch-testing-yaml:jar:1.0.0-SNAPSHOT:test` を解決）。`mvn help:describe -Dplugin=com.nablarch.framework:nablarch-testing-converter:1.0.0-SNAPSHOT` BUILD SUCCESS（Goal Prefix `nablarch-testing-converter`、ゴール `convert`） | - | - |

## QA Expert Review

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Meaningful tests/verification | - | - |
| Edge case coverage | - | - |

## Expert Reviews (code changes only)

### Language Expert

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Best practices | - | - |
| Codebase style consistency | - | - |
| GWT test format | - | - |

### Software-engineering Expert

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Separation of concerns | - | - |
| System integrity | - | - |
| Maintainability | - | - |

## Overall Verdict

- Self-check: OK
- QA: -
- Language expert: -
- Software-engineering expert: -
- Ready for user review: -
