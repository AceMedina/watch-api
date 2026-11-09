from fastapi import FastAPI, HTTPException, Header, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Optional, Literal
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Database Connection
load_dotenv()

def get_db_connection():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise HTTPException(status_code=503, detail="Database configuration missing.")
    try:
        return psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    except psycopg2.OperationalError:
        raise HTTPException(status_code=503, detail="Database connection failed.")

# Configuration
VALID_API_KEYS = {
    "watch-api-001": "Watch Gallery",
    "chronicle-api-002": "Chronicle Game",
    "broke-oclock-003": "Broke O'Clock"
}

API_VERSION = "1.0"

app = FastAPI(
    title="Simple Watch API",
    description="A beginner-friendly REST API containing information about watches.",
    version=API_VERSION
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Watch Data Models
class Watch(BaseModel):
    id: int
    brand: Literal["Rolex", "Omega", "Audemars Piguet", "Patek Philippe", "Richard Mille"]
    model: str = Field(min_length=1)
    nickname: str = Field(min_length=1)
    reference_number: str = Field(min_length=1)
    case_material: str = Field(min_length=1)
    case_size_mm: float = Field(gt=0)
    dial_color: str = Field(min_length=1)
    bezel_material: str = Field(min_length=1)
    movement_type: Literal["Automatic", "Manual-Wind"]
    movement: str = Field(min_length=1)
    power_reserve_hours: int = Field(gt=0)
    water_resistance_m: int = Field(gt=0)
    year: int = Field(ge=1900, le=2026)
    origin: Literal["Switzerland"]
    category: Literal["Diver", "Chronograph", "Sports", "Dress", "Pilot", "Field", "GMT"]
    price_php: int = Field(gt=0)
    image: str = Field(min_length=1)
    description: str = Field(min_length=1)

class WatchCreate(BaseModel):
    brand: Literal["Rolex", "Omega", "Audemars Piguet", "Patek Philippe", "Richard Mille"]
    model: str = Field(min_length=1)
    nickname: str = Field(min_length=1)
    reference_number: str = Field(min_length=1)
    case_material: str = Field(min_length=1)
    case_size_mm: float = Field(gt=0)
    dial_color: str = Field(min_length=1)
    bezel_material: str = Field(min_length=1)
    movement_type: Literal["Automatic", "Manual-Wind"]
    movement: str = Field(min_length=1)
    power_reserve_hours: int = Field(gt=0)
    water_resistance_m: int = Field(gt=0)
    year: int = Field(ge=1900, le=2026)
    origin: Literal["Switzerland"]
    category: Literal["Diver", "Chronograph", "Sports", "Dress", "Pilot", "Field", "GMT"]
    price_php: int = Field(gt=0)
    image: str = Field(min_length=1)
    description: str = Field(min_length=1)

class WatchUpdate(BaseModel):
    brand: Optional[Literal["Rolex", "Omega", "Audemars Piguet", "Patek Philippe", "Richard Mille"]] = None
    model: Optional[str] = Field(default=None, min_length=1)
    nickname: Optional[str] = Field(default=None, min_length=1)
    reference_number: Optional[str] = Field(default=None, min_length=1)
    case_material: Optional[str] = Field(default=None, min_length=1)
    case_size_mm: Optional[float] = Field(default=None, gt=0)
    dial_color: Optional[str] = Field(default=None, min_length=1)
    bezel_material: Optional[str] = Field(default=None, min_length=1)
    movement_type: Optional[Literal["Automatic", "Manual-Wind"]] = None
    movement: Optional[str] = Field(default=None, min_length=1)
    power_reserve_hours: Optional[int] = Field(default=None, gt=0)
    water_resistance_m: Optional[int] = Field(default=None, gt=0)
    year: Optional[int] = Field(default=None, ge=1900, le=2026)
    origin: Optional[Literal["Switzerland"]] = None
    category: Optional[Literal["Diver", "Chronograph", "Sports", "Dress", "Pilot", "Field", "GMT"]] = None
    price_php: Optional[int] = Field(default=None, gt=0)
    image: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = Field(default=None, min_length=1)

# Authentication
def verify_api_key(x_api_key: Optional[str] = Header(default=None)):
    if not x_api_key or x_api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key."
        )
    return True

# Public Routes
@app.get("/")
def home():
    return {
        "message": "Welcome to the Watch Gallery API!",
        "version": API_VERSION,
        "endpoints": [
            "/health",
            "/api/v1/watches",
            "/api/v1/watches/{id}",
            "/api/v1/watches/search"
        ]
    }

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "Simple Watch API",
        "version": API_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }

# Protected Routes - Read and Search
@app.get("/api/v1/watches", dependencies=[Depends(verify_api_key)])
def get_watches():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM watches ORDER BY id ASC;")
            rows = cur.fetchall()
        return {"count": len(rows), "watches": rows}
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()

@app.get("/api/v1/watches/search", dependencies=[Depends(verify_api_key)])
def search_watches(q: str = Query(..., min_length=1)):
    pattern = f"%{q.strip()}%"
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM watches
                WHERE CAST(id AS TEXT) ILIKE %s
                   OR brand ILIKE %s
                   OR model ILIKE %s
                   OR nickname ILIKE %s
                   OR reference_number ILIKE %s
                   OR case_material ILIKE %s
                   OR dial_color ILIKE %s
                   OR category ILIKE %s
                   OR origin ILIKE %s
                ORDER BY id ASC;
                """,
                (pattern,) * 9
            )
            results = cur.fetchall()
        return {"query": q, "count": len(results), "results": results}
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()

@app.get("/api/v1/watches/{watch_id}", response_model=Watch, dependencies=[Depends(verify_api_key)])
def get_watch(watch_id: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM watches WHERE id = %s;", (watch_id,))
            watch = cur.fetchone()
        if not watch:
            raise HTTPException(status_code=404, detail="Watch not found.")
        return watch
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()

# Protected Routes - Create
@app.post("/api/v1/watches", response_model=Watch, status_code=201, dependencies=[Depends(verify_api_key)])
def create_watch(watch: WatchCreate):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO watches (
                    brand, model, nickname, reference_number, case_material,
                    case_size_mm, dial_color, bezel_material, movement_type,
                    movement, power_reserve_hours, water_resistance_m, year,
                    origin, category, price_php, image, description
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING *;
                """,
                (
                    watch.brand, watch.model, watch.nickname, watch.reference_number,
                    watch.case_material, watch.case_size_mm, watch.dial_color,
                    watch.bezel_material, watch.movement_type, watch.movement,
                    watch.power_reserve_hours, watch.water_resistance_m, watch.year,
                    watch.origin, watch.category, watch.price_php, watch.image,
                    watch.description
                )
            )
            new_watch = cur.fetchone()
        conn.commit()
        return new_watch
    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=409, detail="Duplicate or invalid record.")
    except psycopg2.Error:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()

# Protected Routes - Update
@app.patch("/api/v1/watches/{watch_id}", response_model=Watch, dependencies=[Depends(verify_api_key)])
def update_watch(watch_id: int, watch: WatchUpdate):
    updates = watch.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update.")

    set_clause = ", ".join(f"{col} = %s" for col in updates.keys())
    values = list(updates.values()) + [watch_id]

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE watches SET {set_clause} WHERE id = %s RETURNING *;",
                values
            )
            updated_watch = cur.fetchone()
        if not updated_watch:
            raise HTTPException(status_code=404, detail="Watch not found.")
        conn.commit()
        return updated_watch
    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=409, detail="Duplicate or invalid record.")
    except psycopg2.Error:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()

# Protected Routes - Delete
@app.delete("/api/v1/watches/{watch_id}", dependencies=[Depends(verify_api_key)])
def delete_watch(watch_id: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM watches WHERE id = %s RETURNING id;", (watch_id,))
            deleted = cur.fetchone()
        if not deleted:
            raise HTTPException(status_code=404, detail="Watch not found.")
        conn.commit()
        return {"message": f"Watch {watch_id} deleted successfully."}
    except psycopg2.Error:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()