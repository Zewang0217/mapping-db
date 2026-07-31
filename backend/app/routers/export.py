import csv
import io

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.database import get_pool

router = APIRouter()

FIELDNAMES = [
    "source_name", "source_type", "original_name", "description", "is_threat",
    "source_dim", "mech_dim", "target_dim", "vuln_tags", "confidence",
    "evidence", "notes",
]


@router.get("/csv")
async def export_csv():
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT s.name AS source_name, s.source_type,
                   c.original_name, c.description, c.is_threat,
                   m.source_dim, m.mech_dim, m.target_dim,
                   m.vuln_tags, m.confidence, m.evidence, m.notes
            FROM mappings m
            JOIN categories c ON c.id = m.category_id
            JOIN sources s ON s.id = c.source_id
            ORDER BY s.id, c.id
        """)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=FIELDNAMES)
    writer.writeheader()
    for r in rows:
        d = dict(r)
        tags = d.get("vuln_tags", [])
        d["vuln_tags"] = ",".join(tags) if tags else ""
        writer.writerow(d)

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=mappings_export.csv"},
    )
