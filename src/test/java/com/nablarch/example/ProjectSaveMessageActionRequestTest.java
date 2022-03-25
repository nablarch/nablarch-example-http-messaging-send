package com.nablarch.example;

import nablarch.test.core.batch.BatchRequestTestSupport;
import nablarch.test.junit5.extension.batch.BatchRequestTest;
import org.junit.jupiter.api.Test;

/**
 * プロジェクト登録HTTPメッセージ送信リクエスト単体テストクラス。
 */
@BatchRequestTest
class ProjectSaveMessageActionRequestTest {

    BatchRequestTestSupport support;

    /**
     * 正常終了のテストケース。
     * <p/>
     * 全ての出力対象フィールドにデータがある場合。
     */
    @Test
    void testNormalEndExistAllFields() {
        support.execute(support.testName.getMethodName());
    }

    /**
     * 正常終了のテストケース。
     * <p/>
     * 必須の出力対象フィールドにのみデータがある場合。
     */
    @Test
    void testNormalEndOnlyRequireFields() {
        support.execute(support.testName.getMethodName());
    }

    /**
     * 異常系のテストケース。
     */
    @Test
    void testAbNormalEnd() {
        support.execute(support.testName.getMethodName());
    }
}