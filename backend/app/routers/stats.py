from collections import Counter

from fastapi import APIRouter

from app.database import get_pool

router = APIRouter()


@router.get("")
async def get_stats():
    pool = await get_pool()
    async with pool.acquire() as conn:
        sources = await conn.fetchval("SELECT COUNT(*) FROM sources")
        cats = await conn.fetchval("SELECT COUNT(*) FROM categories")
        mapped = await conn.fetchval(
            "SELECT COUNT(*) FROM mappings WHERE source_dim IS NOT NULL AND cardinality(source_dim) > 0"
        )
        threats = await conn.fetchval(
            "SELECT COUNT(*) FROM categories WHERE is_threat=true"
        )

        # Dimension distributions
        dims_raw = await conn.fetch(
            "SELECT source_dim, mech_dim, target_dim, confidence FROM mappings"
        )
        source_dist: Counter[str] = Counter()
        mech_dist: Counter[str] = Counter()
        target_dist: Counter[str] = Counter()
        for r in dims_raw:
            if r["source_dim"]:
                source_dist.update(r["source_dim"])
            if r["mech_dim"]:
                mech_dist.update(r["mech_dim"])
            if r["target_dim"]:
                target_dist.update(r["target_dim"])
        conf_dist = Counter(r["confidence"] for r in dims_raw if r["confidence"])

        # Source breakdown
        src_rows = await conn.fetch("""
            SELECT s.id, s.name, s.status,
                   COUNT(c.id)::int AS cats,
                   COUNT(m.id) FILTER (WHERE m.source_dim IS NOT NULL AND cardinality(m.source_dim) > 0)::int AS mapped
            FROM sources s
            LEFT JOIN categories c ON c.source_id = s.id
            LEFT JOIN mappings m ON m.category_id = c.id
            GROUP BY s.id
            ORDER BY s.id
        """)

        return {
            "total_sources": sources,
            "total_categories": cats,
            "total_mapped": mapped,
            "total_threats": threats,
            "source_breakdown": [dict(r) for r in src_rows],
            "dim_source_distribution": dict(source_dist),
            "dim_mech_distribution": dict(mech_dist),
            "dim_target_distribution": dict(target_dist),
            "confidence_distribution": dict(conf_dist),
        }
