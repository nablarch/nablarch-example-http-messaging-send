package com.nablarch.example;

import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

import nablarch.core.date.SystemTimeUtil;
import nablarch.core.db.statement.ParameterizedSqlPStatement;
import nablarch.core.db.statement.SqlRow;
import nablarch.core.log.Logger;
import nablarch.core.log.LoggerManager;
import nablarch.fw.DataReader;
import nablarch.fw.ExecutionContext;
import nablarch.fw.Result;
import nablarch.fw.Result.Success;
import nablarch.fw.action.BatchAction;
import nablarch.fw.messaging.MessageSender;
import nablarch.fw.messaging.MessagingException;
import nablarch.fw.messaging.SyncMessage;
import nablarch.fw.reader.DatabaseRecordReader;
import nablarch.fw.results.TransactionAbnormalEnd;

/**
 * プロジェクト登録HTTPメッセージを発行する業務アクションクラス。
 * <p>
 * プロジェクト登録要求テーブルを参照し、要求がある場合はプロジェクト登録HTTPメッセージを発行する。
 *
 * @author Nabu Rakutaro
 */
public class ProjectSaveMessageAction extends BatchAction<SqlRow> {

    /**
     * ロガー
     */
    private static final Logger LOGGER = LoggerManager.get(ProjectSaveMessageAction.class);

    /**
     * {@inheritDoc}
     * <p>
     * 同期応答メッセージ送信を行う。
     */
    @Override
    public Result handle(final SqlRow inputData, final ExecutionContext ctx) {
        LOGGER.logInfo("start");

        // ヘッダを準備
        try {
            // メッセージ送信
            MessageSender.sendSync(
                    new SyncMessage("ProjectSaveMessage")
                            .addDataRecord(inputData)
                            .setHeaderRecord(Collections.singletonMap("X-Message-Id", "1")));
        } catch (MessagingException e) {
            throw new TransactionAbnormalEnd(100, e, "error.sendServer.fail");
        }

        //処理成功
        return new Success();
    }

    /**
     * {@inheritDoc}
     * <p>
     * 処理ステータスを正常終了に更新する。
     */
    @Override
    protected void transactionSuccess(final SqlRow inputData, final ExecutionContext context) {
        final Map<String, Object> condition = new HashMap<>();
        condition.put("project_ins_req_id", inputData.getInteger("PROJECT_INS_REQ_ID"));
        condition.put("update_date", SystemTimeUtil.getTimestamp());
        final ParameterizedSqlPStatement statement = getParameterizedSqlStatement("UPDATE_STATUS_NORMAL_END");
        statement.executeUpdateByMap(condition);
    }

    /**
     * {@inheritDoc}
     * <p>
     * 処理ステータスを異常終了に更新する。
     */
    @Override
    protected void transactionFailure(final SqlRow inputData, ExecutionContext context) {
        final Map<String, Object> condition = new HashMap<>();
        condition.put("project_ins_req_id", inputData.getInteger("PROJECT_INS_REQ_ID"));
        condition.put("update_date", SystemTimeUtil.getTimestamp());
        final ParameterizedSqlPStatement statement = getParameterizedSqlStatement("UPDATE_STATUS_ABNORMAL_END");
        statement.executeUpdateByMap(condition);
    }


    /**
     * {@inheritDoc}
     * プロジェクト登録メッセージ送信要求一覧を読み込む{@link DataReader}を生成する。
     */
    @Override
    public DataReader<SqlRow> createReader(ExecutionContext ctx) {
        DatabaseRecordReader reader = new DatabaseRecordReader();
        reader.setStatement(getSqlPStatement("GET_PROJECT_INS_REQ_LIST"));
        return reader;
    }
}
