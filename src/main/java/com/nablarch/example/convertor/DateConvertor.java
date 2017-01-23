package com.nablarch.example.convertor;

import nablarch.core.dataformat.convertor.value.ValueConvertorSupport;
import nablarch.core.util.DateUtil;

import java.util.Date;

/**
 * {@link Date}オブジェクトを"yyyyMMdd"フォーマットの文字列に変換するコンバータ。
 *
 * @author Nabu Rakutaro
 */
public class DateConvertor extends ValueConvertorSupport<Object, String> {

    /**
     * JSONファイルから読み込む際は何もしない。
     * @param data 読み込んだJSONデータ
     * @return 読み込んだJSONデータ
     */
    @Override
    public Object convertOnRead(String data) {
        return data;
    }

    /**
     * データからJSONファイルを生成する際に、Date型オブジェクトを指定のフォーマットの文字列へ変換する。
     * @param data 変換対象の日付オブジェクト
     * @return yyyyMMddフォーマットの文字列
     * @throws IllegalArgumentException Date型ではないデータが引き渡された場合
     */
    @Override
    public String convertOnWrite(Object data) {

        if (data instanceof Date) {
            return DateUtil.formatDate((Date) data, "yyyyMMdd");
        } else if (data == null) {
            return null;
        } else {
            // Date型ではない場合
            throw new IllegalArgumentException("Target Data is not a java.util.Date Type Object.");
        }
    }
}
