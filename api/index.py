from fastapi import FastAPI, HTTPException, Header, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone, date, timedelta
from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field
from typing import Optional, Literal
import os
import bcrypt
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
raw_keys = os.getenv("VALID_API_KEYS", "")
VALID_API_KEYS = {key.strip() for key in raw_keys.split(",") if key.strip()}

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
    origin: Literal["Switzerland", "Germany", "France", "United Kingdom", "Japan", "Italy"]
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
    origin: Literal["Switzerland", "Germany", "France", "United Kingdom", "Japan", "Italy"]
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
    origin: Optional[Literal["Switzerland", "Germany", "France", "United Kingdom", "Japan", "Italy"]] = None
    category: Optional[Literal["Diver", "Chronograph", "Sports", "Dress", "Pilot", "Field", "GMT"]] = None
    price_php: Optional[int] = Field(default=None, gt=0)
    image: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = Field(default=None, min_length=1)

# User, Favorite & Review Data Models
class UserAuth(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=4, max_length=72)

class FavoriteCreate(BaseModel):
    user_id: int
    watch_id: int

class ReviewCreate(BaseModel):
    user_id: int
    rating: int = Field(ge=1, le=5)
    comment: str = Field(min_length=1, max_length=300)

# Authentication & Role Verification
def verify_api_key(x_api_key: Optional[str] = Header(default=None)):
    if not x_api_key or x_api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key."
        )
    return True

def verify_admin(
    x_api_key: bool = Depends(verify_api_key),
    x_user_id: Optional[int] = Header(default=None)
):
    if not x_user_id:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required (missing x-user-id)."
        )
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, username, role FROM users WHERE id = %s;", (x_user_id,))
            admin_user = cur.fetchone()
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()

    if not admin_user or admin_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required."
        )
    return admin_user

# Audit Log Helper
def log_activity(cur, action: str, details: str, user_id: Optional[int] = None, watch_id: Optional[int] = None):
    cur.execute(
        """
        INSERT INTO audit_logs (user_id, watch_id, action, details)
        VALUES (%s, %s, %s, %s);
        """,
        (user_id, watch_id, action, details)
    )

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
            "/api/v1/watches/search",
            "/api/v1/auth/register",
            "/api/v1/auth/login",
            "/api/v1/users/{user_id}/favorites",
            "/api/v1/favorites",
            "/api/v1/watches/{watch_id}/reviews",
            "/api/v1/audit-logs",
            "/api/v1/chronicle/daily",
            "/api/v1/chronicle/games",
            "/api/v1/chronicle/users/{user_id}/history",
            "/api/v1/chronicle/leaderboard",
            "/api/v1/broke-oclock/users/{user_id}/goals",
            "/api/v1/broke-oclock/goals",
            "/api/v1/broke-oclock/goals/{goal_id}/deposit",
            "/api/v1/broke-oclock/goals/{goal_id}"
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

# Admin Routes - Create
@app.post("/api/v1/watches", response_model=Watch, status_code=201)
def create_watch(watch: WatchCreate, admin_user: dict = Depends(verify_admin)):
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
            log_activity(
                cur,
                "CREATE_WATCH",
                f"Added {new_watch['brand']} {new_watch['model']}",
                user_id=admin_user["id"],
                watch_id=new_watch["id"]
            )
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

# Admin Routes - Update
@app.patch("/api/v1/watches/{watch_id}", response_model=Watch)
def update_watch(watch_id: int, watch: WatchUpdate, admin_user: dict = Depends(verify_admin)):
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
            log_activity(
                cur,
                "UPDATE_WATCH",
                f"Updated watch ID {watch_id}",
                user_id=admin_user["id"],
                watch_id=watch_id
            )
        conn.commit()
        return updated_watch
    except HTTPException:
        conn.rollback()
        raise
    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=409, detail="Duplicate or invalid record.")
    except psycopg2.Error:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()

# Admin Routes - Delete
@app.delete("/api/v1/watches/{watch_id}")
def delete_watch(watch_id: int, admin_user: dict = Depends(verify_admin)):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM watches WHERE id = %s RETURNING id, brand, model;",
                (watch_id,)
            )
            deleted = cur.fetchone()
            if not deleted:
                raise HTTPException(status_code=404, detail="Watch not found.")
            log_activity(
                cur,
                "DELETE_WATCH",
                f"Deleted {deleted['brand']} {deleted['model']} (ID {watch_id})",
                user_id=admin_user["id"],
                watch_id=None
            )
        conn.commit()
        return {"message": f"Watch {watch_id} deleted successfully."}
    except HTTPException:
        conn.rollback()
        raise
    except psycopg2.Error:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()

# Protected Routes - User Authentication
@app.post("/api/v1/auth/register", status_code=201, dependencies=[Depends(verify_api_key)])
def register_user(user: UserAuth):
    clean_username = user.username.strip()
    hashed_pw = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (username, password_hash)
                VALUES (%s, %s)
                RETURNING id, username, role, created_at;
                """,
                (clean_username, hashed_pw)
            )
            new_user = cur.fetchone()
            log_activity(cur, "REGISTER", f"User '{clean_username}' registered", user_id=new_user["id"])
        conn.commit()
        return {"message": "Account created successfully.", "user": new_user}
    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=409, detail="Username already exists.")
    except psycopg2.Error:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()

@app.post("/api/v1/auth/login", dependencies=[Depends(verify_api_key)])
def login_user(user: UserAuth):
    clean_username = user.username.strip()

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, password_hash, role FROM users WHERE username = %s;",
                (clean_username,)
            )
            db_user = cur.fetchone()
            if not db_user or not bcrypt.checkpw(user.password.encode("utf-8"), db_user["password_hash"].encode("utf-8")):
                raise HTTPException(status_code=401, detail="Invalid username or password.")
            log_activity(cur, "LOGIN", f"User '{clean_username}' signed in", user_id=db_user["id"])
        conn.commit()
    except HTTPException:
        raise
    except psycopg2.Error:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()

    return {
        "message": "Login successful.",
        "user": {
            "id": db_user["id"],
            "username": db_user["username"],
            "role": db_user["role"]
        }
    }

# Protected Routes - User Favorites (Many-to-Many JOIN)
@app.get("/api/v1/users/{user_id}/favorites", dependencies=[Depends(verify_api_key)])
def get_user_favorites(user_id: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT w.*, uf.created_at AS favorited_at
                FROM user_favorites uf
                INNER JOIN watches w ON uf.watch_id = w.id
                WHERE uf.user_id = %s
                ORDER BY uf.created_at DESC;
                """,
                (user_id,)
            )
            favorites = cur.fetchall()
        return {"user_id": user_id, "count": len(favorites), "favorites": favorites}
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()

@app.post("/api/v1/favorites", status_code=201, dependencies=[Depends(verify_api_key)])
def add_favorite(fav: FavoriteCreate):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO user_favorites (user_id, watch_id)
                VALUES (%s, %s)
                ON CONFLICT (user_id, watch_id) DO NOTHING
                RETURNING id, user_id, watch_id, created_at;
                """,
                (fav.user_id, fav.watch_id)
            )
            created = cur.fetchone()
            if created:
                log_activity(cur, "ADD_FAVORITE", f"Favorited watch ID {fav.watch_id}", user_id=fav.user_id, watch_id=fav.watch_id)
        conn.commit()
        return {"message": "Added to favorites.", "favorite": created}
    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=404, detail="User or watch not found.")
    except psycopg2.Error:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()

@app.delete("/api/v1/favorites/{user_id}/{watch_id}", dependencies=[Depends(verify_api_key)])
def remove_favorite(user_id: int, watch_id: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM user_favorites WHERE user_id = %s AND watch_id = %s RETURNING id;",
                (user_id, watch_id)
            )
            deleted = cur.fetchone()
            if not deleted:
                raise HTTPException(status_code=404, detail="Favorite not found.")
            log_activity(cur, "REMOVE_FAVORITE", f"Removed favorite watch ID {watch_id}", user_id=user_id, watch_id=watch_id)
        conn.commit()
        return {"message": "Removed from favorites."}
    except HTTPException:
        conn.rollback()
        raise
    except psycopg2.Error:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()

# Protected Routes - Watch Reviews (One-to-Many JOIN)
@app.get("/api/v1/watches/{watch_id}/reviews", dependencies=[Depends(verify_api_key)])
def get_watch_reviews(watch_id: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT r.id, r.watch_id, r.user_id, u.username, r.rating, r.comment, r.created_at
                FROM watch_reviews r
                INNER JOIN users u ON r.user_id = u.id
                WHERE r.watch_id = %s
                ORDER BY r.created_at DESC;
                """,
                (watch_id,)
            )
            reviews = cur.fetchall()
        avg_rating = round(sum(r["rating"] for r in reviews) / len(reviews), 1) if reviews else 0
        return {"watch_id": watch_id, "count": len(reviews), "average_rating": avg_rating, "reviews": reviews}
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()

@app.post("/api/v1/watches/{watch_id}/reviews", status_code=201, dependencies=[Depends(verify_api_key)])
def upsert_watch_review(watch_id: int, review: ReviewCreate):
    clean_comment = review.comment.strip()
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO watch_reviews (user_id, watch_id, rating, comment)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id, watch_id)
                DO UPDATE SET rating = EXCLUDED.rating, comment = EXCLUDED.comment, created_at = NOW()
                RETURNING id, user_id, watch_id, rating, comment, created_at;
                """,
                (review.user_id, watch_id, review.rating, clean_comment)
            )
            saved_review = cur.fetchone()
            log_activity(cur, "REVIEW_WATCH", f"Rated watch ID {watch_id} ({review.rating}/5)", user_id=review.user_id, watch_id=watch_id)
        conn.commit()
        return {"message": "Review saved.", "review": saved_review}
    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=404, detail="User or watch not found.")
    except psycopg2.Error:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()

@app.delete("/api/v1/reviews/{review_id}", dependencies=[Depends(verify_api_key)])
def delete_watch_review(
    review_id: int,
    x_user_id: Optional[int] = Header(default=None)
):
    if not x_user_id:
        raise HTTPException(status_code=403, detail="Authentication required (missing x-user-id).")

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, username, role FROM users WHERE id = %s;", (x_user_id,))
            requester = cur.fetchone()
            if not requester:
                raise HTTPException(status_code=403, detail="User not found.")

            cur.execute("SELECT id, watch_id, user_id FROM watch_reviews WHERE id = %s;", (review_id,))
            review = cur.fetchone()
            if not review:
                raise HTTPException(status_code=404, detail="Review not found.")

            if requester["role"] != "admin" and review["user_id"] != requester["id"]:
                raise HTTPException(status_code=403, detail="You can only delete your own reviews.")

            cur.execute("DELETE FROM watch_reviews WHERE id = %s;", (review_id,))
            log_activity(
                cur,
                "DELETE_REVIEW",
                f"Deleted review ID {review_id} on watch ID {review['watch_id']}",
                user_id=requester["id"],
                watch_id=review["watch_id"]
            )
        conn.commit()
        return {"message": f"Review {review_id} deleted successfully."}
    except HTTPException:
        conn.rollback()
        raise
    except psycopg2.Error:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()

# Admin Routes - Audit Logs (Multi-Table LEFT JOIN)
@app.get("/api/v1/audit-logs")
def get_audit_logs(
    limit: int = Query(default=30, ge=1, le=100),
    admin_user: dict = Depends(verify_admin)
):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT a.id, a.action, a.details, a.created_at,
                       u.username,
                       w.brand AS watch_brand, w.model AS watch_model
                FROM audit_logs a
                LEFT JOIN users u ON a.user_id = u.id
                LEFT JOIN watches w ON a.watch_id = w.id
                ORDER BY a.created_at DESC
                LIMIT %s;
                """,
                (limit,)
            )
            logs = cur.fetchall()
        return {"count": len(logs), "logs": logs}
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()

# Chronicle Game Models & Helpers
MANILA_TZ = ZoneInfo("Asia/Manila")

class ChronicleGameCreate(BaseModel):
    user_id: int
    watch_id: int
    difficulty: Literal["easy", "medium", "hard"]
    game_mode: Literal["daily", "practice"]
    won: bool
    guesses_used: int = Field(ge=1, le=10)

def get_manila_today() -> date:
    return datetime.now(MANILA_TZ).date()

def calculate_chronicle_points(
    difficulty: str,
    game_mode: str,
    won: bool,
    guesses_used: int,
    new_streak: int
) -> tuple[int, int, int]:
    rules = {
        "easy": {"max": 10, "base": 50, "per_unused": 5},
        "medium": {"max": 8, "base": 80, "per_unused": 8},
        "hard": {"max": 6, "base": 120, "per_unused": 12},
    }
    cfg = rules[difficulty]
    max_guesses = cfg["max"]

    if not won:
        return 0, max_guesses, 0

    unused = max(0, max_guesses - guesses_used)
    points = cfg["base"] + (unused * cfg["per_unused"])

    # Daily Challenge boost (+25 pts) & Daily-only consecutive calendar day streak boost (+5 pts per streak starting at 2 wins, max +50 pts)
    streak_bonus = 0
    if game_mode == "daily":
        points += 25
        streak_bonus = min(50, max(0, (new_streak - 1) * 5))
        points += streak_bonus

    return points, max_guesses, streak_bonus

def ensure_daily_watch(cur, target_date: date):
    cur.execute(
        """
        SELECT cd.puzzle_date, w.*
        FROM chronicle_daily cd
        INNER JOIN watches w ON cd.watch_id = w.id
        WHERE cd.puzzle_date = %s;
        """,
        (target_date,)
    )
    existing = cur.fetchone()
    if existing:
        return existing

    # Pick a watch not used in the last 14 days
    cur.execute(
        """
        SELECT id FROM watches
        WHERE id NOT IN (
            SELECT watch_id FROM chronicle_daily
            WHERE puzzle_date >= %s
        )
        ORDER BY RANDOM()
        LIMIT 1;
        """,
        (target_date - timedelta(days=14),)
    )
    picked = cur.fetchone()
    if not picked:
        cur.execute("SELECT id FROM watches ORDER BY RANDOM() LIMIT 1;")
        picked = cur.fetchone()

    if not picked:
        raise HTTPException(status_code=404, detail="No watches available in catalog.")

    cur.execute(
        """
        INSERT INTO chronicle_daily (puzzle_date, watch_id)
        VALUES (%s, %s)
        ON CONFLICT (puzzle_date) DO NOTHING;
        """,
        (target_date, picked["id"])
    )
    cur.execute(
        """
        SELECT cd.puzzle_date, w.*
        FROM chronicle_daily cd
        INNER JOIN watches w ON cd.watch_id = w.id
        WHERE cd.puzzle_date = %s;
        """,
        (target_date,)
    )
    return cur.fetchone()

# Chronicle Routes - Today's Daily Puzzle
@app.get("/api/v1/chronicle/daily", dependencies=[Depends(verify_api_key)])
def get_chronicle_daily(user_id: Optional[int] = Query(default=None)):
    today = get_manila_today()
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            daily_row = ensure_daily_watch(cur, today)
            user_attempt = None
            if user_id:
                cur.execute(
                    """
                    SELECT id, difficulty, won, guesses_used, max_guesses, streak_count, points_earned, played_at
                    FROM chronicle_games
                    WHERE user_id = %s AND game_mode = 'daily' AND puzzle_date = %s;
                    """,
                    (user_id, today)
                )
                user_attempt = cur.fetchone()
        conn.commit()

        watch_data = dict(daily_row)
        watch_data.pop("puzzle_date", None)
        return {
            "puzzle_date": today.isoformat(),
            "already_played": user_attempt is not None,
            "attempt": user_attempt,
            "watch": watch_data
        }
    except HTTPException:
        conn.rollback()
        raise
    except psycopg2.Error:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()

# Chronicle Routes - Save Game & Match History
@app.post("/api/v1/chronicle/games", status_code=201, dependencies=[Depends(verify_api_key)])
def record_chronicle_game(game: ChronicleGameCreate):
    today = get_manila_today()
    yesterday = today - timedelta(days=1)
    effective_date = today if game.game_mode == "daily" else None

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            if game.game_mode == "daily":
                cur.execute(
                    """
                    SELECT id FROM chronicle_games
                    WHERE user_id = %s AND game_mode = 'daily' AND puzzle_date = %s;
                    """,
                    (game.user_id, today)
                )
                if cur.fetchone():
                    raise HTTPException(status_code=409, detail="You already completed today's daily puzzle.")

                # Compute strict consecutive Manila calendar-day Daily streak
                if game.won:
                    cur.execute(
                        """
                        SELECT won, streak_count, COALESCE(puzzle_date, (played_at AT TIME ZONE 'Asia/Manila')::date) AS play_date
                        FROM chronicle_games
                        WHERE user_id = %s AND game_mode = 'daily'
                        ORDER BY id DESC
                        LIMIT 1;
                        """,
                        (game.user_id,)
                    )
                    last_daily = cur.fetchone()
                    if last_daily and last_daily["won"] and last_daily["play_date"] == yesterday:
                        new_streak = (last_daily["streak_count"] or 0) + 1
                    else:
                        new_streak = 1
                else:
                    new_streak = 0
            else:
                # Classic ("practice") rounds do not affect or earn Daily streaks
                new_streak = 0

            points_earned, max_guesses, streak_bonus = calculate_chronicle_points(
                game.difficulty,
                game.game_mode,
                game.won,
                game.guesses_used,
                new_streak
            )

            cur.execute(
                """
                INSERT INTO chronicle_games (
                    user_id, watch_id, difficulty, game_mode, puzzle_date,
                    won, guesses_used, max_guesses, streak_count, points_earned
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *;
                """,
                (
                    game.user_id, game.watch_id, game.difficulty, game.game_mode,
                    effective_date, game.won, game.guesses_used, max_guesses,
                    new_streak, points_earned
                )
            )
            saved = cur.fetchone()
            outcome_label = "Won" if game.won else "Lost"
            log_activity(
                cur,
                "CHRONICLE_GAME",
                f"{outcome_label} {game.game_mode} ({game.difficulty}) in {game.guesses_used}/{max_guesses} (+{points_earned} pts)",
                user_id=game.user_id,
                watch_id=game.watch_id
            )
        conn.commit()
        return {
            "message": "Game saved.",
            "streak_bonus": streak_bonus,
            "game": saved
        }
    except HTTPException:
        conn.rollback()
        raise
    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=409, detail="Duplicate daily entry or invalid user/watch.")
    except psycopg2.Error:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()

@app.get("/api/v1/chronicle/users/{user_id}/history", dependencies=[Depends(verify_api_key)])
def get_chronicle_history(
    user_id: int,
    limit: int = Query(default=25, ge=1, le=100)
):
    today = get_manila_today()
    yesterday = today - timedelta(days=1)
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT g.id, g.difficulty, g.game_mode, g.puzzle_date, g.won,
                       g.guesses_used, g.max_guesses, g.streak_count, g.points_earned, g.played_at,
                       w.brand, w.model, w.nickname, w.image
                FROM chronicle_games g
                INNER JOIN watches w ON g.watch_id = w.id
                WHERE g.user_id = %s
                ORDER BY g.id DESC
                LIMIT %s;
                """,
                (user_id, limit)
            )
            games = cur.fetchall()

            cur.execute(
                """
                SELECT COUNT(*) AS total_games,
                       COALESCE(SUM(CASE WHEN won THEN 1 ELSE 0 END), 0) AS wins,
                       COALESCE(SUM(points_earned), 0) AS total_points,
                       COALESCE(MAX(CASE WHEN game_mode = 'daily' THEN streak_count ELSE 0 END), 0) AS best_streak,
                       ROUND(AVG(CASE WHEN won THEN guesses_used END), 1) AS avg_guesses
                FROM chronicle_games
                WHERE user_id = %s;
                """,
                (user_id,)
            )
            stats = cur.fetchone()

            cur.execute(
                """
                SELECT won, streak_count, COALESCE(puzzle_date, (played_at AT TIME ZONE 'Asia/Manila')::date) AS play_date
                FROM chronicle_games
                WHERE user_id = %s AND game_mode = 'daily'
                ORDER BY id DESC
                LIMIT 1;
                """,
                (user_id,)
            )
            latest_daily = cur.fetchone()
            if (
                latest_daily
                and latest_daily["won"]
                and latest_daily["play_date"] in (today, yesterday)
            ):
                stats["current_streak"] = latest_daily["streak_count"]
            else:
                stats["current_streak"] = 0

        return {"stats": stats, "history": games}
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()

# Chronicle Routes - Strategic Global Leaderboard
@app.get("/api/v1/chronicle/leaderboard", dependencies=[Depends(verify_api_key)])
def get_chronicle_leaderboard(
    scope: Literal["all", "today"] = Query(default="all"),
    difficulty: Literal["all", "easy", "medium", "hard"] = Query(default="all"),
    limit: int = Query(default=20, ge=1, le=50)
):
    today = get_manila_today()
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            if scope == "today":
                query = """
                    SELECT u.id AS user_id,
                           u.username,
                           g.difficulty,
                           g.guesses_used,
                           g.max_guesses,
                           g.streak_count,
                           g.points_earned AS total_points,
                           1 AS wins,
                           1 AS games_played,
                           100.0 AS win_rate,
                           g.guesses_used::numeric AS avg_guesses
                    FROM chronicle_games g
                    INNER JOIN users u ON g.user_id = u.id
                    WHERE g.game_mode = 'daily'
                      AND g.puzzle_date = %s
                      AND g.won = TRUE
                """
                params = [today]
                if difficulty != "all":
                    query += " AND g.difficulty = %s"
                    params.append(difficulty)
                query += """
                    ORDER BY g.points_earned DESC, g.guesses_used ASC, g.played_at ASC
                    LIMIT %s;
                """
                params.append(limit)
                cur.execute(query, tuple(params))
                leaders = cur.fetchall()
            else:
                query = """
                    SELECT u.id AS user_id,
                           u.username,
                           COALESCE(SUM(g.points_earned), 0) AS total_points,
                           COUNT(g.id) AS games_played,
                           COALESCE(SUM(CASE WHEN g.won THEN 1 ELSE 0 END), 0) AS wins,
                           COALESCE(MAX(CASE WHEN g.game_mode = 'daily' THEN g.streak_count ELSE 0 END), 0) AS best_streak,
                           ROUND(
                               COALESCE(SUM(CASE WHEN g.won THEN 1 ELSE 0 END), 0)::numeric
                               / NULLIF(COUNT(g.id), 0) * 100, 1
                           ) AS win_rate,
                           ROUND(AVG(CASE WHEN g.won THEN g.guesses_used END), 1) AS avg_guesses
                    FROM users u
                    INNER JOIN chronicle_games g ON u.id = g.user_id
                    WHERE 1=1
                """
                params = []
                if difficulty != "all":
                    query += " AND g.difficulty = %s"
                    params.append(difficulty)
                query += """
                    GROUP BY u.id, u.username
                    HAVING COALESCE(SUM(g.points_earned), 0) > 0
                    ORDER BY total_points DESC, win_rate DESC, avg_guesses ASC
                    LIMIT %s;
                """
                params.append(limit)
                cur.execute(query, tuple(params))
                leaders = cur.fetchall()

        return {"scope": scope, "difficulty": difficulty, "today": today.isoformat(), "leaderboard": leaders}
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()

# Broke O'Clock Goal Models
class BrokeOClockGoalCreate(BaseModel):
    user_id: int
    watch_id: int
    monthly_salary: float = Field(gt=0)
    savings_rate: int = Field(ge=5, le=100)
    verdict: Optional[str] = Field(default=None, max_length=50)

class BrokeOClockDeposit(BaseModel):
    user_id: int
    amount: Optional[float] = Field(default=None, gt=0)

# Broke O'Clock Routes - Grail Goals
@app.get("/api/v1/broke-oclock/users/{user_id}/goals", dependencies=[Depends(verify_api_key)])
def get_user_goals(user_id: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT g.id, g.user_id, g.watch_id, g.monthly_salary, g.savings_rate,
                       g.amount_saved, g.verdict, g.created_at,
                       w.brand, w.model, w.nickname, w.price_php, w.image
                FROM broke_oclock_goals g
                INNER JOIN watches w ON g.watch_id = w.id
                WHERE g.user_id = %s
                ORDER BY g.created_at DESC;
                """,
                (user_id,)
            )
            goals = cur.fetchall()
        return {"user_id": user_id, "count": len(goals), "goals": goals}
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()

@app.post("/api/v1/broke-oclock/goals", status_code=201, dependencies=[Depends(verify_api_key)])
def create_user_goal(goal: BrokeOClockGoalCreate):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO broke_oclock_goals (user_id, watch_id, monthly_salary, savings_rate, verdict)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *;
                """,
                (goal.user_id, goal.watch_id, goal.monthly_salary, goal.savings_rate, goal.verdict)
            )
            created = cur.fetchone()
            log_activity(
                cur,
                "PIN_GRAIL_GOAL",
                f"Pinned grail goal for watch ID {goal.watch_id}",
                user_id=goal.user_id,
                watch_id=goal.watch_id
            )
        conn.commit()
        return {"message": "Grail goal pinned.", "goal": created}
    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=404, detail="User or watch not found.")
    except psycopg2.Error:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()

@app.patch("/api/v1/broke-oclock/goals/{goal_id}/deposit", dependencies=[Depends(verify_api_key)])
def deposit_goal_cutoff(goal_id: int, deposit: BrokeOClockDeposit):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT g.*, w.price_php
                FROM broke_oclock_goals g
                INNER JOIN watches w ON g.watch_id = w.id
                WHERE g.id = %s AND g.user_id = %s;
                """,
                (goal_id, deposit.user_id)
            )
            existing = cur.fetchone()
            if not existing:
                raise HTTPException(status_code=404, detail="Goal not found.")

            # Default 15/30 cutoff deposit is half of monthly watch savings allocation
            if deposit.amount is not None:
                increment = float(deposit.amount)
            else:
                monthly_alloc = float(existing["monthly_salary"]) * (int(existing["savings_rate"]) / 100.0)
                increment = round(monthly_alloc / 2.0, 2)

            new_saved = float(existing["amount_saved"]) + increment

            cur.execute(
                """
                UPDATE broke_oclock_goals
                SET amount_saved = %s
                WHERE id = %s
                RETURNING *;
                """,
                (new_saved, goal_id)
            )
            updated = cur.fetchone()
            log_activity(
                cur,
                "GOAL_DEPOSIT",
                f"Logged cutoff deposit (+PHP {increment:,.2f}) on goal ID {goal_id}",
                user_id=deposit.user_id,
                watch_id=existing["watch_id"]
            )
        conn.commit()
        return {"message": "Cutoff deposit logged.", "added": increment, "goal": updated}
    except HTTPException:
        conn.rollback()
        raise
    except psycopg2.Error:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()

@app.delete("/api/v1/broke-oclock/goals/{goal_id}", dependencies=[Depends(verify_api_key)])
def delete_user_goal(goal_id: int, user_id: int = Query(...)):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM broke_oclock_goals WHERE id = %s AND user_id = %s RETURNING id, watch_id;",
                (goal_id, user_id)
            )
            deleted = cur.fetchone()
            if not deleted:
                raise HTTPException(status_code=404, detail="Goal not found.")
            log_activity(
                cur,
                "DELETE_GRAIL_GOAL",
                f"Removed grail goal ID {goal_id}",
                user_id=user_id,
                watch_id=deleted["watch_id"]
            )
        conn.commit()
        return {"message": "Goal removed."}
    except HTTPException:
        conn.rollback()
        raise
    except psycopg2.Error:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        conn.close()