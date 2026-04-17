"""FastAPI routes for the EvidenceAI REST API.

Endpoints:
  POST /reviews          — Start a new systematic review job
  GET  /reviews          — List all reviews for the current user
  GET  /reviews/{id}     — Get a specific review result
  GET  /status/{job_id}  — Poll job status
  GET  /reviews/{id}/package — Download FDA evidence package
  POST /search           — Search the evidence base
  GET  /evidence/{query} — Quick evidence search (GET-friendly)
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from evidence_ai.api.deps import get_current_user, get_db, get_redis
from evidence_ai.api.schemas import (
    CoEScoresResponse,
    CreateReviewRequest,
    ErrorResponse,
    ReviewCreatedResponse,
    ReviewResultResponse,
    ReviewStatus,
    ReviewStatusResponse,
    SearchRequest,
    SearchResponse,
)
from evidence_ai.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Reviews ───────────────────────────────────────────────────────────────────

@router.post(
    "/reviews",
    response_model=ReviewCreatedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start a systematic review",
    description=(
        "Start a new AI-powered systematic review. The review is processed "
        "asynchronously. Poll `/status/{review_id}` for progress."
    ),
    tags=["reviews"],
)
async def create_review(
    request: CreateReviewRequest,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict, Depends(get_current_user)],
    redis: Annotated[Any, Depends(get_redis)],
) -> ReviewCreatedResponse:
    """Start a new systematic review job."""
    review_id = f"rev_{uuid.uuid4().hex[:8]}"

    # Estimate runtime (rough heuristic: ~1 min per 50 papers)
    estimated_minutes = max(5, request.max_results // 50)

    # TODO: Create DB record for the review
    # from evidence_ai.db.models import ReviewRecord
    # review_record = ReviewRecord(
    #     id=review_id,
    #     user_id=user["user_id"],
    #     question=request.question,
    #     status="queued",
    # )
    # db.add(review_record)
    # await db.flush()

    # Dispatch Celery task
    background_tasks.add_task(
        _run_review_task,
        review_id=review_id,
        request=request,
        user_id=user["user_id"],
    )

    logger.info("Review %s queued by user %s", review_id, user["user_id"])

    return ReviewCreatedResponse(
        review_id=review_id,
        status=ReviewStatus.QUEUED,
        estimated_minutes=estimated_minutes,
        job_url=f"{settings.api_prefix}/status/{review_id}",
    )


@router.get(
    "/reviews",
    summary="List systematic reviews",
    tags=["reviews"],
)
async def list_reviews(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict, Depends(get_current_user)],
    limit: int = 20,
    offset: int = 0,
) -> dict:
    """List all reviews for the current user."""
    # TODO: Query from DB
    # from sqlalchemy import select
    # from evidence_ai.db.models import ReviewRecord
    # result = await db.execute(
    #     select(ReviewRecord)
    #     .where(ReviewRecord.user_id == user["user_id"])
    #     .order_by(ReviewRecord.created_at.desc())
    #     .limit(limit)
    #     .offset(offset)
    # )
    # reviews = result.scalars().all()
    return {"reviews": [], "total": 0, "limit": limit, "offset": offset}


@router.get(
    "/reviews/{review_id}",
    response_model=ReviewResultResponse,
    summary="Get review result",
    tags=["reviews"],
)
async def get_review(
    review_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict, Depends(get_current_user)],
) -> ReviewResultResponse:
    """Get the result of a completed systematic review."""
    # TODO: Retrieve from DB
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Review {review_id} not found",
    )


@router.get(
    "/reviews/{review_id}/package",
    summary="Download FDA evidence package",
    tags=["reviews"],
    description=(
        "Download the FDA evidence package (eCTD format) for a completed review. "
        "Returns a ZIP file containing Module 2.5, 2.7.3, and 2.7.4 documents."
    ),
)
async def download_package(
    review_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict, Depends(get_current_user)],
) -> FileResponse:
    """Download the FDA evidence package as a ZIP file."""
    # TODO: Generate and return evidence package
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Review {review_id} not found or not yet complete",
    )


# ── Status ────────────────────────────────────────────────────────────────────

@router.get(
    "/status/{review_id}",
    response_model=ReviewStatusResponse,
    summary="Poll review status",
    tags=["status"],
)
async def get_status(
    review_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ReviewStatusResponse:
    """Poll the status of an in-progress systematic review."""
    # TODO: Retrieve from DB or Celery task status
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Review {review_id} not found",
    )


# ── Search ────────────────────────────────────────────────────────────────────

@router.post(
    "/search",
    response_model=SearchResponse,
    summary="Search evidence base",
    tags=["search"],
)
async def search_evidence(
    request: SearchRequest,
    user: Annotated[dict, Depends(get_current_user)],
    redis: Annotated[Any, Depends(get_redis)],
) -> SearchResponse:
    """Search the evidence base for relevant papers and evidence items."""
    # TODO: Implement vector similarity search over the evidence store
    # This requires:
    # 1. A vector database (pgvector or Pinecone)
    # 2. Embedding model (e.g. BioBERT-based sentence encoder)
    # 3. Pre-computed embeddings for all ingested abstracts

    return SearchResponse(
        query=request.query,
        total_results=0,
        results=[],
    )


@router.get(
    "/evidence",
    response_model=SearchResponse,
    summary="Quick evidence search",
    tags=["search"],
    description="GET-friendly evidence search. Use q= parameter.",
)
async def quick_search(
    q: str,
    limit: int = 20,
    user: Annotated[dict, Depends(get_current_user)] = None,  # type: ignore[assignment]
) -> SearchResponse:
    """Quick evidence search via GET request."""
    return SearchResponse(query=q, total_results=0, results=[])


# ── Background task ───────────────────────────────────────────────────────────

async def _run_review_task(
    review_id: str,
    request: CreateReviewRequest,
    user_id: str,
) -> None:
    """Background task to run the full evidence synthesis pipeline.

    In production, this would be dispatched to a Celery worker. For the
    simple FastAPI background task version, it runs in the same process.

    TODO: Dispatch to Celery:
        from evidence_ai.worker import run_review
        run_review.delay(review_id=review_id, request=request.model_dump())
    """
    logger.info("Running review %s for user %s", review_id, user_id)

    try:
        from evidence_ai import EvidenceAI

        client = EvidenceAI()
        review = await client.synthesize(
            question=request.question,
            databases=[db.value for db in request.databases],
            date_range=request.date_range.model_dump() if request.date_range else None,
            study_designs=[sd.value for sd in request.study_designs] if request.study_designs else None,
            max_papers=request.max_results,
            include_augmentation=request.include_augmentation,
        )

        logger.info(
            "Review %s completed. LoE=%.3f, direction=%s",
            review_id,
            review.level_of_evidence,
            review.effect_direction.value,
        )

        # TODO: Save review result to DB
        # await save_review_result(review_id, review)

    except Exception as e:  # noqa: BLE001
        logger.exception("Review %s failed: %s", review_id, e)
        # TODO: Update DB record with error status
