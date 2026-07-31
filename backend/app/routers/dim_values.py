from fastapi import APIRouter, HTTPException

from app.database import get_pool
from app.models import DimValueCreate, DimValueResponse

router = APIRouter()


@router.get("", response_model=list[DimValueResponse])
async def list_dim_values():
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM dimension_values ORDER BY dimension, id"
        )
        return [dict(r) for r in rows]


@router.post("", response_model=DimValueResponse, status_code=201)
async def create_dim_value(body: DimValueCreate):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO dimension_values
               (dimension, value_name, definition, examples, counter_examples, decision_rules, literature_ref)
               VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *""",
            body.dimension,
            body.value_name,
            body.definition,
            body.examples,
            body.counter_examples,
            body.decision_rules,
            body.literature_ref,
        )
        return dict(row)


@router.put("/{dim_id}", response_model=DimValueResponse)
async def update_dim_value(dim_id: int, body: DimValueCreate):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """UPDATE dimension_values SET
               dimension=$1, value_name=$2, definition=$3, examples=$4,
               counter_examples=$5, decision_rules=$6, literature_ref=$7,
               updated_at=NOW()
               WHERE id=$8 RETURNING *""",
            body.dimension,
            body.value_name,
            body.definition,
            body.examples,
            body.counter_examples,
            body.decision_rules,
            body.literature_ref,
            dim_id,
        )
        if not row:
            raise HTTPException(404, "Dimension value not found")
        return dict(row)


@router.delete("/{dim_id}", status_code=204)
async def delete_dim_value(dim_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM dimension_values WHERE id=$1", dim_id
        )
        if result == "DELETE 0":
            raise HTTPException(404, "Dimension value not found")
