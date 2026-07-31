from fastapi import APIRouter, HTTPException

from app.database import get_pool
from app.models import MappingUpdate, MappingResponse

router = APIRouter()


@router.get("/categories/{category_id}/mapping", response_model=MappingResponse)
async def get_mapping(category_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM mappings WHERE category_id=$1", category_id
        )
        if not row:
            raise HTTPException(404, "Mapping not found")
        return dict(row)


@router.put("/categories/{category_id}/mapping", response_model=MappingResponse)
async def update_mapping(category_id: int, body: MappingUpdate):
    pool = await get_pool()
    fields: dict[str, object] = {}

    for k in ("source_dim", "mech_dim", "target_dim", "confidence", "evidence", "notes"):
        v = getattr(body, k, None)
        if v is not None:
            fields[k] = v

    if body.vuln_tags is not None:
        fields["vuln_tags"] = body.vuln_tags  # list → PostgreSQL TEXT[] auto-cast

    if not fields:
        raise HTTPException(400, "No fields to update")

    placeholders = []
    values: list[object] = []
    for i, k in enumerate(fields.keys(), start=1):
        placeholders.append(f"{k}=${i}")
        values.append(fields[k])
    placeholders.append("updated_at=NOW()")
    values.append(category_id)
    set_clause = ", ".join(placeholders)

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            f"UPDATE mappings SET {set_clause} WHERE category_id=${len(values)} RETURNING *",
            *values,
        )
        if not row:
            raise HTTPException(404, "Mapping not found")

        # Update category status to 'mapped' if all dims are filled
        if all(row.get(d) is not None for d in ("source_dim", "mech_dim", "target_dim")):
            await conn.execute(
                "UPDATE categories SET status='mapped', updated_at=NOW() WHERE id=$1",
                category_id,
            )

        return dict(row)
