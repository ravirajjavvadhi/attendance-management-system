"""Inspect schema and aggregate counts; never import application startup."""
import ast
import json
from pathlib import Path

import psycopg2
from psycopg2 import sql

root = Path(__file__).resolve().parents[1]
dsn = next(
    line.split("=", 1)[1].strip().strip('"').strip("'")
    for line in (root / "backend/.env").read_text().splitlines()
    if line.strip().startswith("DATABASE_URL=")
)
try:
    conn = psycopg2.connect(dsn, connect_timeout=12)
    conn.set_session(readonly=True)
    cur = conn.cursor()
    cur.execute("SET LOCAL statement_timeout = '12000ms'")
    cur.execute("SHOW transaction_read_only")
    result = {"transaction_read_only": cur.fetchone()[0]}
    cur.execute("SELECT table_name,column_name FROM information_schema.columns WHERE table_schema='public' ORDER BY table_name,ordinal_position")
    schema = {}
    for table, column in cur.fetchall():
        schema.setdefault(table, []).append(column)
    result["tables"] = schema
    gaps = []
    for f in (root / "backend/app/models").glob("*.py"):
        for cls in ast.parse(f.read_text(encoding="utf-8-sig")).body:
            if not isinstance(cls, ast.ClassDef):
                continue
            table, cols = None, []
            for n in cls.body:
                if isinstance(n, ast.Assign):
                    for t in n.targets:
                        if isinstance(t, ast.Name) and t.id == "__tablename__" and isinstance(n.value, ast.Constant):
                            table = n.value.value
                        elif isinstance(t, ast.Name) and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) and n.value.func.id == "Column":
                            cols.append(t.id)
            if table:
                if table not in schema:
                    gaps.append(f"Missing table: {table}")
                else:
                    gaps.extend(f"Missing column: {table}.{c}" for c in cols if c not in schema[table])
    result["model_column_gaps"] = gaps
    result["counts"] = {}
    for table in ["institutions", "users", "student_profiles", "faculty_profiles", "parent_profiles", "parent_student_links", "academic_sessions", "erp_timetable", "attendance_records", "sms_queue"]:
        if table in schema:
            cur.execute(sql.SQL("SELECT count(*) FROM {}").format(sql.Identifier(table)))
            result["counts"][table] = cur.fetchone()[0]
    cur.execute("SELECT role,count(*) FROM users GROUP BY role ORDER BY role")
    result["role_counts"] = dict(cur.fetchall())
    conn.rollback()
    conn.close()
    (root / "analysis/database-schema-summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "tables"}, indent=2))
    print("Public tables:", len(schema))
except Exception as exc:
    from urllib.parse import urlsplit
    detail = str(exc).replace(dsn, "[database URL redacted]")
    password = urlsplit(dsn).password
    if password:
        detail = detail.replace(password, "[redacted]")
    print("Read-only schema check failed:", type(exc).__name__, detail)
    raise SystemExit(1)
