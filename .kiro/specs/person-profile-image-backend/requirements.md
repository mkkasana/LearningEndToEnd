# Requirements Document

## Introduction

This feature adds backend support for person profile image upload, compression, storage, retrieval, and deletion. The system uses a pluggable storage abstraction so that images are stored locally on the filesystem during development (`ENVIRONMENT=local`) and on AWS S3 in staging/production. Images are compressed and resized server-side using Pillow to keep storage costs low and load times fast.

## Glossary

- **Image_Upload_Service**: The backend service responsible for receiving, validating, compressing, and storing person profile images.
- **Storage_Backend**: An abstraction layer that provides a consistent interface for storing and retrieving files, with implementations for local filesystem and AWS S3.
- **Local_Storage**: A Storage_Backend implementation that saves files to the local filesystem and serves them via a FastAPI static endpoint.
- **S3_Storage**: A Storage_Backend implementation that uploads files to an AWS S3 bucket and returns CloudFront or S3 URLs.
- **Image_Processor**: A component that uses Pillow to validate, resize, and compress uploaded images into standardized formats.
- **Person**: The core database model representing a person in the family tree system.
- **Profile_Image_Key**: A string field on the Person model that stores the storage key (filename) of the person's profile image.

## Requirements

### Requirement 1: Storage Backend Abstraction

**User Story:** As a developer, I want a pluggable storage backend, so that I can use local filesystem storage during development and S3 in production without changing application code.

#### Acceptance Criteria

1. THE Storage_Backend SHALL define an interface with `upload`, `delete`, and `get_url` methods
2. WHEN `ENVIRONMENT` is set to `local`, THE Image_Upload_Service SHALL use Local_Storage to save files to a configurable local directory
3. WHEN `ENVIRONMENT` is set to `staging` or `production`, THE Image_Upload_Service SHALL use S3_Storage to upload files to a configured S3 bucket
4. THE Local_Storage SHALL save files to the `uploads/person-images/` directory relative to the backend application root
5. THE S3_Storage SHALL upload files to the S3 bucket specified by the `S3_IMAGES_BUCKET` configuration setting
6. WHEN `get_url` is called on Local_Storage, THE Local_Storage SHALL return a relative URL path in the format `/api/v1/uploads/person-images/{filename}`
7. WHEN `get_url` is called on S3_Storage, THE S3_Storage SHALL return the full CloudFront or S3 URL for the file

### Requirement 2: Image Processing and Compression

**User Story:** As a system operator, I want uploaded images to be automatically compressed and resized, so that storage costs remain low and images load quickly.

#### Acceptance Criteria

1. WHEN an image is uploaded, THE Image_Processor SHALL resize the image to fit within 400x400 pixels while maintaining the aspect ratio
2. WHEN an image is uploaded, THE Image_Processor SHALL generate a thumbnail variant that fits within 100x100 pixels while maintaining the aspect ratio
3. WHEN an image is processed, THE Image_Processor SHALL convert the image to JPEG format at 85% quality
4. WHEN an image is processed, THE Image_Processor SHALL strip EXIF metadata from the output image
5. IF the uploaded file is not a valid image (JPEG, PNG, or WebP), THEN THE Image_Processor SHALL raise a validation error with a descriptive message
6. IF the uploaded file exceeds 5 MB in size, THEN THE Image_Upload_Service SHALL reject the upload with a descriptive error message
7. THE Image_Processor SHALL produce two output files: a main image (max 400x400) and a thumbnail (max 100x100)
8. FOR ALL valid images, processing then reading back the processed image SHALL produce a valid JPEG file (round-trip property)

### Requirement 3: Person Profile Image API Endpoints

**User Story:** As a user, I want API endpoints to upload, retrieve, and delete profile images for persons, so that I can manage profile photos through the application.

#### Acceptance Criteria

1. WHEN an authenticated user uploads an image for a person they have access to, THE Image_Upload_Service SHALL store the image and update the Person record with the image key
2. WHEN an authenticated user requests a person's profile image URL, THE Image_Upload_Service SHALL return the URL for both the main image and the thumbnail
3. WHEN an authenticated user deletes a person's profile image, THE Image_Upload_Service SHALL remove the image files from storage and clear the Person record's image key
4. IF an unauthenticated user attempts to upload, retrieve, or delete a profile image, THEN THE Image_Upload_Service SHALL return a 401 Unauthorized response
5. IF a user attempts to upload an image for a person they do not have access to, THEN THE Image_Upload_Service SHALL return a 403 Forbidden response
6. WHEN an image is uploaded for a person that already has a profile image, THE Image_Upload_Service SHALL replace the existing image and clean up the old files
7. THE Image_Upload_Service SHALL generate a unique filename using UUID for each uploaded image to prevent filename collisions

### Requirement 4: Database Schema Update

**User Story:** As a developer, I want the Person model to store a reference to the profile image, so that the image can be associated with a person record.

#### Acceptance Criteria

1. THE Person model SHALL include a nullable `profile_image_key` field of type string
2. WHEN a profile image is uploaded, THE Image_Upload_Service SHALL set the `profile_image_key` field to the generated filename (without path prefix)
3. WHEN a profile image is deleted, THE Image_Upload_Service SHALL set the `profile_image_key` field to null
4. THE Alembic migration SHALL add the `profile_image_key` column to the existing `person` table without data loss

### Requirement 5: Local Development Serving

**User Story:** As a developer, I want uploaded images to be served directly by the backend during local development, so that I can test the full image flow without AWS credentials.

#### Acceptance Criteria

1. WHEN `ENVIRONMENT` is `local`, THE backend SHALL serve files from the `uploads/` directory via a static file endpoint at `/api/v1/uploads/`
2. WHEN `ENVIRONMENT` is `staging` or `production`, THE backend SHALL NOT mount the static file endpoint
3. THE Docker Compose configuration SHALL mount the `uploads/` directory as a volume so that uploaded files persist across container restarts

### Requirement 6: Configuration Settings

**User Story:** As a developer, I want image upload settings to be configurable via environment variables, so that I can adjust limits and storage locations per environment.

#### Acceptance Criteria

1. THE Settings class SHALL include `IMAGE_MAX_SIZE_MB` with a default value of 5
2. THE Settings class SHALL include `IMAGE_MAX_DIMENSION` with a default value of 400
3. THE Settings class SHALL include `IMAGE_THUMBNAIL_DIMENSION` with a default value of 100
4. THE Settings class SHALL include `IMAGE_QUALITY` with a default value of 85
5. THE Settings class SHALL include `S3_IMAGES_BUCKET` with a default value of empty string
6. THE Settings class SHALL include `CLOUDFRONT_IMAGES_URL` with a default value of empty string
7. WHEN `ENVIRONMENT` is `staging` or `production` and `S3_IMAGES_BUCKET` is empty, THE application SHALL log a warning at startup
