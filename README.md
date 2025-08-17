# Puper Backend API

**The Waze of Public Restrooms** - A state-of-the-art REST API for finding, rating, and reviewing public toilets worldwide.

## Features

- 🚽 **Restroom Management**: Add, search, and manage public restroom locations
- 📍 **Geospatial Search**: Find restrooms near your location with advanced filtering
- ⭐ **Rating System**: Comprehensive 5-star rating system for cleanliness, safety, accessibility, and more
- 👤 **User Authentication**: Secure JWT-based authentication system
- 🏆 **Gamification**: Badge system and points to encourage user participation
- ♿ **Accessibility**: Full support for accessibility information and filtering
- 📱 **Mobile-Ready**: RESTful API designed for mobile applications
- 🗺️ **Route Integration**: Find restrooms along your route with detour calculations

## Tech Stack

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with PostGIS for geospatial data
- **Caching**: Redis
- **Authentication**: JWT with bcrypt password hashing
- **ORM**: SQLAlchemy with Alembic migrations
- **Validation**: Pydantic models
- **Documentation**: Auto-generated OpenAPI/Swagger docs

## Quick Start

### Using Docker Compose (Recommended)

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd puper
   cp .env.example .env
   ```

2. **Start services**:
   ```bash
   docker-compose up -d
   ```

3. **Access the API**:
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

### Manual Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup PostgreSQL with PostGIS**:
   ```bash
   # Install PostgreSQL and PostGIS
   # Create database: puper
   # Enable PostGIS extension
   ```

3. **Setup Redis**:
   ```bash
   # Install and start Redis server
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your database and Redis URLs
   ```

5. **Run the application**:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

### Authentication
- `POST /register` - Register a new user
- `POST /token` - Login and get access token
- `GET /users/me` - Get current user info

### Restrooms
- `POST /restrooms` - Create a new restroom
- `GET /restrooms/{id}` - Get restroom details
- `POST /restrooms/search` - Search restrooms by location

### Reviews
- `POST /reviews` - Create a review
- `GET /restrooms/{id}/reviews` - Get restroom reviews

### Favorites
- `POST /favorites/{restroom_id}` - Add to favorites
- `DELETE /favorites/{restroom_id}` - Remove from favorites
- `GET /favorites` - Get user favorites

### Admin (Role-based Access)
- `GET /admin/dashboard` - Admin dashboard with statistics
- `GET /admin/users` - List and manage users
- `GET /admin/restrooms` - Manage restrooms and verification
- `GET /admin/reports` - Handle user reports
- `GET /admin/analytics` - Detailed analytics and insights
- `POST /admin/ingest/osm` - Trigger OpenStreetMap data import
- `GET /admin/stats` - System-wide statistics

### Image Upload
- `POST /upload/image` - Upload images for reviews/restrooms

## Database Schema

### Core Models
- **User**: User accounts with authentication and gamification
- **Restroom**: Restroom locations with geospatial data and amenities
- **Review**: User reviews with multi-dimensional ratings
- **Favorite**: User favorite restrooms
- **Report**: Issue reports for restrooms

### Key Features
- Geospatial indexing for fast location-based queries
- Cached rating aggregates for performance
- Comprehensive amenity and accessibility tracking
- Badge system for user engagement

## Configuration

Key environment variables:

```env
DATABASE_URL=postgresql://user:pass@localhost/puper
SECRET_KEY=your-secret-key
REDIS_URL=redis://localhost:6379
GOOGLE_MAPS_API_KEY=your-api-key
```

## Development

### Running Tests
```bash
pytest
```

### Database Migrations
```bash
# Using the migration helper (recommended)
python migrate.py create "Description of changes"
python migrate.py upgrade

# Or using Alembic directly
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

See [MIGRATIONS.md](MIGRATIONS.md) for detailed migration guide.

### Code Formatting
```bash
black .
isort .
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For support, please open an issue on GitHub or contact the development team.
