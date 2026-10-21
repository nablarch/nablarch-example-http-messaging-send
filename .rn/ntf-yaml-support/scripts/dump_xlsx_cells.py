#!/usr/bin/env python3
"""Task #3 サンプリング比較用: .xlsx の全シートのセル値を標準ライブラリのみで読み出してテキスト出力する。

converter（Apache POI）とは独立した経路で Excel 側の値を取得し、生成 YAML と突き合わせるために使う。
（環境に xlrd / openpyxl が無いため、.xlsx の OOXML を zipfile + ElementTree で直接解析する）

使い方: python3 -I dump_xlsx_cells.py <book.xlsx> [シート名]
出力:   <シート名>\t<行番号>\t<セル値1>\t<セル値2>...（空でない行のみ。列位置は A 列起点で空セルは空文字）
"""
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
REL_NS = "{http://schemas.openxmlformats.org/package/2006/relationships}"


def col_index(ref):
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - ord("A") + 1)
    return n - 1


def text_of(si):
    # ふりがな（rPh）はセル値ではないため除外し、直下の t と リッチテキスト r/t のみ連結する
    parts = [t.text or "" for t in si.findall("m:t", NS)]
    parts += [t.text or "" for t in si.findall("m:r/m:t", NS)]
    return "".join(parts)


def main(path, only_sheet=None):
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            shared = [text_of(si) for si in root.findall("m:si", NS)]
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        targets = {r.get("Id"): r.get("Target") for r in rels.iter(REL_NS + "Relationship")}
        for sheet in wb.find("m:sheets", NS):
            name = sheet.get("name")
            if only_sheet and name != only_sheet:
                continue
            target = targets[sheet.get("{%s}id" % NS["r"])].lstrip("/")
            if not target.startswith("xl/"):
                target = "xl/" + target
            root = ET.fromstring(z.read(target))
            for row in root.iter("{%s}row" % NS["m"]):
                cells = {}
                for c in row.findall("m:c", NS):
                    t = c.get("t")
                    if t == "inlineStr":
                        val = text_of(c.find("m:is", NS))
                    else:
                        v = c.find("m:v", NS)
                        if v is None:
                            continue
                        val = shared[int(v.text)] if t == "s" else v.text
                    cells[col_index(c.get("r"))] = val
                if any(v != "" for v in cells.values()):
                    width = max(cells) + 1
                    vals = [cells.get(i, "") for i in range(width)]
                    print("\t".join([name, row.get("r")] + [v.replace("\n", "\\n") for v in vals]))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
