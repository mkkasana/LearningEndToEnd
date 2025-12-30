# Design Document: Contribution Stats

## Overview

The Contribution Stats feature provides users with visibility into their genealogy contributions by displaying all Person records they have created, along with engagement metrics showing how many times each profile has been viewed. This feature consists of three main components:

1. **Profile View Tracking System**: Automatically records when users view person profiles
2. **Contribution Statistics API**: Retrieves and aggregates contribution data with view counts
3. **Contribution Stats UI**: Displays contributions in an intuitive dialog interface

The design follows the existing FastAPI + SQLModel architecture with a layered approach: Database Models → Repositories → Services → API Routes → Frontend Components.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  ContributionStatsDialog.tsx                           │ │
│  │  - Fetches contributions via API                       │ │
│  │  - Displays person list with view counts               │ │
│  │  - Shows formatted addresses and dates                 │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend API Layer                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  /api/v1/person/my-contributions                       │ │
│  │  /api/v1/person/{person_id}/relationships/with-details │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                             │
│  ┌──────────────────────┐  ┌──────────────────────────────┐│
│  │  PersonService       │  │ ProfileViewTrackingService   ││
│  │  - Get contributions │  │ - Record view events         ││
│  │  - Enrich with stats │  │ - Calculate view counts      ││
│  └──────────────────────┘  └──────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Repository Layer                            │
│  ┌──────────────────────┐  ┌──────────────────────────────┐│
│  │  PersonRepository    │  │ ProfileViewTrackingRepository││
│  │  - Query by creator  │  │ - CRUD operations            ││
│  │  - Join with address │  │ - Aggregate view counts      ││
│  └──────────────────────┘  └──────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   person     │  │person_address│  │profile_view_     │  │
│  │              │  │              │  │tracking          │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```


### Data Flow

#### Recording Profile Views

```
User clicks on person → GET /person/{id}/relationships/with-details
                                    ↓
                        Extract current_user.id and person_id
                                    ↓
                        Get viewer's Person record (by user_id)
                                    ↓
                        Check: viewer != viewed person?
                                    ↓
                ProfileViewTrackingService.record_view()
                                    ↓
        Check for existing non-aggregated record (viewer + viewed)
                                    ↓
        ┌───────────────────────────┴───────────────────────────┐
        │                                                         │
    Exists?                                                  Not exists?
        │                                                         │
        ▼                                                         ▼
Increment view_count                                    Create new record
Update last_viewed_at                                   view_count = 1
                                                        is_aggregated = false
```

#### Fetching Contribution Stats

```
User opens Contribution Stats Dialog → GET /person/my-contributions
                                                ↓
                            PersonService.get_my_contributions()
                                                ↓
                    Query persons WHERE created_by_user_id = current_user.id
                                                ↓
                            For each person, fetch:
                            - Person details
                            - Addresses (join person_address)
                            - View count (sum from profile_view_tracking)
                                                ↓
                            Format and return results
                            Sorted by view_count DESC
```

## Components and Interfaces

### Database Models

#### ProfileViewTracking Model

```python
# backend/app/db_models/profile_view_tracking.py

import uuid
from datetime import datetime
from sqlmodel import Field, SQLModel

class ProfileViewTracking(SQLModel, table=True):
    """Track profile view events for analytics."""
    
    __tablename__ = "profile_view_tracking"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier for the view record"
    )
    
    viewed_person_id: uuid.UUID = Field(
        foreign_key="person.id",
        index=True,
        description="Person whose profile was viewed"
    )
    
    viewer_person_id: uuid.UUID = Field(
        foreign_key="person.id",
        index=True,
        description="Person who viewed the profile"
    )
    
    view_count: int = Field(
        default=1,
        description="Number of times viewed (for aggregated records)"
    )
    
    last_viewed_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of most recent view"
    )
    
    is_aggregated: bool = Field(
        default=False,
        description="Whether this is an aggregated record"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Record creation timestamp"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Record last update timestamp"
    )
```


### Repository Layer

#### ProfileViewTrackingRepository

```python
# backend/app/repositories/profile_view_tracking_repository.py

import uuid
from datetime import datetime
from sqlmodel import Session, select, func
from app.db_models.profile_view_tracking import ProfileViewTracking
from app.repositories.base import BaseRepository

class ProfileViewTrackingRepository(BaseRepository[ProfileViewTracking]):
    """Repository for profile view tracking data access."""
    
    def __init__(self, session: Session):
        super().__init__(ProfileViewTracking, session)
    
    def get_non_aggregated_view(
        self, 
        viewer_person_id: uuid.UUID, 
        viewed_person_id: uuid.UUID
    ) -> ProfileViewTracking | None:
        """Get existing non-aggregated view record for viewer-viewed pair."""
        statement = select(ProfileViewTracking).where(
            ProfileViewTracking.viewer_person_id == viewer_person_id,
            ProfileViewTracking.viewed_person_id == viewed_person_id,
            ProfileViewTracking.is_aggregated == False
        )
        return self.session.exec(statement).first()
    
    def get_total_views_for_person(self, person_id: uuid.UUID) -> int:
        """Get total view count for a person (sum of all view_count)."""
        statement = select(func.sum(ProfileViewTracking.view_count)).where(
            ProfileViewTracking.viewed_person_id == person_id
        )
        result = self.session.exec(statement).first()
        return result if result is not None else 0
    
    def get_total_views_for_persons(
        self, 
        person_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, int]:
        """Get total view counts for multiple persons."""
        statement = select(
            ProfileViewTracking.viewed_person_id,
            func.sum(ProfileViewTracking.view_count).label("total_views")
        ).where(
            ProfileViewTracking.viewed_person_id.in_(person_ids)
        ).group_by(
            ProfileViewTracking.viewed_person_id
        )
        
        results = self.session.exec(statement).all()
        return {person_id: total_views for person_id, total_views in results}
```

#### PersonRepository Extensions

```python
# backend/app/repositories/person/person_repository.py

# Add this method to existing PersonRepository class

def get_by_creator(self, creator_user_id: uuid.UUID) -> list[Person]:
    """Get all persons created by a specific user."""
    statement = select(Person).where(
        Person.created_by_user_id == creator_user_id
    )
    return list(self.session.exec(statement).all())
```


### Service Layer

#### ProfileViewTrackingService

```python
# backend/app/services/profile_view_tracking_service.py

import logging
import uuid
from datetime import datetime
from sqlmodel import Session
from app.db_models.profile_view_tracking import ProfileViewTracking
from app.repositories.profile_view_tracking_repository import ProfileViewTrackingRepository

logger = logging.getLogger(__name__)

class ProfileViewTrackingService:
    """Service for profile view tracking business logic."""
    
    def __init__(self, session: Session):
        self.repo = ProfileViewTrackingRepository(session)
        self.session = session
    
    def record_view(
        self, 
        viewer_person_id: uuid.UUID, 
        viewed_person_id: uuid.UUID
    ) -> None:
        """
        Record a profile view event.
        
        If a non-aggregated record exists for this viewer-viewed pair,
        increment the count. Otherwise, create a new record.
        """
        try:
            # Don't record self-views
            if viewer_person_id == viewed_person_id:
                logger.debug(f"Skipping self-view for person {viewer_person_id}")
                return
            
            # Check for existing non-aggregated record
            existing = self.repo.get_non_aggregated_view(
                viewer_person_id, 
                viewed_person_id
            )
            
            if existing:
                # Increment existing record
                existing.view_count += 1
                existing.last_viewed_at = datetime.utcnow()
                existing.updated_at = datetime.utcnow()
                self.repo.update(existing)
                logger.info(
                    f"Incremented view count to {existing.view_count} "
                    f"for person {viewed_person_id} by {viewer_person_id}"
                )
            else:
                # Create new record
                view_record = ProfileViewTracking(
                    viewer_person_id=viewer_person_id,
                    viewed_person_id=viewed_person_id,
                    view_count=1,
                    is_aggregated=False
                )
                self.repo.create(view_record)
                logger.info(
                    f"Created new view record for person {viewed_person_id} "
                    f"by {viewer_person_id}"
                )
        
        except Exception as e:
            # Log error but don't fail the request
            logger.error(
                f"Error recording profile view: {e}",
                exc_info=True
            )
    
    def get_total_views(self, person_id: uuid.UUID) -> int:
        """Get total view count for a person."""
        return self.repo.get_total_views_for_person(person_id)
    
    def get_total_views_bulk(
        self, 
        person_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, int]:
        """Get total view counts for multiple persons."""
        if not person_ids:
            return {}
        return self.repo.get_total_views_for_persons(person_ids)
```


#### PersonService Extensions

```python
# backend/app/services/person/person_service.py

# Add these methods to existing PersonService class

from app.services.profile_view_tracking_service import ProfileViewTrackingService
from app.repositories.address.person_address_repository import PersonAddressRepository

def get_my_contributions(
    self, 
    user_id: uuid.UUID
) -> list[dict]:
    """
    Get all persons created by the user with view statistics.
    
    Returns list of dicts with person details, addresses, and view counts.
    Sorted by view count descending (most viewed first).
    """
    # Get all persons created by this user
    persons = self.person_repo.get_by_creator(user_id)
    
    if not persons:
        return []
    
    # Get person IDs for bulk operations
    person_ids = [p.id for p in persons]
    
    # Get view counts for all persons
    view_tracking_service = ProfileViewTrackingService(self.person_repo.session)
    view_counts = view_tracking_service.get_total_views_bulk(person_ids)
    
    # Get addresses for all persons
    address_repo = PersonAddressRepository(self.person_repo.session)
    
    # Build result list
    results = []
    for person in persons:
        # Get addresses for this person
        addresses = address_repo.get_by_person_id(person.id)
        address_str = self._format_addresses(addresses)
        
        # Get view count (default to 0 if no views)
        view_count = view_counts.get(person.id, 0)
        
        results.append({
            "id": person.id,
            "first_name": person.first_name,
            "last_name": person.last_name,
            "date_of_birth": person.date_of_birth,
            "date_of_death": person.date_of_death,
            "is_active": person.is_active if hasattr(person, 'is_active') else True,
            "address": address_str,
            "total_views": view_count,
            "created_at": person.created_at
        })
    
    # Sort by view count descending
    results.sort(key=lambda x: x["total_views"], reverse=True)
    
    return results

def _format_addresses(self, addresses: list) -> str:
    """Format addresses as comma-separated string."""
    if not addresses:
        return ""
    
    address_parts = []
    for addr in addresses:
        parts = []
        if addr.address_line1:
            parts.append(addr.address_line1)
        if addr.city:
            parts.append(addr.city)
        if addr.state:
            parts.append(addr.state)
        if addr.country:
            parts.append(addr.country)
        
        if parts:
            address_parts.append(" ".join(parts))
    
    return ", ".join(address_parts)
```


### API Schema Layer

#### Response Schemas

```python
# backend/app/schemas/person/person_contribution.py

from datetime import date, datetime
import uuid
from pydantic import BaseModel

class PersonContributionPublic(BaseModel):
    """Schema for person contribution with statistics."""
    
    id: uuid.UUID
    first_name: str
    last_name: str
    date_of_birth: date
    date_of_death: date | None
    is_active: bool
    address: str
    total_views: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class PersonContributionsResponse(BaseModel):
    """Response schema for contributions list."""
    
    contributions: list[PersonContributionPublic]
    total_count: int
```


### API Routes

#### Contribution Stats Endpoint

```python
# backend/app/api/routes/person/person.py

# Add this endpoint to existing person router

@router.get("/my-contributions", response_model=list[PersonContributionPublic])
@log_route
def get_my_contributions(
    session: SessionDep, 
    current_user: CurrentUser
) -> Any:
    """
    Get all persons created by the current user with view statistics.
    
    Returns list of contributed persons with:
    - Person details (name, dates, status)
    - Formatted address
    - Total view count
    
    Results are sorted by view count descending (most viewed first).
    """
    person_service = PersonService(session)
    contributions = person_service.get_my_contributions(current_user.id)
    
    logger.info(
        f"Retrieved {len(contributions)} contributions for user {current_user.email}"
    )
    
    return contributions
```

#### Profile View Recording Hook

```python
# backend/app/api/routes/person/person.py

# Modify existing endpoint to add view tracking

@router.get(
    "/{person_id}/relationships/with-details",
    response_model=PersonRelationshipsWithDetailsResponse,
)
def get_person_relationships_with_details(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
) -> Any:
    """
    Get all relationships for a specific person with full person details.
    
    This endpoint also records a profile view event for analytics.
    """
    from app.schemas.person.person_relationship import (
        PersonDetails,
        PersonRelationshipsWithDetailsResponse,
    )
    from app.services.profile_view_tracking_service import ProfileViewTrackingService

    person_service = PersonService(session)

    # Verify the person exists
    person = person_service.person_repo.get_by_id(person_id)
    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person not found",
        )

    # Record profile view (async, non-blocking)
    try:
        viewer_person = person_service.get_person_by_user_id(current_user.id)
        if viewer_person:
            view_tracking_service = ProfileViewTrackingService(session)
            view_tracking_service.record_view(
                viewer_person_id=viewer_person.id,
                viewed_person_id=person_id
            )
    except Exception as e:
        # Log but don't fail the request
        logger.error(f"Failed to record profile view: {e}", exc_info=True)

    # Continue with normal relationship retrieval
    relationship_service = PersonRelationshipService(session)
    relationships = relationship_service.get_relationships_by_person(person_id)

    # Enrich each relationship with person details
    result = []
    for rel in relationships:
        related_person = person_service.person_repo.get_by_id(rel.related_person_id)
        if related_person:
            result.append(
                PersonRelationshipWithDetails(
                    relationship=rel,
                    person=PersonDetails(**related_person.model_dump()),
                )
            )

    return PersonRelationshipsWithDetailsResponse(
        selected_person=PersonDetails(**person.model_dump()), 
        relationships=result
    )
```


## Data Models

### Database Schema

#### profile_view_tracking Table

```sql
CREATE TABLE profile_view_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    viewed_person_id UUID NOT NULL,
    viewer_person_id UUID NOT NULL,
    view_count INTEGER NOT NULL DEFAULT 1,
    last_viewed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_aggregated BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT fk_viewed_person 
        FOREIGN KEY (viewed_person_id) 
        REFERENCES person(id) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_viewer_person 
        FOREIGN KEY (viewer_person_id) 
        REFERENCES person(id) 
        ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_profile_view_tracking_viewed_person 
    ON profile_view_tracking(viewed_person_id);

CREATE INDEX idx_profile_view_tracking_viewer_person 
    ON profile_view_tracking(viewer_person_id);

CREATE INDEX idx_profile_view_tracking_composite 
    ON profile_view_tracking(viewed_person_id, viewer_person_id, is_aggregated);
```

### Alembic Migration

```python
# backend/app/alembic/versions/xxxx_add_profile_view_tracking.py

"""Add profile view tracking table

Revision ID: xxxx
Revises: yyyy
Create Date: 2024-xx-xx

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'xxxx'
down_revision = 'yyyy'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create profile_view_tracking table
    op.create_table(
        'profile_view_tracking',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('viewed_person_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('viewer_person_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('last_viewed_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('is_aggregated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['viewed_person_id'], ['person.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['viewer_person_id'], ['person.id'], ondelete='CASCADE'),
    )
    
    # Create indexes
    op.create_index(
        'idx_profile_view_tracking_viewed_person',
        'profile_view_tracking',
        ['viewed_person_id']
    )
    op.create_index(
        'idx_profile_view_tracking_viewer_person',
        'profile_view_tracking',
        ['viewer_person_id']
    )
    op.create_index(
        'idx_profile_view_tracking_composite',
        'profile_view_tracking',
        ['viewed_person_id', 'viewer_person_id', 'is_aggregated']
    )

def downgrade() -> None:
    op.drop_index('idx_profile_view_tracking_composite')
    op.drop_index('idx_profile_view_tracking_viewer_person')
    op.drop_index('idx_profile_view_tracking_viewed_person')
    op.drop_table('profile_view_tracking')
```


## Frontend Components

### ContributionStatsDialog Component

```typescript
// frontend/src/components/Profile/ContributionStatsDialog.tsx

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Loader2, Eye, MapPin, Calendar } from 'lucide-react';
import { PersonContributionPublic } from '@/client';
import { PersonService } from '@/client/services';

interface ContributionStatsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ContributionStatsDialog({
  open,
  onOpenChange,
}: ContributionStatsDialogProps) {
  const [contributions, setContributions] = useState<PersonContributionPublic[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      fetchContributions();
    }
  }, [open]);

  const fetchContributions = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await PersonService.getMyContributions();
      setContributions(data);
    } catch (err) {
      setError('Failed to load contributions');
      console.error('Error fetching contributions:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDateRange = (birthDate: string, deathDate: string | null) => {
    const birthYear = new Date(birthDate).getFullYear();
    if (deathDate) {
      const deathYear = new Date(deathDate).getFullYear();
      return `${birthYear} - ${deathYear}`;
    }
    return `${birthYear}`;
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>My Contribution Stats</DialogTitle>
        </DialogHeader>

        {loading && (
          <div className="flex justify-center items-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        )}

        {error && (
          <div className="text-center py-8 text-red-500">
            {error}
          </div>
        )}

        {!loading && !error && contributions.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            <p>You haven't created any person profiles yet.</p>
            <p className="text-sm mt-2">
              Start building your family tree to see your contributions here.
            </p>
          </div>
        )}

        {!loading && !error && contributions.length > 0 && (
          <div className="space-y-4">
            <div className="text-sm text-muted-foreground mb-4">
              Total contributions: {contributions.length}
            </div>

            {contributions.map((person) => (
              <div
                key={person.id}
                className="border rounded-lg p-4 hover:bg-accent/50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    {/* Name and Status */}
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-semibold text-lg">
                        {person.first_name} {person.last_name}
                      </h3>
                      <div
                        className={`w-3 h-3 rounded-full ${
                          person.is_active
                            ? 'bg-green-500'
                            : 'bg-gray-300 border border-gray-400'
                        }`}
                        title={person.is_active ? 'Active' : 'Deactivated'}
                      />
                    </div>

                    {/* Date Range */}
                    <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
                      <Calendar className="h-4 w-4" />
                      <span>
                        {formatDateRange(person.date_of_birth, person.date_of_death)}
                      </span>
                    </div>

                    {/* Address */}
                    {person.address && (
                      <div className="flex items-start gap-2 text-sm text-muted-foreground mb-2">
                        <MapPin className="h-4 w-4 mt-0.5 flex-shrink-0" />
                        <span>{person.address}</span>
                      </div>
                    )}
                  </div>

                  {/* View Count */}
                  <div className="flex items-center gap-2 ml-4">
                    <Badge variant="secondary" className="flex items-center gap-1">
                      <Eye className="h-4 w-4" />
                      <span>{person.total_views}</span>
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
```


### Navigation Integration

```typescript
// Add to frontend/src/components/UserMenu.tsx or similar

import { ContributionStatsDialog } from '@/components/Profile/ContributionStatsDialog';

// In the menu items:
<DropdownMenuItem onClick={() => setContributionStatsOpen(true)}>
  <BarChart className="mr-2 h-4 w-4" />
  <span>Contribution Stats</span>
</DropdownMenuItem>

// Add state and dialog:
const [contributionStatsOpen, setContributionStatsOpen] = useState(false);

<ContributionStatsDialog
  open={contributionStatsOpen}
  onOpenChange={setContributionStatsOpen}
/>
```

### API Client Service

```typescript
// frontend/src/client/services/PersonService.ts

// Add this method to PersonService

export async function getMyContributions(): Promise<PersonContributionPublic[]> {
  const response = await request({
    url: '/api/v1/person/my-contributions',
    method: 'GET',
  });
  return response.data;
}
```

### TypeScript Types

```typescript
// frontend/src/client/types.gen.ts

export interface PersonContributionPublic {
  id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  date_of_death: string | null;
  is_active: boolean;
  address: string;
  total_views: number;
  created_at: string;
}
```


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Contribution Query Correctness
*For any* user and any set of person records in the database, querying contributions for that user should return exactly the persons where created_by_user_id matches the user's ID, and no others.

**Validates: Requirements 1.1**

### Property 2: Name Display Format
*For any* person record with first_name and last_name, the displayed name should contain both the first_name and last_name in the correct order.

**Validates: Requirements 1.2**

### Property 3: Address Formatting
*For any* person with multiple addresses, the formatted address string should contain all address components separated by commas.

**Validates: Requirements 1.3, 5.3**

### Property 4: Date Range Formatting for Living Persons
*For any* person where date_of_death is NULL, the displayed date range should show only the birth year.

**Validates: Requirements 1.4**

### Property 5: Date Range Formatting for Deceased Persons
*For any* person where date_of_death is NOT NULL, the displayed date range should show birth year hyphen death year.

**Validates: Requirements 1.5**

### Property 6: Status Indicator Presence
*For any* person record, the display should include an indicator of whether the person is active or deactivated based on the is_active field.

**Validates: Requirements 1.6**

### Property 7: View Recording on Endpoint Call
*For any* valid person_id and authenticated user with a person record, calling GET /person/{person_id}/relationships/with-details should create or update a profile view record.

**Validates: Requirements 3.1**

### Property 8: Correct Viewer and Viewed Mapping
*For any* profile view event, the viewer_person_id should match the logged-in user's person record, and the viewed_person_id should match the person_id from the URL parameter.

**Validates: Requirements 3.2, 3.3**

### Property 9: First View Creates New Record
*For any* viewer-viewed pair that has no existing non-aggregated record, recording a view should create a new profile_view_tracking record with view_count equal to 1.

**Validates: Requirements 3.6**

### Property 10: Subsequent Views Increment Count
*For any* viewer-viewed pair that has an existing non-aggregated record, recording another view should increment the view_count by 1 and update the last_viewed_at timestamp.

**Validates: Requirements 3.7**

### Property 11: Error Resilience
*For any* error that occurs during profile view recording, the system should log the error and continue processing the original request without throwing an exception.

**Validates: Requirements 3.8**

### Property 12: View Count Aggregation
*For any* person with multiple view records (both aggregated and non-aggregated), the total view count should equal the sum of all view_count values for that person.

**Validates: Requirements 4.2, 4.3**

### Property 13: View Statistics Response Format
*For any* list of person IDs, the view statistics response should be a mapping where each person_id maps to its total_view_count.

**Validates: Requirements 4.5**

### Property 14: Contributions API Response Completeness
*For any* contribution returned by the API, the response should include all required fields: id, first_name, last_name, date_of_birth, date_of_death, is_active, address, and total_views.

**Validates: Requirements 5.2, 5.3, 5.4**

### Property 15: Contributions Sorted by View Count
*For any* list of contributions returned by the API, the list should be sorted in descending order by total_view_count (most viewed first).

**Validates: Requirements 5.5**


## Error Handling

### Profile View Recording Errors

**Strategy**: Fail gracefully - never let view tracking errors break the main request

```python
try:
    view_tracking_service.record_view(viewer_id, viewed_id)
except Exception as e:
    logger.error(f"Failed to record profile view: {e}", exc_info=True)
    # Continue processing - don't raise
```

**Error Scenarios**:
1. **Database connection failure**: Log error, continue
2. **Invalid person IDs**: Log warning, continue
3. **Constraint violations**: Log error, continue
4. **Transaction conflicts**: Retry once, then log and continue

### Contribution Query Errors

**Strategy**: Return appropriate HTTP status codes with clear messages

**Error Scenarios**:
1. **User not authenticated**: 401 Unauthorized
2. **User has no person record**: Return empty list (not an error)
3. **Database query failure**: 500 Internal Server Error with generic message
4. **Invalid pagination parameters**: 400 Bad Request

### View Statistics Errors

**Strategy**: Return partial results when possible

**Error Scenarios**:
1. **Some person IDs invalid**: Return stats for valid IDs, omit invalid ones
2. **Database aggregation failure**: 500 Internal Server Error
3. **Empty person ID list**: Return empty dict (not an error)

## Testing Strategy

### Unit Tests

Unit tests will verify specific examples, edge cases, and error conditions:

**PersonService Tests**:
- Test `get_my_contributions()` with user who has no contributions
- Test `get_my_contributions()` with user who has multiple contributions
- Test `_format_addresses()` with empty address list
- Test `_format_addresses()` with single address
- Test `_format_addresses()` with multiple addresses

**ProfileViewTrackingService Tests**:
- Test `record_view()` with self-view (should not record)
- Test `record_view()` with first view (creates new record)
- Test `record_view()` with subsequent view (increments count)
- Test `record_view()` with database error (should not raise)
- Test `get_total_views()` with person who has no views
- Test `get_total_views_bulk()` with empty list

**Repository Tests**:
- Test `get_by_creator()` with user who created no persons
- Test `get_non_aggregated_view()` with non-existent pair
- Test `get_total_views_for_person()` with mixed aggregated/non-aggregated records

### Property-Based Tests

Property-based tests will verify universal properties across all inputs. Each test should run a minimum of 100 iterations.

**Test Configuration**: Use `pytest` with `hypothesis` library for property-based testing.

**Property Test 1: Contribution Query Correctness**
- Generate random users and person records
- Assign random created_by_user_id values
- Query contributions for a specific user
- Verify all returned persons have matching created_by_user_id
- **Feature: contribution-stats, Property 1: Contribution Query Correctness**

**Property Test 2: Name Display Format**
- Generate random person records with various first/last names
- Format the display name
- Verify both first_name and last_name appear in result
- **Feature: contribution-stats, Property 2: Name Display Format**

**Property Test 3: Address Formatting**
- Generate random persons with 0-5 addresses each
- Format addresses
- Verify comma separation and all address components present
- **Feature: contribution-stats, Property 3: Address Formatting**

**Property Test 4: Date Range Formatting (Living)**
- Generate random persons with date_of_death = NULL
- Format date range
- Verify only birth year appears (no hyphen or death year)
- **Feature: contribution-stats, Property 4: Date Range Formatting for Living Persons**

**Property Test 5: Date Range Formatting (Deceased)**
- Generate random persons with date_of_death NOT NULL
- Format date range
- Verify format is "birth_year - death_year"
- **Feature: contribution-stats, Property 5: Date Range Formatting for Deceased Persons**

**Property Test 6: View Recording Creates or Updates**
- Generate random viewer-viewed pairs
- Record views multiple times
- Verify first view creates record with count=1
- Verify subsequent views increment count
- **Feature: contribution-stats, Property 9 & 10: View Record Creation and Increment**

**Property Test 7: View Count Aggregation**
- Generate random person with multiple view records
- Mix aggregated (is_aggregated=true) and non-aggregated records
- Calculate total views
- Verify sum equals sum of all view_count values
- **Feature: contribution-stats, Property 12: View Count Aggregation**

**Property Test 8: Contributions Sorting**
- Generate random contributions with various view counts
- Retrieve contributions
- Verify list is sorted by total_views descending
- **Feature: contribution-stats, Property 15: Contributions Sorted by View Count**

### Integration Tests

Integration tests will verify end-to-end workflows:

1. **Full Contribution Flow**:
   - Create user and person
   - Create multiple family members
   - Call `/my-contributions` endpoint
   - Verify all created persons returned with correct data

2. **View Tracking Flow**:
   - Create two users with persons
   - User A views User B's person profile
   - Verify view record created
   - User A views again
   - Verify view count incremented

3. **Contribution Stats with Views**:
   - Create user with multiple contributed persons
   - Have other users view those persons
   - Call `/my-contributions`
   - Verify view counts are correct and sorted


## Performance Considerations

### Database Query Optimization

1. **Indexes**: 
   - Composite index on `(viewed_person_id, viewer_person_id, is_aggregated)` for fast lookups
   - Individual indexes on `viewed_person_id` and `viewer_person_id` for aggregation queries

2. **Bulk Operations**:
   - Use `get_total_views_bulk()` to fetch view counts for multiple persons in a single query
   - Avoid N+1 queries by fetching all addresses in bulk

3. **Query Limits**:
   - Consider pagination for users with many contributions (>100)
   - Limit view statistics queries to reasonable batch sizes

### Caching Strategy

**View Counts**: Consider caching view counts with short TTL (5-10 minutes)
```python
@cache(ttl=300)  # 5 minutes
def get_total_views(person_id: uuid.UUID) -> int:
    return self.repo.get_total_views_for_person(person_id)
```

**Contributions List**: Cache per user with medium TTL (30 minutes)
```python
@cache(key="contributions:{user_id}", ttl=1800)  # 30 minutes
def get_my_contributions(user_id: uuid.UUID) -> list[dict]:
    # ... implementation
```

**Cache Invalidation**:
- Invalidate contribution cache when user creates new person
- Invalidate view count cache when view is recorded (or accept eventual consistency)

### Aggregation Strategy (Future)

**Problem**: As view records accumulate, the table grows and queries slow down

**Solution**: Periodic aggregation job

```python
# Pseudo-code for aggregation job
def aggregate_view_records():
    """
    Consolidate multiple non-aggregated records into single aggregated records.
    Run daily or hourly depending on traffic.
    """
    # Find all non-aggregated records older than 24 hours
    old_records = get_non_aggregated_records(older_than=24_hours)
    
    # Group by (viewer_person_id, viewed_person_id)
    grouped = group_by_viewer_viewed_pair(old_records)
    
    for (viewer_id, viewed_id), records in grouped.items():
        # Sum view counts
        total_count = sum(r.view_count for r in records)
        latest_view = max(r.last_viewed_at for r in records)
        
        # Create aggregated record
        create_aggregated_record(
            viewer_id=viewer_id,
            viewed_id=viewed_id,
            view_count=total_count,
            last_viewed_at=latest_view,
            is_aggregated=True
        )
        
        # Delete old non-aggregated records
        delete_records(records)
```

**Benefits**:
- Keeps table size manageable
- Maintains query performance
- Preserves total view counts
- Allows for historical analysis if needed

## Security Considerations

### Authorization

1. **Contribution Access**: Users can only see their own contributions
   - Verify `current_user.id` matches query parameter
   - No admin override needed (privacy-focused)

2. **View Recording**: Only authenticated users with person records can generate views
   - Check `current_user` is authenticated
   - Verify user has associated person record
   - Prevent anonymous view tracking

3. **Profile Viewing**: Respect existing person profile access controls
   - Don't expose view tracking to unauthorized users
   - View counts only visible to person creator

### Data Privacy

1. **Viewer Identity**: View records store person IDs, not user IDs
   - Maintains separation between auth and demographic data
   - Allows for future multi-user person management

2. **Aggregation**: Aggregated records preserve privacy
   - Individual view timestamps are lost after aggregation
   - Only total counts remain

3. **GDPR Compliance**:
   - View records deleted when person is deleted (CASCADE)
   - Users can request view data deletion
   - View tracking can be disabled per user (future enhancement)

## Deployment Considerations

### Database Migration

1. **Run migration**: `alembic upgrade head`
2. **Verify indexes**: Check that all indexes were created
3. **Test queries**: Run sample queries to verify performance

### Rollback Plan

If issues arise:
1. **Disable view tracking**: Comment out view recording code in endpoint
2. **Revert migration**: `alembic downgrade -1`
3. **Monitor**: Check for any orphaned records

### Monitoring

**Metrics to Track**:
- View recording success/failure rate
- Average view count per person
- Contribution query response time
- Profile view tracking table size
- Cache hit/miss rates

**Alerts**:
- View recording error rate > 5%
- Contribution query time > 2 seconds
- Profile view tracking table > 10M rows (time to aggregate)

## Future Enhancements

1. **View Trends**: Track views over time for trend analysis
2. **Most Viewed Profiles**: Leaderboard of most viewed persons
3. **Viewer Demographics**: Show who is viewing profiles (with privacy controls)
4. **Export**: Allow users to export contribution stats to CSV/PDF
5. **Notifications**: Notify users when their contributions reach view milestones
6. **Aggregation Job**: Implement automated aggregation script
7. **Real-time Updates**: Use WebSockets to update view counts in real-time
8. **Privacy Controls**: Allow users to opt-out of view tracking
