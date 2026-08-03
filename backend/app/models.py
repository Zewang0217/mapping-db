from datetime import datetime

from pydantic import BaseModel


# ── Source ──────────────────────────────────────────────

class SourceCreate(BaseModel):
    name: str
    source_type: str  # scanner | paper | report
    url: str | None = None
    notes: str | None = None


class SourceUpdate(BaseModel):
    name: str | None = None
    source_type: str | None = None
    url: str | None = None
    status: str | None = None
    notes: str | None = None


class SourceResponse(BaseModel):
    id: int
    name: str
    source_type: str
    url: str | None
    category_count: int
    status: str
    notes: str | None
    created_at: datetime


# ── Category ────────────────────────────────────────────

class CategoryCreate(BaseModel):
    original_name: str
    description: str | None = None
    is_threat: bool = True


class CategoryUpdate(BaseModel):
    original_name: str | None = None
    description: str | None = None
    is_threat: bool | None = None
    status: str | None = None


class CategoryResponse(BaseModel):
    id: int
    source_id: int
    original_name: str
    description: str | None
    is_threat: bool
    status: str


# ── Mapping ─────────────────────────────────────────────

class MappingUpdate(BaseModel):
    source_dim: list[str] | None = None
    mech_dim: list[str] | None = None
    target_dim: list[str] | None = None
    vuln_tags: list[str] | None = None
    carrier_tags: list[str] | None = None
    confidence: str | None = None
    evidence: str | None = None
    notes: str | None = None


class MappingResponse(BaseModel):
    id: int
    category_id: int
    source_dim: list[str] | None
    mech_dim: list[str] | None
    target_dim: list[str] | None
    vuln_tags: list[str]
    carrier_tags: list[str]
    confidence: str | None
    evidence: str | None
    notes: str | None


# ── Dimension Value ─────────────────────────────────────

class DimValueCreate(BaseModel):
    dimension: str
    value_name: str
    definition: str | None = None
    examples: str | None = None
    counter_examples: str | None = None
    decision_rules: str | None = None
    literature_ref: str | None = None


class DimValueResponse(BaseModel):
    id: int
    dimension: str
    value_name: str
    definition: str | None
    examples: str | None
    counter_examples: str | None
    decision_rules: str | None
    literature_ref: str | None


# ── Stats ───────────────────────────────────────────────

class StatsResponse(BaseModel):
    total_sources: int
    total_categories: int
    total_mapped: int
    total_threats: int
    source_breakdown: list[dict]
    dim_source_distribution: dict[str, int]
    dim_mech_distribution: dict[str, int]
    dim_target_distribution: dict[str, int]
    confidence_distribution: dict[str, int]
