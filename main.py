import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import SQLModel

from app.agents.business_analyst import ask_business_analyst
from app.databases.db import engine


logger = logging.getLogger(__name__)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info(
        "Initializing database tables..."
    )

    create_db_and_tables()

    yield

    logger.info(
        "Application shutdown."
    )


app = FastAPI(
    title="AI Business Analyst",
    description=(
        "AI-powered business analysis system "
        "combining structured CRM data and RAG."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


class GeminiRequest(BaseModel):

    query: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Business question for the AI analyst.",
    )


@app.get("/health")
async def health():

    return {
        "status": "ok",
        "service": "ai-business-analyst",
    }


@app.post("/gemini")
async def chat(req: GeminiRequest):

    query = req.query.strip()

    try:

        result = await ask_business_analyst(
            query
        )

        return {
            "query": query,
            "result": result,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:

        logger.exception(
            "Business analyst request failed."
        )

        raise HTTPException(
            status_code=500,
            detail="Business analysis request failed.",
        )