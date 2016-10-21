package com.nablarch.example;

import com.nablarch.example.test.BatchRequestTestBase;
import org.junit.Test;

/**
 * プロジェクト登録HTTPメッセージ送信リクエスト単体テストクラス。
 */
public class ProjectSaveMessageActionRequestTest extends BatchRequestTestBase {

    /**
     * 正常終了のテストケース。
     * <p/>
     * 全ての出力対象フィールドにデータがある場合。
     */
    @Test
    public void testNormalEndExistAllFields() {
        execute();
    }

    /**
     * 正常終了のテストケース。
     * <p/>
     * 必須の出力対象フィールドにのみデータがある場合。
     */
    @Test
    public void testNormalEndOnlyRequireFields() {
        execute();
    }

    /**
     * 異常系のテストケース。
     */
    @Test
    public void testAbNormalEnd() {
        execute();
    }
}