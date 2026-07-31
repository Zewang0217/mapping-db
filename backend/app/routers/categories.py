from fastapi import APIRouter, HTTPException

from app.database import get_pool
from app.models import CategoryCreate, CategoryUpdate, CategoryResponse

router = APIRouter()


@router.get("/sources/{source_id}/categories", response_model=list[CategoryResponse])
async def list_categories(source_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM categories WHERE source_id=$1 ORDER BY id",
            source_id,
        )
        return [dict(r) for r in rows]


@router.post("/sources/{source_id}/categories", response_model=CategoryResponse, status_code=201)
async def create_category(source_id: int, body: CategoryCreate):
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Verify source exists
        src = await conn.fetchrow("SELECT id FROM sources WHERE id=$1", source_id)
        if not src:
            raise HTTPException(404, "Source not found")

        row = await conn.fetchrow(
            "INSERT INTO categories (source_id, original_name, description, is_threat) "
            "VALUES ($1, $2, $3, $4) RETURNING *",
            source_id, body.original_name, body.description, body.is_threat,
        )

        # Auto-create empty mapping row
        await conn.execute(
            "INSERT INTO mappings (category_id) VALUES ($1) ON CONFLICT DO NOTHING",
            row["id"],
        )

        # Update source category_count
        await conn.execute(
            "UPDATE sources SET category_count = ("
            "  SELECT COUNT(*) FROM categories WHERE source_id=$1"
            "), updated_at=NOW() WHERE id=$1",
            source_id,
        )

        return dict(row)


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: int, body: CategoryUpdate):
    pool = await get_pool()
    field_values: dict[str, object] = {}
    for k in ("original_name", "description", "is_threat", "status"):
        v = getattr(body, k, None)
        if v is not None:
            field_values[k] = v
    if not field_values:
        raise HTTPException(400, "No fields to update")

    placeholders = []
    values: list[object] = []
    for i, k in enumerate(field_values.keys(), start=1):
        placeholders.append(f"{k}=${i}")
        values.append(field_values[k])
    placeholders.append("updated_at=NOW()")
    values.append(category_id)
    set_clause = ", ".join(placeholders)

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            f"UPDATE categories SET {set_clause} WHERE id=${len(values)} RETURNING *",
            *values,
        )
        if not row:
            raise HTTPException(404, "Category not found")
        return dict(row)


@router.delete("/categories/{category_id}", status_code=204)
async def delete_category(category_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT source_id FROM categories WHERE id=$1", category_id
        )
        if not row:
            raise HTTPException(404, "Category not found")
        source_id = row["source_id"]

        await conn.execute("DELETE FROM categories WHERE id=$1", category_id)

        # Update source category_count
        await conn.execute(
            "UPDATE sources SET category_count = ("
            "  SELECT COUNT(*) FROM categories WHERE source_id=$1"
            "), updated_at=NOW() WHERE id=$1",
            source_id,
        )
