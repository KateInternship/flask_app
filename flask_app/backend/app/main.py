from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import date, time as _time
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

import re
import os

from .database import get_engine

app = FastAPI(title="Machines API")

class Record(BaseModel):
    machine_name: str
    date: date
    time: _time

_valid_tbl = re.compile(r"[A-Za-z_][A-Za-z0-9_]*$")

def _sanitize_table(name: str) -> str:
    if not _valid_tbl.fullmatch(name):
        raise HTTPException(status_code=400, detail="Invalid table name")
    return name

@app.post("/add/{table_name}", summary="Add record (auto-create table)")
async def add_record(
    table_name: str = Path(..., description="Target table name"),
    rec: Record = ...
):
    table = _sanitize_table(table_name)
    engine = get_engine()

    async with engine.begin() as conn:
        await conn.execute(text(f'''
            CREATE TABLE IF NOT EXISTS "{table}" (
                id SERIAL PRIMARY KEY,
                machine_name TEXT,
                date DATE,
                time TIME
            )
        '''))
        await conn.execute(
            text(f'''
                INSERT INTO "{table}" (machine_name, date, time)
                VALUES (:machine_name, :date, :time)
            '''),
            rec.model_dump(),
        )

    return {"status": "ok", "table": table}

@app.get(
    "/query",
    summary="Get records from all tables",
    response_description="List of rows matching criteria",
)
async def query_records(
    machine_name: str = Query(..., description="Machine name"),
    date_: date = Query(..., alias="date", description="Date"),
):
    engine = get_engine()
    rows: list[dict] = []

    async with engine.begin() as conn:
        tbls = await conn.execute(text("""
            SELECT table_name
              FROM information_schema.tables
             WHERE table_schema = 'public'
        """))
        for (tbl,) in tbls.all():
            tbl = _sanitize_table(tbl)
            try:
                q = text(f'''
                    SELECT
                        machine_name,
                        date,
                        time,
                        '{tbl}' AS table_name
                    FROM "{tbl}"
                    WHERE machine_name = :machine_name
                      AND date = :date
                ''')
                result = await conn.execute(
                    q,
                    {"machine_name": machine_name, "date": date_}
                )
                rows.extend([dict(r) for r in result.mappings()])
            except Exception:
                continue

    return rows
