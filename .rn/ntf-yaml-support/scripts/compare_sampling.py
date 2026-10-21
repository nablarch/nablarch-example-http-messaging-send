#!/usr/bin/env python3
"""Task #3 サンプリング比較用: Excel（.xlsx）のセル値と生成 YAML の値を、指定したサンプル箇所について突き合わせる。

Excel 側は dump_xlsx_cells.py と同じく標準ライブラリで OOXML を直接読む（converter / Apache POI とは独立した経路）。
比較では NTF が Excel 読み込み時に行う次の正規化だけを Excel 側に適用する（値の意味を変えない表記上の差のみ）:
  - 数値セル: NTF の PoiXlsReader は Cell#toString() を使うため、整数値の数値セルは "1.0" 形式になる
  - フィールド長 "-" の電文フィールド: NTF の DataFileFragment#addValue が正規表現 \\s*[\\r\\n]\\s* を除去する
  - セル値 "null": NTF の nullInterpreter が null に解釈する（YAML では null 値として出力される）

使い方: python3 -I compare_sampling.py <book.xlsx> <yamlDir>
出力:   TSV（yamlファイル, サンプルキー, Excel値(正規化後), YAML値, OK/NG）。NG が1件でもあれば終了コード 1。
"""
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

import yaml

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
REL_NS = "{http://schemas.openxmlformats.org/package/2006/relationships}"
REMOVE_LS_SP = re.compile(r"\s*[\r\n]\s*")


def col_index(ref):
    n = 0
    for ch in re.match(r"[A-Z]+", ref).group(0):
        n = n * 26 + (ord(ch) - ord("A") + 1)
    return n - 1


def text_of(si):
    parts = [t.text or "" for t in si.findall("m:t", NS)]
    parts += [t.text or "" for t in si.findall("m:r/m:t", NS)]
    return "".join(parts)


def java_double_str(raw):
    f = float(raw)
    if f.is_integer() and abs(f) < 1e7:
        return "%d.0" % int(f)
    return repr(f)


def load_book(path):
    """{シート名: {(行番号, 列index): 値}}。数値セルは NTF と同じ toString 表記にする。"""
    book = {}
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            shared = [text_of(si) for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS)]
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        targets = {r.get("Id"): r.get("Target") for r in rels.iter(REL_NS + "Relationship")}
        for sheet in wb.find("m:sheets", NS):
            target = targets[sheet.get("{%s}id" % NS["r"])].lstrip("/")
            target = target if target.startswith("xl/") else "xl/" + target
            cells = {}
            for row in ET.fromstring(z.read(target)).iter("{%s}row" % NS["m"]):
                for c in row.findall("m:c", NS):
                    t = c.get("t")
                    if t == "inlineStr":
                        val = text_of(c.find("m:is", NS))
                    else:
                        v = c.find("m:v", NS)
                        if v is None:
                            continue
                        if t == "s":
                            val = shared[int(v.text)]
                        elif t in (None, "n"):
                            val = java_double_str(v.text)
                        else:
                            val = v.text
                    cells[(int(row.get("r")), col_index(c.get("r")))] = val
            book[sheet.get("name")] = cells
    return book


def by_group(blocks, group_id, key="group_id"):
    return next(b for b in blocks if b[key] == group_id)


# (シート, Excel行, Excel列index(A=0), 電文"-"フィールドか, YAML値の取り出し, サンプルキー)
def body_row(y, sec, gid):
    return by_group(y[sec], gid)["records"][0]["rows"][0][0]


def header_row(y, sec, gid, i):
    return by_group(y[sec], gid)["records"][0]["rows"][0][i]


SAMPLES = {
    "testNormalEndExistAllFields": [
        (4, 1, False, lambda y: by_group(y["list_maps"], "testShots", "id")["rows"][0]["description"], "testShots[no=1].description"),
        (10, 1, False, lambda y: by_group(y["setup_tables"], "1")["rows"][0]["PROJECT_NAME"], "SETUP_TABLE[1] PROJECT_INS_REQ_ID=1 PROJECT_NAME"),
        (10, 6, False, lambda y: by_group(y["setup_tables"], "1")["rows"][0]["CLIENT_ID"], "SETUP_TABLE[1] PROJECT_INS_REQ_ID=1 CLIENT_ID(数値セル)"),
        (10, 11, False, lambda y: by_group(y["setup_tables"], "1")["rows"][0]["SALES"], "SETUP_TABLE[1] PROJECT_INS_REQ_ID=1 SALES"),
        (35, 2, False, lambda y: by_group(y["expected_tables"], "1")["rows"][0]["UPDATE_DATE"], "EXPECTED_TABLE[1] UPDATE_DATE"),
        (27, 1, True, lambda y: body_row(y, "response_body_messages", "case1"), "RESPONSE_BODY_MESSAGES[case1] JSON"),
        (54, 1, True, lambda y: body_row(y, "expected_request_body_messages", "case1"), "EXPECTED_REQUEST_BODY_MESSAGES[case1] JSON(改行入りセル)"),
    ],
    "testNormalEndOnlyRequireFields": [
        (4, 1, False, lambda y: by_group(y["list_maps"], "testShots", "id")["rows"][0]["description"], "testShots[no=1].description"),
        (10, 4, False, lambda y: by_group(y["setup_tables"], "1")["rows"][0]["PROJECT_START_DATE"], "SETUP_TABLE[1] PROJECT_INS_REQ_ID=1 PROJECT_START_DATE(null)"),
        (10, 11, False, lambda y: by_group(y["setup_tables"], "1")["rows"][0]["SALES"], "SETUP_TABLE[1] PROJECT_INS_REQ_ID=1 SALES(null)"),
        (46, 2, False, lambda y: header_row(y, "expected_request_header_messages", "case1", 1), "EXPECTED_REQUEST_HEADER_MESSAGES[case1] 再送要求フラグ"),
        (54, 1, True, lambda y: body_row(y, "expected_request_body_messages", "case1"), "EXPECTED_REQUEST_BODY_MESSAGES[case1] JSON(改行入りセル)"),
    ],
    "testAbNormalEnd": [
        (5, 1, False, lambda y: by_group(y["list_maps"], "testShots", "id")["rows"][1]["description"], "testShots[no=2].description"),
        (5, 10, False, lambda y: by_group(y["list_maps"], "testShots", "id")["rows"][1]["expectedMessageByClient"], "testShots[no=2].expectedMessageByClient"),
        (54, 1, False, lambda y: by_group(y["list_maps"], "expectedLog1", "id")["rows"][0]["message1"], "LIST_MAP=expectedLog1 message1"),
        (50, 1, False, lambda y: by_group(y["expected_tables"], "1")["rows"][0]["STATUS"], "EXPECTED_TABLE[1] STATUS"),
        (27, 1, True, lambda y: body_row(y, "response_body_messages", "case1"), "RESPONSE_BODY_MESSAGES[case1] JSON"),
        (44, 1, True, lambda y: body_row(y, "response_body_messages", "case2"), "RESPONSE_BODY_MESSAGES[case2] JSON"),
        (100, 1, True, lambda y: body_row(y, "expected_request_body_messages", "case2"), "EXPECTED_REQUEST_BODY_MESSAGES[case2] JSON(改行入りセル)"),
    ],
}


def main(book_path, yaml_dir):
    book = load_book(book_path)
    ng = 0
    for sheet, samples in SAMPLES.items():
        with open(os.path.join(yaml_dir, sheet + ".yaml"), encoding="utf-8") as f:
            y = yaml.safe_load(f)
        for row, col, ondemand, pick, key in samples:
            excel = book[sheet].get((row, col), "")
            if ondemand:
                excel = REMOVE_LS_SP.sub("", excel)
            if excel == "null":
                excel = None
            actual = pick(y)
            ok = excel == actual
            excel, actual = ("null" if v is None else v for v in (excel, actual))
            ng += 0 if ok else 1
            print("\t".join([sheet + ".yaml", key, "row%d" % row, excel, actual, "OK" if ok else "NG"]))
    # setUpDb: Excel 側にデータブロックが無い（コメント行のみ）ことと YAML が空であることを確認する
    setup_rows = sorted({r for (r, c) in book["setUpDb"]})
    setup_has_block = any(not book["setUpDb"][(r, 0)].startswith("//") for r in setup_rows if (r, 0) in book["setUpDb"])
    setup_yaml = os.path.getsize(os.path.join(yaml_dir, "setUpDb.yaml"))
    ok = (not setup_has_block) and setup_yaml == 0
    ng += 0 if ok else 1
    print("\t".join(["setUpDb.yaml", "全行(%d行・コメントのみ)" % len(setup_rows), "row" + ",".join(map(str, setup_rows)),
                     "データブロックなし" if not setup_has_block else "データブロックあり", "空(0B)" if setup_yaml == 0 else "%dB" % setup_yaml,
                     "OK" if ok else "NG"]))
    sys.exit(1 if ng else 0)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
