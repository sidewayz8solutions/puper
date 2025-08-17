"""
Puper Backend API - FastAPI Implementation
==========================================
State-of-the-art REST API for the Puper mobile application.
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Body, File, UploadFile, BackgroundTasks
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, func, Index
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError
import uuid
import os
from enum import Enum
import httpx
import asyncio
from redis import Redis
import json
import logging
from decimal import Decimal
import math

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://puper_user:puper_password@localhost:5432/puper")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
OSM_OVERPASS_URL = os.getenv("OSM_OVERPASS_URL", "https://overpass-api.de/api/interpreter")

# Additional configuration from environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
ENABLE_DOCS = os.getenv("ENABLE_DOCS", "true").lower() == "true"
DB_ECHO = os.getenv("DB_ECHO", "false").lower() == "true"
AUTO_RELOAD = os.getenv("AUTO_RELOAD", "true").lower() == "true"

# Cache TTL settings
CACHE_TTL_SHORT = int(os.getenv("CACHE_TTL_SHORT", "300"))
CACHE_TTL_MEDIUM = int(os.getenv("CACHE_TTL_MEDIUM", "1800"))
CACHE_TTL_LONG = int(os.getenv("CACHE_TTL_LONG", "86400"))

# Upload settings
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "5242880"))  # 5MB
ALLOWED_IMAGE_TYPES = os.getenv("ALLOWED_IMAGE_TYPES", "image/jpeg,image/png,image/webp").split(",")

# Search settings
DEFAULT_SEARCH_RADIUS = int(os.getenv("DEFAULT_SEARCH_RADIUS", "5000"))
MAX_SEARCH_RADIUS = int(os.getenv("MAX_SEARCH_RADIUS", "50000"))
DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", "50"))
MAX_PAGE_SIZE = int(os.getenv("MAX_PAGE_SIZE", "200"))

# Gamification points
POINTS_REVIEW = int(os.getenv("POINTS_REVIEW", "10"))
POINTS_RESTROOM_SUBMISSION = int(os.getenv("POINTS_RESTROOM_SUBMISSION", "20"))
POINTS_PHOTO_UPLOAD = int(os.getenv("POINTS_PHOTO_UPLOAD", "5"))
POINTS_HELPFUL_VOTE = int(os.getenv("POINTS_HELPFUL_VOTE", "2"))

# Admin settings
DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@puper.local")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
engine = create_engine(DATABASE_URL, echo=DB_ECHO)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup for caching
redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ========================= LIFESPAN EVENTS =========================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    logger.info("Starting Puper API...")

    # Create tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

    # Test Redis connection
    try:
        redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")

    # Create default admin user if it doesn't exist
    try:
        db = SessionLocal()
        admin_user = db.query(User).filter(User.username == DEFAULT_ADMIN_USERNAME).first()
        if not admin_user:
            admin_user = User(
                username=DEFAULT_ADMIN_USERNAME,
                email=DEFAULT_ADMIN_EMAIL,
                hashed_password=get_password_hash(DEFAULT_ADMIN_PASSWORD),
                role=UserRole.ADMIN,
                full_name="Default Admin",
                is_verified=True
            )
            db.add(admin_user)
            db.commit()
            logger.info(f"Created default admin user: {DEFAULT_ADMIN_USERNAME}")
        db.close()
    except Exception as e:
        logger.warning(f"Could not create default admin user: {e}")

    # Log configuration
    logger.info(f"Database URL: {DATABASE_URL.split('@')[0]}@***")  # Hide password
    logger.info(f"Redis URL: {REDIS_URL}")
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"Debug mode: {DEBUG}")
    logger.info(f"Docs enabled: {ENABLE_DOCS}")

    logger.info("Puper API started successfully!")

    yield  # Application runs here

    # Shutdown
    logger.info("Shutting down Puper API...")

    # Close database connections
    try:
        engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")

    logger.info("Puper API shutdown complete")

# FastAPI app
app = FastAPI(
    title="Puper API",
    description="The Waze of Public Restrooms - Find, rate, and review public toilets worldwide",
    version="1.0.0",
    debug=DEBUG,
    docs_url="/docs" if ENABLE_DOCS else None,
    redoc_url="/redoc" if ENABLE_DOCS else None,
    lifespan=lifespan
)

# CORS middleware
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ========================= ENUMS =========================

class RestroomSource(str, Enum):
    OSM = "osm"
    THIRD_PARTY = "third_party"
    CITY = "city"
    USER = "user"
    GOOGLE = "google"
    MERGED = "merged"

class AccessibilityLevel(str, Enum):
    FULL = "full"
    PARTIAL = "partial"
    NONE = "none"
    UNKNOWN = "unknown"

class UserRole(str, Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    PARTNER = "partner"

# ========================= DATABASE MODELS =========================

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default=UserRole.USER)
    points = Column(Integer, default=0)
    badges = Column(JSON, default=list)
    is_verified = Column(Boolean, default=False)
    is_anonymous = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviews = relationship("Review", back_populates="user")
    submitted_restrooms = relationship("Restroom", back_populates="submitter")
    favorites = relationship("Favorite", back_populates="user")

class Restroom(Base):
    __tablename__ = "restrooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(20), nullable=False, index=True)
    source_id = Column(String(100), index=True)
    name = Column(String(200))
    description = Column(String(500))
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    address = Column(String(300))
    city = Column(String(100), index=True)
    country = Column(String(100), index=True)

    # Attributes
    wheelchair_accessible = Column(String(20), default=AccessibilityLevel.UNKNOWN)
    gender_neutral = Column(Boolean)
    baby_changing = Column(Boolean)
    indoor = Column(Boolean, default=True)
    requires_fee = Column(Boolean, default=False)
    fee_amount = Column(Float)
    unisex = Column(Boolean)

    # Amenities
    has_soap = Column(Boolean)
    has_toilet_paper = Column(Boolean)
    has_hand_dryer = Column(Boolean)
    has_paper_towels = Column(Boolean)
    has_hot_water = Column(Boolean)
    has_mirror = Column(Boolean)

    # Ratings (cached aggregates)
    avg_cleanliness = Column(Float, default=0.0)
    avg_lighting = Column(Float, default=0.0)
    avg_safety = Column(Float, default=0.0)
    avg_privacy = Column(Float, default=0.0)
    avg_accessibility = Column(Float, default=0.0)
    avg_overall = Column(Float, default=0.0, index=True)
    review_count = Column(Integer, default=0, index=True)

    # Operating hours (JSON format)
    operating_hours = Column(JSON)

    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    temporarily_closed = Column(Boolean, default=False)
    permanently_closed = Column(Boolean, default=False)

    # Metadata
    submitter_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_verified_at = Column(DateTime)

    # Additional data
    extra_attributes = Column(JSON, default=dict)
    photos = Column(JSON, default=list)  # List of photo URLs

    # Relationships
    submitter = relationship("User", back_populates="submitted_restrooms")
    reviews = relationship("Review", back_populates="restroom", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="restroom", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="restroom", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_location_spatial', 'location', postgresql_using='gist'),
        Index('idx_avg_overall_active', 'avg_overall', 'is_active'),
        Index('idx_city_country', 'city', 'country'),
    )

class Review(Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    restroom_id = Column(UUID(as_uuid=True), ForeignKey('restrooms.id'), nullable=False)

    # Ratings (1-5 scale)
    cleanliness = Column(Integer, nullable=False)
    lighting = Column(Integer, nullable=False)
    safety = Column(Integer, nullable=False)
    privacy = Column(Integer, nullable=False)
    accessibility = Column(Integer, nullable=False)
    overall = Column(Integer, nullable=False)

    # Review content
    comment = Column(String(1000))
    photos = Column(JSON, default=list)  # List of photo URLs

    # Metadata
    is_verified = Column(Boolean, default=False)
    helpful_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="reviews")
    restroom = relationship("Restroom", back_populates="reviews")

    # Indexes
    __table_args__ = (
        Index('idx_restroom_created', 'restroom_id', 'created_at'),
        Index('idx_user_reviews', 'user_id', 'created_at'),
    )

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    restroom_id = Column(UUID(as_uuid=True), ForeignKey('restrooms.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="favorites")
    restroom = relationship("Restroom", back_populates="favorites")

    # Unique constraint
    __table_args__ = (
        Index('idx_user_restroom_unique', 'user_id', 'restroom_id', unique=True),
    )

class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restroom_id = Column(UUID(as_uuid=True), ForeignKey('restrooms.id'), nullable=False)
    reporter_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    report_type = Column(String(50), nullable=False)  # closed, out_of_order, incorrect_info, etc.
    description = Column(String(500))
    status = Column(String(20), default="pending")  # pending, verified, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)

    # Relationships
    restroom = relationship("Restroom", back_populates="reports")

# ========================= PYDANTIC SCHEMAS =========================

class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    is_anonymous: bool = False

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    role: str
    points: int
    badges: List[str]
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class RestroomBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    wheelchair_accessible: Optional[str] = AccessibilityLevel.UNKNOWN
    gender_neutral: Optional[bool] = None
    baby_changing: Optional[bool] = None
    indoor: Optional[bool] = True
    requires_fee: Optional[bool] = False
    fee_amount: Optional[float] = None
    unisex: Optional[bool] = None
    has_soap: Optional[bool] = None
    has_toilet_paper: Optional[bool] = None
    has_hand_dryer: Optional[bool] = None
    has_paper_towels: Optional[bool] = None
    has_hot_water: Optional[bool] = None
    has_mirror: Optional[bool] = None
    operating_hours: Optional[Dict[str, Any]] = None

class RestroomCreate(RestroomBase):
    source: str = RestroomSource.USER
    source_id: Optional[str] = None
    extra_attributes: Optional[Dict[str, Any]] = {}

class RestroomResponse(RestroomBase):
    id: str
    source: str
    avg_cleanliness: float
    avg_lighting: float
    avg_safety: float
    avg_privacy: float
    avg_accessibility: float
    avg_overall: float
    review_count: int
    is_active: bool
    is_verified: bool
    temporarily_closed: bool
    permanently_closed: bool
    created_at: datetime
    updated_at: datetime
    distance: Optional[float] = None  # Distance from search point
    detour_time: Optional[int] = None  # Detour time in seconds

    class Config:
        from_attributes = True

class ReviewBase(BaseModel):
    cleanliness: int = Field(..., ge=1, le=5)
    lighting: int = Field(..., ge=1, le=5)
    safety: int = Field(..., ge=1, le=5)
    privacy: int = Field(..., ge=1, le=5)
    accessibility: int = Field(..., ge=1, le=5)
    overall: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)

class ReviewCreate(ReviewBase):
    restroom_id: str

class ReviewResponse(ReviewBase):
    id: str
    user_id: str
    restroom_id: str
    username: Optional[str] = None
    is_verified: bool
    helpful_count: int
    created_at: datetime
    photos: List[str]

    class Config:
        from_attributes = True

class SearchParams(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    radius: float = Field(default=5000, ge=100, le=50000)  # meters
    min_rating: Optional[float] = Field(None, ge=1, le=5)
    wheelchair_accessible: Optional[bool] = None
    gender_neutral: Optional[bool] = None
    baby_changing: Optional[bool] = None
    free_only: Optional[bool] = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)

class RouteSearchParams(BaseModel):
    origin_lat: float = Field(..., ge=-90, le=90)
    origin_lon: float = Field(..., ge=-180, le=180)
    dest_lat: float = Field(..., ge=-90, le=90)
    dest_lon: float = Field(..., ge=-180, le=180)
    max_detour_minutes: int = Field(default=10, ge=1, le=30)
    min_rating: Optional[float] = Field(None, ge=1, le=5)
    wheelchair_accessible: Optional[bool] = None
    limit: int = Field(default=20, ge=1, le=50)

# ========================= AUTHENTICATION =========================

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(lambda: SessionLocal())):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ========================= GAMIFICATION SYSTEM =========================

class BadgeSystem:
    """Manages user badges and points"""

    BADGES = {
        "first_review": {"name": "First Steps", "points": 10, "description": "Posted your first review"},
        "explorer_10": {"name": "Explorer", "points": 50, "description": "Reviewed 10 different restrooms"},
        "explorer_50": {"name": "Master Explorer", "points": 200, "description": "Reviewed 50 different restrooms"},
        "contributor": {"name": "Contributor", "points": 100, "description": "Added 5 new restrooms"},
        "photographer": {"name": "Photographer", "points": 75, "description": "Uploaded 10 photos"},
        "helpful_reviewer": {"name": "Helpful Reviewer", "points": 150, "description": "Received 50 helpful votes"},
        "guardian": {"name": "Guardian", "points": 100, "description": "Reported 10 issues that were verified"},
        "accessibility_champion": {"name": "Accessibility Champion", "points": 200, "description": "Added accessibility info to 20 restrooms"},
    }

    @classmethod
    def check_and_award_badges(cls, user: User, db: Session):
        """Check and award badges based on user activity"""
        new_badges = []

        # Check review count badges
        review_count = db.query(Review).filter(Review.user_id == user.id).count()
        if review_count >= 1 and "first_review" not in user.badges:
            user.badges.append("first_review")
            user.points += cls.BADGES["first_review"]["points"]
            new_badges.append("first_review")

        if review_count >= 10 and "explorer_10" not in user.badges:
            user.badges.append("explorer_10")
            user.points += cls.BADGES["explorer_10"]["points"]
            new_badges.append("explorer_10")

        if review_count >= 50 and "explorer_50" not in user.badges:
            user.badges.append("explorer_50")
            user.points += cls.BADGES["explorer_50"]["points"]
            new_badges.append("explorer_50")

        # Check contribution badges
        contribution_count = db.query(Restroom).filter(
            Restroom.submitter_id == user.id,
            Restroom.source == RestroomSource.USER
        ).count()

        if contribution_count >= 5 and "contributor" not in user.badges:
            user.badges.append("contributor")
            user.points += cls.BADGES["contributor"]["points"]
            new_badges.append("contributor")

        if new_badges:
            db.commit()

        return new_badges

# ========================= UTILITY FUNCTIONS =========================

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in meters using Haversine formula"""
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

async def update_restroom_ratings(restroom_id: str, db: Session):
    """Update cached rating aggregates for a restroom"""
    reviews = db.query(Review).filter(Review.restroom_id == restroom_id).all()

    if not reviews:
        return

    restroom = db.query(Restroom).filter(Restroom.id == restroom_id).first()
    if not restroom:
        return

    # Calculate averages
    restroom.avg_cleanliness = sum(r.cleanliness for r in reviews) / len(reviews)
    restroom.avg_lighting = sum(r.lighting for r in reviews) / len(reviews)
    restroom.avg_safety = sum(r.safety for r in reviews) / len(reviews)
    restroom.avg_privacy = sum(r.privacy for r in reviews) / len(reviews)
    restroom.avg_accessibility = sum(r.accessibility for r in reviews) / len(reviews)
    restroom.avg_overall = sum(r.overall for r in reviews) / len(reviews)
    restroom.review_count = len(reviews)

    db.commit()

# ========================= GEOCODING FUNCTIONS =========================

async def reverse_geocode(lat: float, lon: float) -> Dict[str, str]:
    """Reverse geocode coordinates to get address information"""
    cache_key = f"geocode:{lat:.6f},{lon:.6f}"

    # Check cache first
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # Use Google Maps Geocoding API or OSM Nominatim
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://nominatim.openstreetmap.org/reverse",
            params={
                "lat": lat,
                "lon": lon,
                "format": "json",
                "addressdetails": 1
            },
            headers={"User-Agent": "Puper/1.0"}
        )

        if response.status_code == 200:
            data = response.json()
            result = {
                "address": data.get("display_name", ""),
                "city": data.get("address", {}).get("city") or data.get("address", {}).get("town"),
                "country": data.get("address", {}).get("country")
            }
            redis_client.setex(cache_key, 86400, json.dumps(result))  # Cache for 24 hours
            return result

    return {"address": "", "city": "", "country": ""}

# ========================= API ENDPOINTS =========================

@app.get("/")
async def root():
    return {
        "name": "Puper API",
        "version": "1.0.0",
        "description": "The Waze of Public Restrooms",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "auth": "/auth/*",
            "restrooms": "/restrooms/*",
            "reviews": "/reviews/*",
            "users": "/users/*"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# --- Authentication Endpoints ---

@app.post("/auth/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    # Create new user
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password),
        is_anonymous=user.is_anonymous
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id)}, expires_delta=access_token_expires
    )

    user_response = UserResponse(
        id=str(db_user.id),
        username=db_user.username,
        email=db_user.email,
        full_name=db_user.full_name,
        role=db_user.role,
        points=db_user.points,
        badges=db_user.badges,
        is_verified=db_user.is_verified,
        is_anonymous=db_user.is_anonymous,
        created_at=db_user.created_at
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }

@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with username and password"""
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    user_response = UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        points=user.points,
        badges=user.badges,
        is_verified=user.is_verified,
        is_anonymous=user.is_anonymous,
        created_at=user.created_at
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }

# --- Restroom Endpoints ---

@app.get("/restrooms/search", response_model=List[RestroomResponse])
async def search_restrooms(
    params: SearchParams = Depends(),
    db: Session = Depends(get_db)
):
    """Search for restrooms near a location"""
    # Cache key
    cache_key = f"search:{params.lat:.4f},{params.lon:.4f}:{params.radius}:{params.min_rating}"
    cached = redis_client.get(cache_key)

    if cached and params.offset == 0:
        return json.loads(cached)

    # Build query
    query = db.query(Restroom).filter(
        Restroom.is_active == True,
        Restroom.permanently_closed == False
    )

    # Apply filters
    if params.min_rating:
        query = query.filter(Restroom.avg_overall >= params.min_rating)

    if params.wheelchair_accessible is not None:
        if params.wheelchair_accessible:
            query = query.filter(Restroom.wheelchair_accessible.in_([AccessibilityLevel.FULL, AccessibilityLevel.PARTIAL]))
        else:
            query = query.filter(Restroom.wheelchair_accessible == AccessibilityLevel.NONE)

    if params.gender_neutral is not None:
        query = query.filter(Restroom.gender_neutral == params.gender_neutral)

    if params.baby_changing is not None:
        query = query.filter(Restroom.baby_changing == params.baby_changing)

    if params.free_only:
        query = query.filter(Restroom.requires_fee == False)

    # Get all restrooms and calculate distances
    all_restrooms = query.all()
    restrooms_with_distance = []

    for restroom in all_restrooms:
        distance = calculate_distance(params.lat, params.lon, restroom.latitude, restroom.longitude)
        if distance <= params.radius:
            restroom_response = RestroomResponse(
                id=str(restroom.id),
                source=restroom.source,
                name=restroom.name,
                description=restroom.description,
                latitude=restroom.latitude,
                longitude=restroom.longitude,
                address=restroom.address,
                city=restroom.city,
                country=restroom.country,
                wheelchair_accessible=restroom.wheelchair_accessible,
                gender_neutral=restroom.gender_neutral,
                baby_changing=restroom.baby_changing,
                indoor=restroom.indoor,
                requires_fee=restroom.requires_fee,
                fee_amount=restroom.fee_amount,
                unisex=restroom.unisex,
                has_soap=restroom.has_soap,
                has_toilet_paper=restroom.has_toilet_paper,
                has_hand_dryer=restroom.has_hand_dryer,
                has_paper_towels=restroom.has_paper_towels,
                has_hot_water=restroom.has_hot_water,
                has_mirror=restroom.has_mirror,
                operating_hours=restroom.operating_hours,
                avg_cleanliness=restroom.avg_cleanliness,
                avg_lighting=restroom.avg_lighting,
                avg_safety=restroom.avg_safety,
                avg_privacy=restroom.avg_privacy,
                avg_accessibility=restroom.avg_accessibility,
                avg_overall=restroom.avg_overall,
                review_count=restroom.review_count,
                is_active=restroom.is_active,
                is_verified=restroom.is_verified,
                temporarily_closed=restroom.temporarily_closed,
                permanently_closed=restroom.permanently_closed,
                created_at=restroom.created_at,
                updated_at=restroom.updated_at,
                distance=round(distance, 2)
            )
            restrooms_with_distance.append(restroom_response)

    # Sort by distance
    restrooms_with_distance.sort(key=lambda x: x.distance)

    # Apply pagination
    paginated = restrooms_with_distance[params.offset:params.offset + params.limit]

    # Cache results for 5 minutes
    if params.offset == 0:
        redis_client.setex(cache_key, 300, json.dumps([r.dict() for r in paginated]))

    return paginated

@app.get("/restrooms/route", response_model=List[RestroomResponse])
async def search_along_route(
    params: RouteSearchParams = Depends(),
    db: Session = Depends(get_db)
):
    """Search for restrooms along a route"""
    # This would integrate with Google Routes API to get the polyline
    # and then use Search Along Route to find restrooms
    # For now, we'll implement a simplified version

    # Get restrooms between origin and destination
    min_lat = min(params.origin_lat, params.dest_lat) - 0.1
    max_lat = max(params.origin_lat, params.dest_lat) + 0.1
    min_lon = min(params.origin_lon, params.dest_lon) - 0.1
    max_lon = max(params.origin_lon, params.dest_lon) + 0.1

    query = db.query(Restroom).filter(
        Restroom.is_active == True,
        Restroom.permanently_closed == False,
        Restroom.latitude.between(min_lat, max_lat),
        Restroom.longitude.between(min_lon, max_lon)
    )

    # Apply filters
    if params.min_rating:
        query = query.filter(Restroom.avg_overall >= params.min_rating)

    if params.wheelchair_accessible:
        query = query.filter(Restroom.wheelchair_accessible.in_([AccessibilityLevel.FULL, AccessibilityLevel.PARTIAL]))

    restrooms = query.limit(params.limit).all()

    # Calculate approximate detour time (simplified)
    results = []
    for restroom in restrooms:
        # Calculate distance from route line (simplified as distance from origin)
        distance_from_origin = calculate_distance(
            params.origin_lat, params.origin_lon,
            restroom.latitude, restroom.longitude
        )

        # Estimate detour time (assuming 50 km/h average speed)
        detour_minutes = (distance_from_origin / 1000) / 50 * 60

        if detour_minutes <= params.max_detour_minutes:
            restroom_response = RestroomResponse(
                id=str(restroom.id),
                source=restroom.source,
                name=restroom.name,
                description=restroom.description,
                latitude=restroom.latitude,
                longitude=restroom.longitude,
                address=restroom.address,
                city=restroom.city,
                country=restroom.country,
                wheelchair_accessible=restroom.wheelchair_accessible,
                gender_neutral=restroom.gender_neutral,
                baby_changing=restroom.baby_changing,
                indoor=restroom.indoor,
                requires_fee=restroom.requires_fee,
                fee_amount=restroom.fee_amount,
                unisex=restroom.unisex,
                has_soap=restroom.has_soap,
                has_toilet_paper=restroom.has_toilet_paper,
                has_hand_dryer=restroom.has_hand_dryer,
                has_paper_towels=restroom.has_paper_towels,
                has_hot_water=restroom.has_hot_water,
                has_mirror=restroom.has_mirror,
                operating_hours=restroom.operating_hours,
                avg_cleanliness=restroom.avg_cleanliness,
                avg_lighting=restroom.avg_lighting,
                avg_safety=restroom.avg_safety,
                avg_privacy=restroom.avg_privacy,
                avg_accessibility=restroom.avg_accessibility,
                avg_overall=restroom.avg_overall,
                review_count=restroom.review_count,
                is_active=restroom.is_active,
                is_verified=restroom.is_verified,
                temporarily_closed=restroom.temporarily_closed,
                permanently_closed=restroom.permanently_closed,
                created_at=restroom.created_at,
                updated_at=restroom.updated_at,
                detour_time=int(detour_minutes * 60)  # Convert to seconds
            )
            results.append(restroom_response)

    # Sort by detour time
    results.sort(key=lambda x: x.detour_time)

    return results[:params.limit]

@app.get("/restrooms/{restroom_id}", response_model=RestroomResponse)
async def get_restroom(restroom_id: str, db: Session = Depends(get_db)):
    """Get details of a specific restroom"""
    restroom = db.query(Restroom).filter(Restroom.id == restroom_id).first()

    if not restroom:
        raise HTTPException(status_code=404, detail="Restroom not found")

    return RestroomResponse(
        id=str(restroom.id),
        source=restroom.source,
        name=restroom.name,
        description=restroom.description,
        latitude=restroom.latitude,
        longitude=restroom.longitude,
        address=restroom.address,
        city=restroom.city,
        country=restroom.country,
        wheelchair_accessible=restroom.wheelchair_accessible,
        gender_neutral=restroom.gender_neutral,
        baby_changing=restroom.baby_changing,
        indoor=restroom.indoor,
        requires_fee=restroom.requires_fee,
        fee_amount=restroom.fee_amount,
        unisex=restroom.unisex,
        has_soap=restroom.has_soap,
        has_toilet_paper=restroom.has_toilet_paper,
        has_hand_dryer=restroom.has_hand_dryer,
        has_paper_towels=restroom.has_paper_towels,
        has_hot_water=restroom.has_hot_water,
        has_mirror=restroom.has_mirror,
        operating_hours=restroom.operating_hours,
        avg_cleanliness=restroom.avg_cleanliness,
        avg_lighting=restroom.avg_lighting,
        avg_safety=restroom.avg_safety,
        avg_privacy=restroom.avg_privacy,
        avg_accessibility=restroom.avg_accessibility,
        avg_overall=restroom.avg_overall,
        review_count=restroom.review_count,
        is_active=restroom.is_active,
        is_verified=restroom.is_verified,
        temporarily_closed=restroom.temporarily_closed,
        permanently_closed=restroom.permanently_closed,
        created_at=restroom.created_at,
        updated_at=restroom.updated_at
    )

@app.post("/restrooms", response_model=RestroomResponse)
async def create_restroom(
    restroom: RestroomCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a new restroom"""
    from geoalchemy2.elements import WKTElement

    # Reverse geocode if address not provided
    if not restroom.address:
        geo_info = await reverse_geocode(restroom.latitude, restroom.longitude)
        restroom.address = geo_info["address"]
        restroom.city = restroom.city or geo_info["city"]
        restroom.country = restroom.country or geo_info["country"]

    # Create restroom
    db_restroom = Restroom(
        source=restroom.source,
        source_id=restroom.source_id,
        name=restroom.name,
        description=restroom.description,
        location=WKTElement(f'POINT({restroom.longitude} {restroom.latitude})', srid=4326),
        latitude=restroom.latitude,
        longitude=restroom.longitude,
        address=restroom.address,
        city=restroom.city,
        country=restroom.country,
        wheelchair_accessible=restroom.wheelchair_accessible,
        gender_neutral=restroom.gender_neutral,
        baby_changing=restroom.baby_changing,
        indoor=restroom.indoor,
        requires_fee=restroom.requires_fee,
        fee_amount=restroom.fee_amount,
        unisex=restroom.unisex,
        has_soap=restroom.has_soap,
        has_toilet_paper=restroom.has_toilet_paper,
        has_hand_dryer=restroom.has_hand_dryer,
        has_paper_towels=restroom.has_paper_towels,
        has_hot_water=restroom.has_hot_water,
        has_mirror=restroom.has_mirror,
        operating_hours=restroom.operating_hours,
        submitter_id=current_user.id,
        extra_attributes=restroom.extra_attributes or {}
    )

    db.add(db_restroom)
    db.commit()
    db.refresh(db_restroom)

    # Award points for contribution
    current_user.points += POINTS_RESTROOM_SUBMISSION
    db.commit()

    # Check for new badges
    background_tasks.add_task(BadgeSystem.check_and_award_badges, current_user, db)

    logger.info(f"New restroom submitted by {current_user.username}: {db_restroom.id}")

    return RestroomResponse(
        id=str(db_restroom.id),
        source=db_restroom.source,
        name=db_restroom.name,
        description=db_restroom.description,
        latitude=db_restroom.latitude,
        longitude=db_restroom.longitude,
        address=db_restroom.address,
        city=db_restroom.city,
        country=db_restroom.country,
        wheelchair_accessible=db_restroom.wheelchair_accessible,
        gender_neutral=db_restroom.gender_neutral,
        baby_changing=db_restroom.baby_changing,
        indoor=db_restroom.indoor,
        requires_fee=db_restroom.requires_fee,
        fee_amount=db_restroom.fee_amount,
        unisex=db_restroom.unisex,
        has_soap=db_restroom.has_soap,
        has_toilet_paper=db_restroom.has_toilet_paper,
        has_hand_dryer=db_restroom.has_hand_dryer,
        has_paper_towels=db_restroom.has_paper_towels,
        has_hot_water=db_restroom.has_hot_water,
        has_mirror=db_restroom.has_mirror,
        operating_hours=db_restroom.operating_hours,
        avg_cleanliness=db_restroom.avg_cleanliness,
        avg_lighting=db_restroom.avg_lighting,
        avg_safety=db_restroom.avg_safety,
        avg_privacy=db_restroom.avg_privacy,
        avg_accessibility=db_restroom.avg_accessibility,
        avg_overall=db_restroom.avg_overall,
        review_count=db_restroom.review_count,
        is_active=db_restroom.is_active,
        is_verified=db_restroom.is_verified,
        temporarily_closed=db_restroom.temporarily_closed,
        permanently_closed=db_restroom.permanently_closed,
        created_at=db_restroom.created_at,
        updated_at=db_restroom.updated_at
    )

@app.put("/restrooms/{restroom_id}", response_model=RestroomResponse)
async def update_restroom(
    restroom_id: str,
    updates: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update restroom information (moderators and partners only)"""
    if current_user.role not in [UserRole.MODERATOR, UserRole.ADMIN, UserRole.PARTNER]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    restroom = db.query(Restroom).filter(Restroom.id == restroom_id).first()

    if not restroom:
        raise HTTPException(status_code=404, detail="Restroom not found")

    # Update fields
    for key, value in updates.items():
        if hasattr(restroom, key):
            setattr(restroom, key, value)

    restroom.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(restroom)

    return RestroomResponse(
        id=str(restroom.id),
        source=restroom.source,
        name=restroom.name,
        description=restroom.description,
        latitude=restroom.latitude,
        longitude=restroom.longitude,
        address=restroom.address,
        city=restroom.city,
        country=restroom.country,
        wheelchair_accessible=restroom.wheelchair_accessible,
        gender_neutral=restroom.gender_neutral,
        baby_changing=restroom.baby_changing,
        indoor=restroom.indoor,
        requires_fee=restroom.requires_fee,
        fee_amount=restroom.fee_amount,
        unisex=restroom.unisex,
        has_soap=restroom.has_soap,
        has_toilet_paper=restroom.has_toilet_paper,
        has_hand_dryer=restroom.has_hand_dryer,
        has_paper_towels=restroom.has_paper_towels,
        has_hot_water=restroom.has_hot_water,
        has_mirror=restroom.has_mirror,
        operating_hours=restroom.operating_hours,
        avg_cleanliness=restroom.avg_cleanliness,
        avg_lighting=restroom.avg_lighting,
        avg_safety=restroom.avg_safety,
        avg_privacy=restroom.avg_privacy,
        avg_accessibility=restroom.avg_accessibility,
        avg_overall=restroom.avg_overall,
        review_count=restroom.review_count,
        is_active=restroom.is_active,
        is_verified=restroom.is_verified,
        temporarily_closed=restroom.temporarily_closed,
        permanently_closed=restroom.permanently_closed,
        created_at=restroom.created_at,
        updated_at=restroom.updated_at
    )

# --- Review Endpoints ---
@app.post("/reviews", response_model=ReviewResponse)
async def create_review(
    review: ReviewCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a review for a restroom"""
    # Check if restroom exists
    restroom = db.query(Restroom).filter(Restroom.id == review.restroom_id).first()
    if not restroom:
        raise HTTPException(status_code=404, detail="Restroom not found")

    # Check if user already reviewed this restroom
    existing_review = db.query(Review).filter(
        Review.user_id == current_user.id,
        Review.restroom_id == review.restroom_id
    ).first()

    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this restroom")

    # Create review
    db_review = Review(
        **review.dict(),
        user_id=current_user.id
    )

    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    # Update restroom ratings
    background_tasks.add_task(update_restroom_ratings, review.restroom_id, db)

    # Award points
    current_user.points += POINTS_REVIEW
    db.commit()

    # Check for badges
    background_tasks.add_task(BadgeSystem.check_and_award_badges, current_user, db)

    # Prepare response
    response = ReviewResponse(
        id=str(db_review.id),
        user_id=str(db_review.user_id),
        restroom_id=str(db_review.restroom_id),
        cleanliness=db_review.cleanliness,
        lighting=db_review.lighting,
        safety=db_review.safety,
        privacy=db_review.privacy,
        accessibility=db_review.accessibility,
        overall=db_review.overall,
        comment=db_review.comment,
        is_verified=db_review.is_verified,
        helpful_count=db_review.helpful_count,
        created_at=db_review.created_at,
        photos=db_review.photos,
        username=current_user.username if not current_user.is_anonymous else "Anonymous"
    )

    return response

@app.get("/reviews/restroom/{restroom_id}", response_model=List[ReviewResponse])
async def get_restroom_reviews(
    restroom_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get reviews for a specific restroom"""
    reviews = db.query(Review).filter(
        Review.restroom_id == restroom_id
    ).order_by(Review.created_at.desc()).offset(offset).limit(limit).all()

    # Add usernames
    results = []
    for review in reviews:
        user = db.query(User).filter(User.id == review.user_id).first()
        review_response = ReviewResponse(
            id=str(review.id),
            user_id=str(review.user_id),
            restroom_id=str(review.restroom_id),
            cleanliness=review.cleanliness,
            lighting=review.lighting,
            safety=review.safety,
            privacy=review.privacy,
            accessibility=review.accessibility,
            overall=review.overall,
            comment=review.comment,
            is_verified=review.is_verified,
            helpful_count=review.helpful_count,
            created_at=review.created_at,
            photos=review.photos,
            username=user.username if user and not user.is_anonymous else "Anonymous"
        )
        results.append(review_response)

    return results

@app.post("/reviews/{review_id}/helpful")
async def mark_review_helpful(
    review_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a review as helpful"""
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Increment helpful count
    review.helpful_count += 1
    db.commit()

    # Award points to review author
    author = db.query(User).filter(User.id == review.user_id).first()
    if author:
        author.points += POINTS_HELPFUL_VOTE
        db.commit()

    return {"message": "Review marked as helpful"}

# --- Favorite Endpoints ---

@app.post("/favorites/{restroom_id}")
async def add_favorite(
    restroom_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a restroom to favorites"""
    # Check if restroom exists
    restroom = db.query(Restroom).filter(Restroom.id == restroom_id).first()
    if not restroom:
        raise HTTPException(status_code=404, detail="Restroom not found")

    # Check if already favorited
    existing = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.restroom_id == restroom_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already in favorites")

    # Add favorite
    favorite = Favorite(user_id=current_user.id, restroom_id=restroom_id)
    db.add(favorite)
    db.commit()

    return {"message": "Added to favorites"}

@app.delete("/favorites/{restroom_id}")
async def remove_favorite(
    restroom_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a restroom from favorites"""
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.restroom_id == restroom_id
    ).first()

    if not favorite:
        raise HTTPException(status_code=404, detail="Not in favorites")

    db.delete(favorite)
    db.commit()

    return {"message": "Removed from favorites"}

@app.get("/favorites", response_model=List[RestroomResponse])
async def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's favorite restrooms"""
    favorites = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()

    restroom_ids = [f.restroom_id for f in favorites]
    restrooms = db.query(Restroom).filter(Restroom.id.in_(restroom_ids)).all()

    results = []
    for restroom in restrooms:
        results.append(RestroomResponse(
            id=str(restroom.id),
            source=restroom.source,
            name=restroom.name,
            description=restroom.description,
            latitude=restroom.latitude,
            longitude=restroom.longitude,
            address=restroom.address,
            city=restroom.city,
            country=restroom.country,
            wheelchair_accessible=restroom.wheelchair_accessible,
            gender_neutral=restroom.gender_neutral,
            baby_changing=restroom.baby_changing,
            indoor=restroom.indoor,
            requires_fee=restroom.requires_fee,
            fee_amount=restroom.fee_amount,
            unisex=restroom.unisex,
            has_soap=restroom.has_soap,
            has_toilet_paper=restroom.has_toilet_paper,
            has_hand_dryer=restroom.has_hand_dryer,
            has_paper_towels=restroom.has_paper_towels,
            has_hot_water=restroom.has_hot_water,
            has_mirror=restroom.has_mirror,
            operating_hours=restroom.operating_hours,
            avg_cleanliness=restroom.avg_cleanliness,
            avg_lighting=restroom.avg_lighting,
            avg_safety=restroom.avg_safety,
            avg_privacy=restroom.avg_privacy,
            avg_accessibility=restroom.avg_accessibility,
            avg_overall=restroom.avg_overall,
            review_count=restroom.review_count,
            is_active=restroom.is_active,
            is_verified=restroom.is_verified,
            temporarily_closed=restroom.temporarily_closed,
            permanently_closed=restroom.permanently_closed,
            created_at=restroom.created_at,
            updated_at=restroom.updated_at
        ))

    return results

# --- Report Endpoints ---

@app.post("/reports")
async def report_issue(
    restroom_id: str,
    report_type: str,
    description: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Report an issue with a restroom"""
    # Check if restroom exists
    restroom = db.query(Restroom).filter(Restroom.id == restroom_id).first()
    if not restroom:
        raise HTTPException(status_code=404, detail="Restroom not found")

    # Create report
    report = Report(
        restroom_id=restroom_id,
        reporter_id=current_user.id,
        report_type=report_type,
        description=description
    )

    db.add(report)
    db.commit()

    # Auto-close if multiple reports
    recent_reports = db.query(Report).filter(
        Report.restroom_id == restroom_id,
        Report.report_type == "closed",
        Report.created_at >= datetime.utcnow() - timedelta(days=1)
    ).count()

    if recent_reports >= 3:
        restroom.temporarily_closed = True
        db.commit()
        logger.warning(f"Restroom {restroom_id} auto-closed due to multiple reports")

    # Award points
    current_user.points += POINTS_HELPFUL_VOTE  # Small reward for reporting issues
    db.commit()

    return {"message": "Issue reported successfully"}

# --- User Profile Endpoints ---

@app.get("/users/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile"""
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        points=current_user.points,
        badges=current_user.badges,
        is_verified=current_user.is_verified,
        is_anonymous=current_user.is_anonymous,
        created_at=current_user.created_at
    )

@app.get("/users/leaderboard")
async def get_leaderboard(
    period: str = Query("week", regex="^(week|month|all)$"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get user leaderboard"""
    query = db.query(User).filter(User.is_anonymous == False)

    if period == "week":
        start_date = datetime.utcnow() - timedelta(days=7)
        # This would need a separate points tracking table for time-based queries
        # For now, we'll just return top users by total points
    elif period == "month":
        start_date = datetime.utcnow() - timedelta(days=30)

    users = query.order_by(User.points.desc()).limit(limit).all()

    return [
        {
            "rank": i + 1,
            "username": user.username,
            "points": user.points,
            "badges": user.badges,
            "review_count": len(user.reviews)
        }
        for i, user in enumerate(users)
    ]

@app.get("/users/{user_id}/stats")
async def get_user_stats(user_id: str, db: Session = Depends(get_db)):
    """Get statistics for a specific user"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stats = {
        "username": user.username if not user.is_anonymous else "Anonymous",
        "points": user.points,
        "badges": user.badges,
        "review_count": db.query(Review).filter(Review.user_id == user_id).count(),
        "contribution_count": db.query(Restroom).filter(
            Restroom.submitter_id == user_id,
            Restroom.source == RestroomSource.USER
        ).count(),
        "member_since": user.created_at
    }

    return stats

# ========================= ADMIN ENDPOINTS =========================

# Admin authentication dependency
async def get_admin_user(current_user: User = Depends(get_current_user)):
    """Ensure current user is admin"""
    if current_user.role not in [UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

async def get_moderator_user(current_user: User = Depends(get_current_user)):
    """Ensure current user is moderator or admin"""
    if current_user.role not in [UserRole.MODERATOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Moderator access required")
    return current_user

# --- Admin Dashboard ---

@app.get("/admin/dashboard")
async def admin_dashboard(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get admin dashboard statistics"""
    # Get counts
    total_users = db.query(User).count()
    total_restrooms = db.query(Restroom).count()
    total_reviews = db.query(Review).count()
    pending_reports = db.query(Report).filter(Report.status == "pending").count()

    # Get recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users_week = db.query(User).filter(User.created_at >= week_ago).count()
    new_restrooms_week = db.query(Restroom).filter(Restroom.created_at >= week_ago).count()
    new_reviews_week = db.query(Review).filter(Review.created_at >= week_ago).count()

    # Get top contributors
    top_contributors = db.query(User).filter(
        User.is_anonymous == False
    ).order_by(User.points.desc()).limit(10).all()

    # Get restrooms needing verification
    unverified_restrooms = db.query(Restroom).filter(
        Restroom.is_verified == False,
        Restroom.source == RestroomSource.USER
    ).count()

    return {
        "totals": {
            "users": total_users,
            "restrooms": total_restrooms,
            "reviews": total_reviews,
            "pending_reports": pending_reports,
            "unverified_restrooms": unverified_restrooms
        },
        "recent_activity": {
            "new_users_week": new_users_week,
            "new_restrooms_week": new_restrooms_week,
            "new_reviews_week": new_reviews_week
        },
        "top_contributors": [
            {
                "id": str(user.id),
                "username": user.username,
                "points": user.points,
                "badges": len(user.badges)
            }
            for user in top_contributors
        ]
    }

# --- User Management ---

@app.get("/admin/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """List all users with filtering"""
    query = db.query(User)

    if search:
        query = query.filter(
            (User.username.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%")) |
            (User.full_name.ilike(f"%{search}%"))
        )

    if role:
        query = query.filter(User.role == role)

    users = query.offset(skip).limit(limit).all()
    total = query.count()

    return {
        "users": [
            {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "points": user.points,
                "badges": user.badges,
                "is_verified": user.is_verified,
                "is_anonymous": user.is_anonymous,
                "created_at": user.created_at,
                "review_count": len(user.reviews),
                "contribution_count": len(user.submitted_restrooms)
            }
            for user in users
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    }

@app.patch("/admin/users/{user_id}")
async def update_user(
    user_id: str,
    updates: Dict[str, Any],
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update user information"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update allowed fields
    allowed_fields = ["role", "is_verified", "points", "badges"]
    for key, value in updates.items():
        if key in allowed_fields and hasattr(user, key):
            setattr(user, key, value)

    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)

    return {
        "message": "User updated successfully",
        "user": {
            "id": str(user.id),
            "username": user.username,
            "role": user.role,
            "is_verified": user.is_verified,
            "points": user.points,
            "badges": user.badges
        }
    }

@app.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a user (soft delete by anonymizing)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Soft delete by anonymizing
    user.username = f"deleted_user_{user.id}"
    user.email = f"deleted_{user.id}@deleted.com"
    user.full_name = "Deleted User"
    user.is_anonymous = True
    user.updated_at = datetime.utcnow()

    db.commit()

    return {"message": "User deleted successfully"}

# --- Restroom Management ---

@app.get("/admin/restrooms")
async def list_restrooms_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    verified: Optional[bool] = Query(None),
    admin_user: User = Depends(get_moderator_user),
    db: Session = Depends(get_db)
):
    """List restrooms for admin management"""
    query = db.query(Restroom)

    if status == "active":
        query = query.filter(Restroom.is_active == True)
    elif status == "inactive":
        query = query.filter(Restroom.is_active == False)
    elif status == "closed":
        query = query.filter(Restroom.temporarily_closed == True)

    if source:
        query = query.filter(Restroom.source == source)

    if verified is not None:
        query = query.filter(Restroom.is_verified == verified)

    restrooms = query.order_by(Restroom.created_at.desc()).offset(skip).limit(limit).all()
    total = query.count()

    return {
        "restrooms": [
            {
                "id": str(restroom.id),
                "name": restroom.name,
                "source": restroom.source,
                "latitude": restroom.latitude,
                "longitude": restroom.longitude,
                "address": restroom.address,
                "city": restroom.city,
                "country": restroom.country,
                "avg_overall": restroom.avg_overall,
                "review_count": restroom.review_count,
                "is_active": restroom.is_active,
                "is_verified": restroom.is_verified,
                "temporarily_closed": restroom.temporarily_closed,
                "permanently_closed": restroom.permanently_closed,
                "created_at": restroom.created_at,
                "submitter_id": str(restroom.submitter_id) if restroom.submitter_id else None
            }
            for restroom in restrooms
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    }

@app.patch("/admin/restrooms/{restroom_id}")
async def update_restroom_admin(
    restroom_id: str,
    updates: Dict[str, Any],
    admin_user: User = Depends(get_moderator_user),
    db: Session = Depends(get_db)
):
    """Update restroom status and information"""
    restroom = db.query(Restroom).filter(Restroom.id == restroom_id).first()
    if not restroom:
        raise HTTPException(status_code=404, detail="Restroom not found")

    # Update allowed fields
    allowed_fields = [
        "is_verified", "is_active", "temporarily_closed", "permanently_closed",
        "name", "description", "address", "city", "country"
    ]

    for key, value in updates.items():
        if key in allowed_fields and hasattr(restroom, key):
            setattr(restroom, key, value)

    restroom.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(restroom)

    return {
        "message": "Restroom updated successfully",
        "restroom": {
            "id": str(restroom.id),
            "name": restroom.name,
            "is_verified": restroom.is_verified,
            "is_active": restroom.is_active,
            "temporarily_closed": restroom.temporarily_closed,
            "permanently_closed": restroom.permanently_closed
        }
    }

@app.delete("/admin/restrooms/{restroom_id}")
async def delete_restroom(
    restroom_id: str,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a restroom permanently"""
    restroom = db.query(Restroom).filter(Restroom.id == restroom_id).first()
    if not restroom:
        raise HTTPException(status_code=404, detail="Restroom not found")

    # Delete associated reviews and favorites first
    db.query(Review).filter(Review.restroom_id == restroom_id).delete()
    db.query(Favorite).filter(Favorite.restroom_id == restroom_id).delete()
    db.query(Report).filter(Report.restroom_id == restroom_id).delete()

    # Delete the restroom
    db.delete(restroom)
    db.commit()

    return {"message": "Restroom deleted successfully"}

# --- Report Management ---

@app.get("/admin/reports")
async def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = Query(None),
    report_type: Optional[str] = Query(None),
    admin_user: User = Depends(get_moderator_user),
    db: Session = Depends(get_db)
):
    """List all reports for admin review"""
    query = db.query(Report)

    if status:
        query = query.filter(Report.status == status)

    if report_type:
        query = query.filter(Report.report_type == report_type)

    reports = query.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
    total = query.count()

    results = []
    for report in reports:
        restroom = db.query(Restroom).filter(Restroom.id == report.restroom_id).first()
        reporter = db.query(User).filter(User.id == report.reporter_id).first() if report.reporter_id else None

        results.append({
            "id": str(report.id),
            "restroom_id": str(report.restroom_id),
            "restroom_name": restroom.name if restroom else "Unknown",
            "restroom_address": restroom.address if restroom else "Unknown",
            "reporter_username": reporter.username if reporter else "Anonymous",
            "report_type": report.report_type,
            "description": report.description,
            "status": report.status,
            "created_at": report.created_at,
            "resolved_at": report.resolved_at
        })

    return {
        "reports": results,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@app.patch("/admin/reports/{report_id}")
async def update_report_status(
    report_id: str,
    status: str,
    admin_user: User = Depends(get_moderator_user),
    db: Session = Depends(get_db)
):
    """Update report status (pending, verified, rejected)"""
    if status not in ["pending", "verified", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.status = status
    if status in ["verified", "rejected"]:
        report.resolved_at = datetime.utcnow()

    # If verified and it's a closure report, close the restroom
    if status == "verified" and report.report_type == "closed":
        restroom = db.query(Restroom).filter(Restroom.id == report.restroom_id).first()
        if restroom:
            restroom.temporarily_closed = True

    db.commit()

    return {"message": f"Report status updated to {status}"}

# --- Analytics ---

@app.get("/admin/analytics")
async def get_analytics(
    period: str = Query("month", regex="^(week|month|quarter|year)$"),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get detailed analytics for admin dashboard"""
    # Calculate date range
    now = datetime.utcnow()
    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    elif period == "quarter":
        start_date = now - timedelta(days=90)
    else:  # year
        start_date = now - timedelta(days=365)

    # User analytics
    new_users = db.query(User).filter(User.created_at >= start_date).count()
    active_users = db.query(User).filter(
        User.reviews.any(Review.created_at >= start_date)
    ).count()

    # Restroom analytics
    new_restrooms = db.query(Restroom).filter(Restroom.created_at >= start_date).count()
    verified_restrooms = db.query(Restroom).filter(
        Restroom.is_verified == True,
        Restroom.created_at >= start_date
    ).count()

    # Review analytics
    new_reviews = db.query(Review).filter(Review.created_at >= start_date).count()
    avg_rating = db.query(func.avg(Review.overall)).filter(
        Review.created_at >= start_date
    ).scalar() or 0

    # Report analytics
    new_reports = db.query(Report).filter(Report.created_at >= start_date).count()
    resolved_reports = db.query(Report).filter(
        Report.resolved_at >= start_date
    ).count()

    # Top cities by restroom count
    top_cities = db.query(
        Restroom.city,
        func.count(Restroom.id).label('count')
    ).filter(
        Restroom.city.isnot(None),
        Restroom.is_active == True
    ).group_by(Restroom.city).order_by(func.count(Restroom.id).desc()).limit(10).all()

    return {
        "period": period,
        "date_range": {
            "start": start_date,
            "end": now
        },
        "users": {
            "new_users": new_users,
            "active_users": active_users
        },
        "restrooms": {
            "new_restrooms": new_restrooms,
            "verified_restrooms": verified_restrooms
        },
        "reviews": {
            "new_reviews": new_reviews,
            "average_rating": round(float(avg_rating), 2)
        },
        "reports": {
            "new_reports": new_reports,
            "resolved_reports": resolved_reports
        },
        "top_cities": [
            {"city": city, "restroom_count": count}
            for city, count in top_cities
        ]
    }

# --- Bulk Operations ---

@app.post("/admin/bulk/verify-restrooms")
async def bulk_verify_restrooms(
    restroom_ids: List[str],
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Bulk verify multiple restrooms"""
    updated_count = db.query(Restroom).filter(
        Restroom.id.in_(restroom_ids)
    ).update(
        {"is_verified": True, "updated_at": datetime.utcnow()},
        synchronize_session=False
    )

    db.commit()

    return {
        "message": f"Verified {updated_count} restrooms",
        "updated_count": updated_count
    }

@app.post("/admin/bulk/close-restrooms")
async def bulk_close_restrooms(
    restroom_ids: List[str],
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Bulk close multiple restrooms"""
    updated_count = db.query(Restroom).filter(
        Restroom.id.in_(restroom_ids)
    ).update(
        {"temporarily_closed": True, "updated_at": datetime.utcnow()},
        synchronize_session=False
    )

    db.commit()

    return {
        "message": f"Closed {updated_count} restrooms",
        "updated_count": updated_count
    }

# --- Data Ingestion ---

@app.post("/admin/ingest/osm")
async def trigger_osm_ingestion(
    bbox: Optional[str] = Query(None, description="Bounding box: south,west,north,east"),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Trigger OpenStreetMap data ingestion (admin only)"""
    # This would trigger the data ingestion pipeline
    # For now, return a mock response
    return {
        "status": "initiated",
        "source": "OpenStreetMap",
        "bbox": bbox,
        "estimated_time": "5-10 minutes",
        "message": "OSM data ingestion started. Check back in a few minutes for results."
    }

@app.get("/admin/stats")
async def get_system_stats(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get system-wide statistics (admin only)"""
    stats = {
        "total_restrooms": db.query(Restroom).count(),
        "active_restrooms": db.query(Restroom).filter(Restroom.is_active == True).count(),
        "verified_restrooms": db.query(Restroom).filter(Restroom.is_verified == True).count(),
        "total_users": db.query(User).count(),
        "verified_users": db.query(User).filter(User.is_verified == True).count(),
        "total_reviews": db.query(Review).count(),
        "pending_reports": db.query(Report).filter(Report.status == "pending").count(),
        "resolved_reports": db.query(Report).filter(Report.status == "verified").count(),
        "restrooms_by_source": {
            source.value: db.query(Restroom).filter(Restroom.source == source.value).count()
            for source in RestroomSource
        },
        "average_rating": db.query(func.avg(Restroom.avg_overall)).scalar() or 0,
        "top_rated_restrooms": db.query(Restroom).filter(
            Restroom.review_count >= 5
        ).order_by(Restroom.avg_overall.desc()).limit(5).count()
    }

    return stats

# --- Image Upload Endpoint ---

@app.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload an image for reviews or restroom photos"""
    # Validate file type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )

    # Validate file size
    if hasattr(file, 'size') and file.size and file.size > MAX_UPLOAD_SIZE:
        max_mb = MAX_UPLOAD_SIZE / (1024 * 1024)
        raise HTTPException(status_code=400, detail=f"File too large (max {max_mb:.1f}MB)")

    # Generate unique filename
    file_extension = file.filename.split('.')[-1] if file.filename else 'jpg'
    unique_filename = f"{uuid.uuid4()}.{file_extension}"

    # In production, upload to S3 or cloud storage
    # For now, return a mock URL
    mock_url = f"https://storage.puper.app/images/{unique_filename}"

    # Award points for photo contribution
    current_user.points += POINTS_PHOTO_UPLOAD
    db.commit()

    # Log the upload
    logger.info(f"Image uploaded by user {current_user.username}: {mock_url}")

    return {
        "url": mock_url,
        "filename": unique_filename,
        "points_awarded": 5,
        "message": "Image uploaded successfully"
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
        reload=AUTO_RELOAD
    )
