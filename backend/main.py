from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.schemas import CompareResponse, OptimizeRequest
from backend.service import compare_housekeeping_algorithms


app = FastAPI(
    title="Hotel Ops Optimizer API",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(
    "/compare",
    response_model=CompareResponse,
)
def compare(
    request: OptimizeRequest,
) -> CompareResponse:
    try:
        return compare_housekeeping_algorithms(request)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error