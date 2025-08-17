# PostGIS Setup Guide for Puper API

## Overview

The Puper API uses PostGIS for geospatial features like location-based searches and spatial indexing. This guide helps you install and configure PostGIS.

## Installation

### macOS (using Homebrew)

```bash
# Install PostGIS
brew install postgis

# If you already have PostgreSQL installed
brew install postgis

# Restart PostgreSQL service
brew services restart postgresql@16
```

### Ubuntu/Debian

```bash
# Install PostGIS
sudo apt-get update
sudo apt-get install postgresql-16-postgis-3

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### CentOS/RHEL

```bash
# Install PostGIS
sudo yum install postgis33_16

# Restart PostgreSQL
sudo systemctl restart postgresql-16
```

### Docker (Recommended for Development)

Use the official PostGIS Docker image:

```yaml
# In docker-compose.yml
services:
  postgres:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: puper
      POSTGRES_USER: puper_user
      POSTGRES_PASSWORD: puper_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

## Database Setup

### 1. Connect to your database

```bash
psql -h localhost -U puper_user -d puper
```

### 2. Create PostGIS extension

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

### 3. Verify installation

```sql
SELECT PostGIS_Version();
```

You should see output like: `3.3.2 USE_GEOS=1 USE_PROJ=1 USE_STATS=1`

## Update Migration for PostGIS

Once PostGIS is installed, you can update the migration to use proper geometry columns:

### 1. Create a new migration

```bash
python migrate.py create "Add PostGIS geometry column"
```

### 2. Edit the migration file

```python
def upgrade() -> None:
    # Add PostGIS geometry column
    op.execute("ALTER TABLE restrooms ADD COLUMN location_geom geometry(POINT, 4326)")
    
    # Update existing data
    op.execute("""
        UPDATE restrooms 
        SET location_geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """)
    
    # Add spatial index
    op.execute("CREATE INDEX idx_restrooms_location_geom ON restrooms USING GIST (location_geom)")
    
    # Make geometry column not null
    op.execute("ALTER TABLE restrooms ALTER COLUMN location_geom SET NOT NULL")

def downgrade() -> None:
    op.drop_index('idx_restrooms_location_geom')
    op.drop_column('restrooms', 'location_geom')
```

### 3. Apply the migration

```bash
python migrate.py upgrade
```

## Update Application Code

Once PostGIS is set up, update the model in `main.py`:

```python
from geoalchemy2 import Geometry

class Restroom(Base):
    # ... other columns ...
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    # ... rest of the model ...
```

## Troubleshooting

### Error: "extension postgis is not available"

This means PostGIS is not installed. Follow the installation steps above.

### Error: "could not access file"

PostGIS might not be properly installed. Try:

```bash
# macOS
brew reinstall postgis

# Ubuntu
sudo apt-get install --reinstall postgresql-16-postgis-3
```

### Permission Issues

Make sure your database user has the necessary permissions:

```sql
-- Connect as superuser
GRANT ALL PRIVILEGES ON DATABASE puper TO puper_user;
ALTER USER puper_user CREATEDB;
```

## Testing PostGIS

Test that PostGIS is working correctly:

```sql
-- Test basic geometry creation
SELECT ST_AsText(ST_MakePoint(-74.0060, 40.7128));

-- Test distance calculation
SELECT ST_Distance(
    ST_MakePoint(-74.0060, 40.7128)::geography,
    ST_MakePoint(-73.9857, 40.7484)::geography
);
```

## Production Considerations

### 1. Performance

- Always use spatial indexes: `CREATE INDEX USING GIST (location)`
- Use geography type for distance calculations
- Consider partitioning large tables by geographic regions

### 2. Backup

PostGIS data requires special consideration during backups:

```bash
# Backup with PostGIS
pg_dump -h hostname -U username -d database_name -f backup.sql

# Restore
psql -h hostname -U username -d database_name -f backup.sql
```

### 3. Monitoring

Monitor spatial query performance:

```sql
-- Check spatial index usage
EXPLAIN ANALYZE SELECT * FROM restrooms 
WHERE ST_DWithin(location::geography, ST_MakePoint(-74, 40)::geography, 1000);
```

## Next Steps

1. Install PostGIS using your preferred method
2. Create the PostGIS extension in your database
3. Run the migration to add proper geometry columns
4. Update your application code to use PostGIS features
5. Test geospatial queries

For more information, see the [PostGIS documentation](https://postgis.net/documentation/).
