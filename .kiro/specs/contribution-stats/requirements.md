# Requirements Document: Contribution Stats

## Introduction

This feature enables users to view their contributions to the family tree system by displaying all persons they have created, along with profile view statistics for each person. This provides users with insights into their genealogy work and the engagement their contributed profiles receive.

## Glossary

- **User**: An authenticated account holder in the system
- **Person**: A demographic record representing an individual (may or may not have a User account)
- **Contributor**: A User who has created Person records
- **Profile_View**: An event when a Person's profile is accessed by another User
- **Viewer**: The Person associated with the User who views another Person's profile
- **Viewed_Person**: The Person whose profile is being accessed
- **Profile_View_Tracking_Table**: Database table storing individual profile view events
- **Aggregated_View**: A consolidated view count combining multiple individual view events
- **Contribution_Stats_Dialog**: UI component displaying the user's created persons and their statistics
- **Active_Person**: A Person record with is_active status
- **Deactivated_Person**: A Person record that has been marked inactive

## Requirements

### Requirement 1: View Contributed Persons List

**User Story:** As a user, I want to see all persons I have created, so that I can track my contributions to the family tree.

#### Acceptance Criteria

1. WHEN a user requests their contribution stats, THE System SHALL retrieve all Person records where created_by_user_id matches the user's ID
2. WHEN displaying a contributed person, THE System SHALL show first_name concatenated with last_name
3. WHEN displaying a contributed person, THE System SHALL show comma-separated address information
4. WHEN a contributed person is alive (date_of_death is NULL), THE System SHALL display only the birth year
5. WHEN a contributed person is deceased (date_of_death is NOT NULL), THE System SHALL display birth year hyphen death year
6. WHEN displaying a contributed person, THE System SHALL indicate whether the person is active or deactivated
7. WHEN the contributed persons list is empty, THE System SHALL display an appropriate empty state message

### Requirement 2: Profile View Tracking

**User Story:** As a system administrator, I want to track profile views, so that users can see engagement metrics for their contributed persons.

#### Acceptance Criteria

1. THE System SHALL create a profile_view_tracking table with id (UUID), viewed_person_id (UUID), viewer_person_id (UUID), view_count (integer), last_viewed_at (timestamp), is_aggregated (boolean), created_at (timestamp), and updated_at (timestamp)
2. WHEN the profile_view_tracking table is created, THE System SHALL add a foreign key constraint from viewed_person_id to person.id
3. WHEN the profile_view_tracking table is created, THE System SHALL add a foreign key constraint from viewer_person_id to person.id
4. WHEN the profile_view_tracking table is created, THE System SHALL add an index on viewed_person_id for query performance
5. WHEN the profile_view_tracking table is created, THE System SHALL add an index on viewer_person_id for query performance
6. WHEN the profile_view_tracking table is created, THE System SHALL add a composite index on (viewed_person_id, viewer_person_id, is_aggregated)
7. WHEN a profile_view_tracking record is created, THE System SHALL set is_aggregated to false by default
8. WHEN a profile_view_tracking record is created, THE System SHALL set view_count to 1 by default

### Requirement 3: Automatic Profile View Recording

**User Story:** As a user, I want profile views to be tracked automatically, so that I can see which profiles are being viewed without manual intervention.

#### Acceptance Criteria

1. WHEN the endpoint GET /api/v1/person/{person_id}/relationships/with-details is invoked, THE System SHALL record a profile view event
2. WHEN recording a profile view, THE System SHALL identify the viewer as the Person record associated with the current user's user_id
3. WHEN recording a profile view, THE System SHALL identify the viewed person as the person_id from the URL parameter
4. WHEN a user views their own profile, THE System SHALL NOT record a profile view event
5. WHEN the viewer has no associated Person record, THE System SHALL NOT record a profile view event
6. WHEN recording a profile view for a viewer-viewed pair that has no existing non-aggregated record, THE System SHALL create a new profile_view_tracking record with view_count set to 1
7. WHEN recording a profile view for a viewer-viewed pair that has an existing non-aggregated record, THE System SHALL increment the view_count by 1 and update last_viewed_at
8. IF an error occurs during profile view recording, THEN THE System SHALL log the error and continue processing the original request without failure

### Requirement 4: Profile View Statistics API

**User Story:** As a user, I want to retrieve view statistics for persons I created, so that I can see engagement metrics in the contribution stats dialog.

#### Acceptance Criteria

1. THE System SHALL provide an API endpoint to retrieve total view counts for a list of person IDs
2. WHEN calculating total views for a person, THE System SHALL sum all view_count values from profile_view_tracking where viewed_person_id matches the person ID
3. WHEN calculating total views, THE System SHALL include both aggregated and non-aggregated records
4. WHEN a person has no view records, THE System SHALL return a view count of zero
5. WHEN retrieving view statistics, THE System SHALL return results as a mapping of person_id to total_view_count
6. WHEN the person ID list is empty, THE System SHALL return an empty result set

### Requirement 5: Contribution Stats API Integration

**User Story:** As a user, I want to see view counts alongside my contributed persons, so that I can understand the engagement each profile receives.

#### Acceptance Criteria

1. THE System SHALL provide an API endpoint GET /api/v1/person/my-contributions that returns all persons created by the current user
2. WHEN retrieving contributions, THE System SHALL include person details (id, first_name, last_name, date_of_birth, date_of_death, is_active)
3. WHEN retrieving contributions, THE System SHALL include comma seperated address information for each person
4. WHEN retrieving contributions, THE System SHALL include total view count for each person
5. WHEN retrieving contributions, THE System SHALL order results by total_view_count descending (most viewed person first)
6. WHEN the user has created no persons, THE System SHALL return an empty list

### Requirement 6: Contribution Stats UI Component

**User Story:** As a user, I want a dedicated UI dialog for contribution stats, so that I can easily access and view my contributions.

#### Acceptance Criteria

1. THE System SHALL provide a "Contribution Stats" navigation option in the profile section
2. WHEN a user clicks "Contribution Stats", THE System SHALL open a dialog displaying their contributions
3. WHEN the contribution stats dialog opens, THE System SHALL fetch and display the user's contributed persons
4. WHEN displaying a person in the contribution stats, THE System SHALL show the full name (first + middle + last)
5. WHEN displaying a person in the contribution stats, THE System SHALL show the formatted address
6. WHEN displaying a person in the contribution stats, THE System SHALL show the birth-death year range or birth year only if alive
7. WHEN displaying a person in the contribution stats, THE System SHALL show the active/deactivated status (Green cricle vs shallow cricle)
8. WHEN displaying a person in the contribution stats, THE System SHALL show the total view count
9. WHEN the contribution stats are loading, THE System SHALL display a loading indicator
10. WHEN there are no contributions, THE System SHALL display a helpful empty state message

### Requirement 7: Repository and Service Layer

**User Story:** As a developer, I want well-structured repository and service layers for profile view tracking, so that the code is maintainable and testable.

#### Acceptance Criteria

1. THE System SHALL implement a ProfileViewTrackingRepository with methods for create, read, update, and query operations
2. THE System SHALL implement a ProfileViewTrackingService with business logic for recording and retrieving view statistics
3. WHEN the service records a view, THE System SHALL use the repository to check for existing non-aggregated records
4. WHEN the service retrieves statistics, THE System SHALL use the repository to aggregate view counts
5. THE System SHALL implement a PersonRepository method to retrieve persons by created_by_user_id
6. THE System SHALL implement a PersonService method to retrieve contributions with view statistics

### Requirement 8: Data Aggregation Preparation

**User Story:** As a system administrator, I want the system designed to support future data aggregation, so that the profile_view_tracking table remains performant as data grows.

#### Acceptance Criteria

1. THE System SHALL include an is_aggregated boolean field in the profile_view_tracking table
2. WHEN creating new view records, THE System SHALL set is_aggregated to false
3. THE System SHALL design the schema to support future aggregation where multiple non-aggregated records can be combined into a single aggregated record
4. WHEN querying for existing non-aggregated records, THE System SHALL filter by is_aggregated equals false
5. THE System SHALL document the aggregation strategy for future implementation

## Future Enhancements

The following features are planned for future releases:

1. **Automated Aggregation Script**: A scheduled job (hourly or daily) that consolidates multiple view records from the same viewer-viewed pair into aggregated records
2. **View Trends**: Time-series data showing view counts over time
3. **Most Viewed Profiles**: Ranking of contributed persons by view count
4. **Viewer Demographics**: Insights into who is viewing the contributed profiles
5. **Export Functionality**: Ability to export contribution statistics to CSV or PDF

## Technical Notes

### Database Schema

```sql
CREATE TABLE profile_view_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    viewed_person_id UUID NOT NULL REFERENCES person(id) ON DELETE CASCADE,
    viewer_person_id UUID NOT NULL REFERENCES person(id) ON DELETE CASCADE,
    view_count INTEGER NOT NULL DEFAULT 1,
    last_viewed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_aggregated BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_profile_view_tracking_viewed_person ON profile_view_tracking(viewed_person_id);
CREATE INDEX idx_profile_view_tracking_viewer_person ON profile_view_tracking(viewer_person_id);
CREATE INDEX idx_profile_view_tracking_composite ON profile_view_tracking(viewed_person_id, viewer_person_id, is_aggregated);
```

### API Endpoints

- `GET /api/v1/person/my-contributions` - Retrieve all persons created by current user with view statistics
- `POST /api/v1/profile-views/record` - Internal endpoint for recording profile views (called automatically)
- `GET /api/v1/profile-views/stats?person_ids=uuid1,uuid2` - Retrieve view statistics for specific persons

### Performance Considerations

- Use database indexes for efficient querying
- Implement pagination for large contribution lists
- Consider caching view counts for frequently accessed profiles
- Design aggregation strategy to keep table size manageable
