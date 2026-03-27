# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path


NS = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
MAIN_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def excel_serial_to_date(value: str | None) -> str | None:
    if not value:
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    if number <= 0:
        return None
    base = datetime(1899, 12, 30)
    return (base + timedelta(days=number)).date().isoformat()


def sql_value(value: object) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, int):
        return str(value)
    text = str(value).replace("\\", "\\\\").replace("'", "''")
    return f"'{text}'"


def normalize_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def col_letters(cell_ref: str) -> str:
    match = re.match(r"([A-Z]+)", cell_ref)
    return match.group(1) if match else ""


@dataclass
class WorkbookData:
    shared_strings: list[str]


def load_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    shared_path = "xl/sharedStrings.xml"
    if shared_path not in zf.namelist():
        return []
    root = ET.fromstring(zf.read(shared_path))
    values: list[str] = []
    for si in root.findall("a:si", NS):
        parts = [node.text or "" for node in si.iterfind(".//a:t", NS)]
        values.append("".join(parts))
    return values


def read_sheet_rows(zf: zipfile.ZipFile, sheet_path: str, shared_strings: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for _, elem in ET.iterparse(zf.open(sheet_path), events=("end",)):
        if elem.tag != f"{MAIN_NS}row":
            continue
        row_data: dict[str, str] = {}
        for cell in elem.findall(f"{MAIN_NS}c"):
            ref = cell.attrib.get("r", "")
            col = col_letters(ref)
            cell_type = cell.attrib.get("t")
            value_node = cell.find(f"{MAIN_NS}v")
            inline_node = cell.find(f"{MAIN_NS}is")
            value = ""
            if cell_type == "s" and value_node is not None and value_node.text is not None:
                value = shared_strings[int(value_node.text)]
            elif cell_type == "inlineStr" and inline_node is not None:
                value = "".join(node.text or "" for node in inline_node.iterfind(f".//{MAIN_NS}t"))
            elif value_node is not None and value_node.text is not None:
                value = value_node.text
            row_data[col] = value.strip()
        if row_data:
            rows.append(row_data)
        elem.clear()
    return rows


def build_category_insert(rows: list[dict[str, str]]) -> list[str]:
    statements: list[str] = ["DELETE FROM stock_category;"]
    for idx, row in enumerate(rows[1:], start=2):
        product_name = row.get("B")
        if not product_name:
            continue
        values = {
            "product_name": product_name,
            "product_brand": row.get("C") or None,
            "product_spec": row.get("D") or None,
            "pn_code": row.get("E") or None,
            "material_code": row.get("F") or None,
            "major_category": row.get("G") or None,
            "category_serial_no": row.get("H") or None,
            "category_suffix_code": row.get("I") or None,
            "applicable_device_model": row.get("J") or None,
            "device_type": row.get("K") or None,
            "source_sheet": "产品分类",
            "source_row_no": idx,
            "remark": None,
        }
        statements.append(
            "INSERT INTO stock_category "
            "(product_name, product_brand, product_spec, pn_code, material_code, major_category, "
            "category_serial_no, category_suffix_code, applicable_device_model, device_type, "
            "source_sheet, source_row_no, remark, create_time, update_time, create_timestamp, update_timestamp, is_deleted, status) "
            f"VALUES ({', '.join(sql_value(values[key]) for key in values)}, NOW(), NOW(), UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 0, 1);"
        )
    return statements


def resolve_category_id_expr() -> str:
    return (
        "(SELECT sc.id FROM stock_category sc "
        "WHERE sc.is_deleted = 0 "
        "AND ("
        "  (NULLIF({material_code}, '') IS NOT NULL AND sc.material_code = NULLIF({material_code}, '')) "
        "  OR (NULLIF({pn_code}, '') IS NOT NULL AND sc.pn_code = NULLIF({pn_code}, '')) "
        "  OR (sc.product_name = {product_name} "
        "      AND COALESCE(sc.product_brand, '') = COALESCE({product_brand}, '') "
        "      AND COALESCE(sc.product_spec, '') = COALESCE({product_spec}, ''))"
        ") "
        "ORDER BY sc.id ASC LIMIT 1)"
    )


def build_record_insert(rows: list[dict[str, str]]) -> list[str]:
    statements: list[str] = ["DELETE FROM stock_in_out_record;"]
    category_id_template = resolve_category_id_expr()
    for idx, row in enumerate(rows[1:], start=2):
        product_name = row.get("D")
        if not product_name:
            continue
        inbound_qty = normalize_int(row.get("Q"))
        stock_qty = normalize_int(row.get("U"))
        outbound_qty = normalize_int(row.get("V"))
        inferred_outbound = 1 if (outbound_qty and outbound_qty > 0) or (stock_qty == 0 and inbound_qty) else 0
        values = {
            "row_no": normalize_int(row.get("A")),
            "category_name": row.get("B") or None,
            "product_type": row.get("C") or None,
            "product_name": product_name,
            "product_brand": row.get("E") or None,
            "product_spec": row.get("F") or None,
            "product_description": row.get("G") or None,
            "pn_code": row.get("H") or None,
            "material_code": row.get("I") or None,
            "serial_number": row.get("J") or None,
            "target_device_type": row.get("K") or None,
            "target_device_brand": row.get("L") or None,
            "target_device_model": row.get("M") or None,
            "major_category": row.get("N") or None,
            "usage_scene": row.get("O") or None,
            "document_no": row.get("P") or None,
            "inbound_qty": inbound_qty,
            "inbound_date": excel_serial_to_date(row.get("R")),
            "inbound_room": row.get("S") or None,
            "storage_location": row.get("T") or None,
            "stock_qty": stock_qty,
            "outbound_qty": outbound_qty,
            "outbound_date": excel_serial_to_date(row.get("W")),
            "actual_device_type": row.get("X") or None,
            "actual_device_brand": row.get("Y") or None,
            "actual_device_model": row.get("Z") or None,
            "device_position": row.get("AA") or None,
            "original_owner_org": row.get("AB") or None,
            "target_room": row.get("AC") or None,
            "remark": row.get("AD") or None,
            "expansion_remark": row.get("AE") or None,
            "source_sheet": "出入库明细表",
            "source_row_no": idx,
            "is_outbound": inferred_outbound,
        }
        category_id_expr = category_id_template.format(
            material_code=sql_value(values["material_code"]),
            pn_code=sql_value(values["pn_code"]),
            product_name=sql_value(values["product_name"]),
            product_brand=sql_value(values["product_brand"]),
            product_spec=sql_value(values["product_spec"]),
        )
        ordered_keys = [
            "is_outbound",
            "category_name",
            "product_type",
            "product_name",
            "product_brand",
            "product_spec",
            "product_description",
            "pn_code",
            "material_code",
            "serial_number",
            "target_device_type",
            "target_device_brand",
            "target_device_model",
            "major_category",
            "usage_scene",
            "document_no",
            "inbound_qty",
            "inbound_date",
            "inbound_room",
            "storage_location",
            "stock_qty",
            "outbound_qty",
            "outbound_date",
            "actual_device_type",
            "actual_device_brand",
            "actual_device_model",
            "device_position",
            "original_owner_org",
            "target_room",
            "remark",
            "expansion_remark",
            "source_sheet",
            "source_row_no",
        ]
        statements.append(
            "INSERT INTO stock_in_out_record "
            "(row_no, category_id, is_outbound, category_name, product_type, product_name, product_brand, product_spec, "
            "product_description, pn_code, material_code, serial_number, target_device_type, target_device_brand, "
            "target_device_model, major_category, usage_scene, document_no, inbound_qty, inbound_date, inbound_room, "
            "storage_location, stock_qty, outbound_qty, outbound_date, actual_device_type, actual_device_brand, "
            "actual_device_model, device_position, original_owner_org, target_room, remark, expansion_remark, "
            "source_sheet, source_row_no, create_time, update_time, create_timestamp, update_timestamp, is_deleted, status) "
            f"VALUES ({sql_value(values['row_no'])}, {category_id_expr}, "
            + ", ".join(sql_value(values[key]) for key in ordered_keys)
            + ", NOW(), NOW(), UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 0, 1);"
        )
    return statements


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--excel", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default="3306")
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--database", required=True)
    args = parser.parse_args()

    excel_path = Path(args.excel)
    with zipfile.ZipFile(excel_path) as zf:
        shared_strings = load_shared_strings(zf)
        category_rows = read_sheet_rows(zf, "xl/worksheets/sheet1.xml", shared_strings)
        record_rows = read_sheet_rows(zf, "xl/worksheets/sheet2.xml", shared_strings)

    sql_lines = [
        "SET NAMES utf8mb4;",
        "START TRANSACTION;",
        *build_category_insert(category_rows),
        *build_record_insert(record_rows),
        "COMMIT;",
        "SELECT 'stock_category' AS table_name, COUNT(*) AS total FROM stock_category;",
        "SELECT 'stock_in_out_record' AS table_name, COUNT(*) AS total FROM stock_in_out_record;",
        "SELECT COUNT(*) AS matched_category_records FROM stock_in_out_record WHERE category_id IS NOT NULL;",
    ]

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".sql", delete=False) as tmp:
        tmp.write("\n".join(sql_lines))
        tmp_path = tmp.name

    try:
        subprocess.run(
            [
                "mysql",
                f"-h{args.host}",
                f"-P{args.port}",
                f"-u{args.user}",
                f"-p{args.password}",
                args.database,
            ]
            + [f"--execute=source {tmp_path}"],
            check=True,
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
