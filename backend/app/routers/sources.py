from fastapi import APIRouter, HTTPException

from app.database import get_pool
from app.models import SourceCreate, SourceUpdate, SourceResponse

router = APIRouter()


@router.get("", response_model=list[SourceResponse])
async def list_sources():
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT s.*, COUNT(c.id)::int AS category_count
            FROM sources s
            LEFT JOIN categories c ON c.source_id = s.id
            GROUP BY s.id
            ORDER BY s.id
        """)
        return [dict(r) for r in rows]


@router.post("", response_model=SourceResponse, status_code=201)
async def create_source(body: SourceCreate):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO sources (name, source_type, url, notes) "
            "VALUES ($1, $2, $3, $4) RETURNING *",
            body.name, body.source_type, body.url, body.notes,
        )
        d = dict(row)
        d["category_count"] = 0
        return d


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(source_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT s.*, COUNT(c.id)::int AS category_count "
            "FROM sources s LEFT JOIN categories c ON c.source_id = s.id "
            "WHERE s.id = $1 GROUP BY s.id",
            source_id,
        )
        if not row:
            raise HTTPException(404, "Source not found")
        return dict(row)


@router.put("/{source_id}", response_model=SourceResponse)
async def update_source(source_id: int, body: SourceUpdate):
    pool = await get_pool()
    field_values: dict[str, object] = {}
    for k in ("name", "source_type", "url", "status", "notes"):
        v = getattr(body, k, None)
        if v is not None:
            field_values[k] = v
    if not field_values:
        raise HTTPException(400, "No fields to update")

    placeholders = []
    values: list[object] = []
    for i, k in enumerate(field_values.keys(), start=1):
        if k == "updated_at":
            placeholders.append(f"{k}=NOW()")
        else:
            placeholders.append(f"{k}=${i}")
            values.append(field_values[k])
    placeholders.append(f"updated_at=NOW()")
    values.append(source_id)
    set_clause = ", ".join(placeholders)

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            f"UPDATE sources SET {set_clause} WHERE id=${len(values)} RETURNING *",
            *values,
        )
        if not row:
            raise HTTPException(404, "Source not found")
        d = dict(row)
        d["category_count"] = d.get("category_count", 0)
        return d


@router.delete("/{source_id}", status_code=204)
async def delete_source(source_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM sources WHERE id=$1", source_id
        )
        if result == "DELETE 0":
            raise HTTPException(404, "Source not found")
