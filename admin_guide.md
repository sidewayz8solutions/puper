# Puper API - Admin Endpoints Guide

## Overview

The Puper API includes comprehensive admin endpoints for managing users, restrooms, reports, and analytics. Admin access is role-based with two levels:

- **Moderator**: Can manage restrooms and reports
- **Admin**: Full access to all admin functions including user management

## Authentication

All admin endpoints require authentication with appropriate role permissions:

```bash
# Login as admin user
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=adminpass"

# Use the returned token in subsequent requests
curl -H "Authorization: Bearer YOUR_TOKEN" "http://localhost:8000/admin/dashboard"
```

## Admin Dashboard

### GET /admin/dashboard
Get comprehensive dashboard statistics.

**Required Role**: Admin

**Response**:
```json
{
  "totals": {
    "users": 1250,
    "restrooms": 3400,
    "reviews": 8900,
    "pending_reports": 15,
    "unverified_restrooms": 45
  },
  "recent_activity": {
    "new_users_week": 23,
    "new_restrooms_week": 12,
    "new_reviews_week": 67
  },
  "top_contributors": [
    {
      "id": "user-id",
      "username": "poweruser",
      "points": 2500,
      "badges": 8
    }
  ]
}
```

## User Management

### GET /admin/users
List all users with filtering and pagination.

**Required Role**: Admin

**Query Parameters**:
- `skip`: Offset for pagination (default: 0)
- `limit`: Number of results (default: 50, max: 200)
- `search`: Search in username, email, or full name
- `role`: Filter by user role (user, moderator, admin, partner)

**Example**:
```bash
curl "http://localhost:8000/admin/users?search=john&role=user&limit=20"
```

### PATCH /admin/users/{user_id}
Update user information.

**Required Role**: Admin

**Allowed Fields**: `role`, `is_verified`, `points`, `badges`

**Example**:
```bash
curl -X PATCH "http://localhost:8000/admin/users/user-id" \
  -H "Content-Type: application/json" \
  -d '{"role": "moderator", "is_verified": true}'
```

### DELETE /admin/users/{user_id}
Soft delete a user by anonymizing their data.

**Required Role**: Admin

## Restroom Management

### GET /admin/restrooms
List restrooms for admin management.

**Required Role**: Moderator

**Query Parameters**:
- `skip`, `limit`: Pagination
- `status`: Filter by status (active, inactive, closed)
- `source`: Filter by source (user, osm, google, etc.)
- `verified`: Filter by verification status (true/false)

### PATCH /admin/restrooms/{restroom_id}
Update restroom status and information.

**Required Role**: Moderator

**Allowed Fields**: `is_verified`, `is_active`, `temporarily_closed`, `permanently_closed`, `name`, `description`, `address`, `city`, `country`

**Example**:
```bash
curl -X PATCH "http://localhost:8000/admin/restrooms/restroom-id" \
  -H "Content-Type: application/json" \
  -d '{"is_verified": true, "is_active": true}'
```

### DELETE /admin/restrooms/{restroom_id}
Permanently delete a restroom and all associated data.

**Required Role**: Admin

## Report Management

### GET /admin/reports
List all reports for admin review.

**Required Role**: Moderator

**Query Parameters**:
- `skip`, `limit`: Pagination
- `status`: Filter by status (pending, verified, rejected)
- `report_type`: Filter by report type (closed, out_of_order, incorrect_info, etc.)

### PATCH /admin/reports/{report_id}
Update report status.

**Required Role**: Moderator

**Body**: `{"status": "verified"}` (pending, verified, rejected)

## Analytics

### GET /admin/analytics
Get detailed analytics for specified time period.

**Required Role**: Admin

**Query Parameters**:
- `period`: Time period (week, month, quarter, year)

**Response includes**:
- User growth and activity metrics
- Restroom creation and verification stats
- Review volume and average ratings
- Report resolution metrics
- Top cities by restroom count

## Bulk Operations

### POST /admin/bulk/verify-restrooms
Bulk verify multiple restrooms.

**Required Role**: Admin

**Body**: `{"restroom_ids": ["id1", "id2", "id3"]}`

### POST /admin/bulk/close-restrooms
Bulk close multiple restrooms.

**Required Role**: Admin

**Body**: `{"restroom_ids": ["id1", "id2", "id3"]}`

## Data Ingestion

### POST /admin/ingest/osm
Trigger OpenStreetMap data ingestion to populate the database with real restroom data.

**Required Role**: Admin

**Query Parameters**:
- `bbox`: Bounding box coordinates (south,west,north,east)

**Example**:
```bash
curl -X POST "http://localhost:8000/admin/ingest/osm?bbox=40.7,-74.1,40.8,-74.0"
```

### GET /admin/stats
Get comprehensive system-wide statistics.

**Required Role**: Admin

**Response includes**:
- Total and active restroom counts
- User and review statistics
- Report status breakdown
- Restrooms by data source
- Average ratings and top-rated restrooms

## Image Upload

### POST /upload/image
Upload images for reviews or restroom photos.

**Required Role**: Any authenticated user

**Body**: Multipart form data with image file

**Supported formats**: JPEG, PNG, WebP (max 5MB)

**Example**:
```bash
curl -X POST "http://localhost:8000/upload/image" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@photo.jpg"
```

**Response**:
```json
{
  "url": "https://storage.puper.app/images/uuid.jpg",
  "filename": "uuid.jpg",
  "points_awarded": 5,
  "message": "Image uploaded successfully"
}
```

## Common Admin Tasks

### 1. Verify New User-Submitted Restrooms
```bash
# List unverified restrooms
curl "http://localhost:8000/admin/restrooms?verified=false&source=user"

# Verify a restroom
curl -X PATCH "http://localhost:8000/admin/restrooms/RESTROOM_ID" \
  -d '{"is_verified": true}'
```

### 2. Handle Reports
```bash
# List pending reports
curl "http://localhost:8000/admin/reports?status=pending"

# Verify a closure report
curl -X PATCH "http://localhost:8000/admin/reports/REPORT_ID" \
  -d '{"status": "verified"}'
```

### 3. Promote User to Moderator
```bash
curl -X PATCH "http://localhost:8000/admin/users/USER_ID" \
  -d '{"role": "moderator"}'
```

### 4. Get Weekly Analytics
```bash
curl "http://localhost:8000/admin/analytics?period=week"
```

### 5. Trigger OSM Data Import
```bash
curl -X POST "http://localhost:8000/admin/ingest/osm?bbox=40.7,-74.1,40.8,-74.0"
```

### 6. Upload Image for Review
```bash
curl -X POST "http://localhost:8000/upload/image" \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@restroom_photo.jpg"
```

## Complete Endpoint Reference

| Endpoint | Method | Role Required | Purpose |
|----------|--------|---------------|---------|
| `/admin/dashboard` | GET | Admin | Dashboard overview |
| `/admin/users` | GET | Admin | List/search users |
| `/admin/users/{id}` | PATCH | Admin | Update user |
| `/admin/users/{id}` | DELETE | Admin | Delete user |
| `/admin/restrooms` | GET | Moderator | List restrooms |
| `/admin/restrooms/{id}` | PATCH | Moderator | Update restroom |
| `/admin/restrooms/{id}` | DELETE | Admin | Delete restroom |
| `/admin/reports` | GET | Moderator | List reports |
| `/admin/reports/{id}` | PATCH | Moderator | Update report |
| `/admin/analytics` | GET | Admin | Detailed analytics |
| `/admin/bulk/verify-restrooms` | POST | Admin | Bulk verify |
| `/admin/bulk/close-restrooms` | POST | Admin | Bulk close |
| `/admin/ingest/osm` | POST | Admin | OSM data ingestion |
| `/admin/stats` | GET | Admin | System statistics |
| `/upload/image` | POST | User | Upload images |

## Error Handling

All admin endpoints return appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (invalid parameters)
- `401`: Unauthorized (no valid token)
- `403`: Forbidden (insufficient permissions)
- `404`: Not found
- `500`: Internal server error

## Rate Limiting

Admin endpoints may have different rate limits than public endpoints. Contact your system administrator for specific limits.

## Security Notes

- Admin tokens should be kept secure and rotated regularly
- All admin actions are logged for audit purposes
- Use HTTPS in production environments
- Consider IP whitelisting for admin access
