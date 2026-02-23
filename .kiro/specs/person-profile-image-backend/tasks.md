# Implementation Plan: Person Profile Image Backend

## Overview

Backend implementation for person profile image upload, processing, and storage. Tasks follow the existing repository/service pattern and introduce a pluggable storage abstraction, image processing with Pillow, and new API endpoints.

## Tasks

- [x] 1. Add configuration settings and database schema
  - [x] 1.1 Add image-related settings to `backend/app/core/config.py`
    - Add `IMAGE_MAX_SIZE_MB`, `IMAGE_MAX_DIMENSION`, `IMAGE_THUMBNAIL_DIMENSION`, `IMAGE_QUALITY`, `S3_IMAGES_BUCKET`, `CLOUDFRONT_IMAGES_URL` fields to the Settings class
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_
  - [x] 1.2 Add `profile_image_key` field to Person model
    - Add nullable `profile_image_key: str | None` field to `backend/app/db_models/person/person.py`
    - _Requirements: 4.1_
  - [x] 1.3 Create Alembic migration for `profile_image_key` column
    - Generate and verify migration that adds `profile_image_key` column to `person` table
    - _Requirements: 4.4_
  - [x] 1.4 Update `PersonPublic` schema to include `profile_image_key`
    - Add `profile_image_key` to the person public response schema
    - _Requirements: 4.1_

- [x] 2. Implement storage backend abstraction
  - [x] 2.1 Create `StorageBackend` abstract base class
    - Create `backend/app/services/storage/base.py` with abstract `upload`, `delete`, `get_url` methods
    - _Requirements: 1.1_
  - [x] 2.2 Implement `LocalStorage`
    - Create `backend/app/services/storage/local_storage.py`
    - Save files to `uploads/person-images/` directory, create dir if missing
    - Return URLs in format `/api/v1/uploads/person-images/{filename}`
    - _Requirements: 1.2, 1.4, 1.6_
  - [ ]* 2.3 Write property tests for LocalStorage
    - **Property 1: LocalStorage round-trip**
    - **Property 2: LocalStorage URL format**
    - **Validates: Requirements 1.4, 1.6**
  - [x] 2.4 Implement `S3Storage`
    - Create `backend/app/services/storage/s3_storage.py`
    - Upload to S3 bucket with `person-images/` prefix using boto3
    - Return CloudFront URL if configured, otherwise S3 URL
    - _Requirements: 1.3, 1.5, 1.7_
  - [ ]* 2.5 Write property test for S3Storage URL format
    - **Property 3: S3Storage URL format**
    - **Validates: Requirements 1.7**
  - [x] 2.6 Create storage factory function
    - Create `backend/app/services/storage/__init__.py` with `get_storage_backend()` factory
    - Return LocalStorage for `local` environment, S3Storage otherwise
    - _Requirements: 1.2, 1.3_

- [x] 3. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement image processor
  - [x] 4.1 Create `ImageProcessor` class
    - Create `backend/app/services/image_processor.py`
    - Implement `validate()` method: check file type (JPEG/PNG/WebP) and size
    - Implement `process()` method: resize main (400x400 max) and thumbnail (100x100 max), convert to JPEG, strip EXIF
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_
  - [ ]* 4.2 Write property tests for ImageProcessor
    - **Property 4: Image dimension constraints**
    - **Property 5: EXIF metadata stripping**
    - **Property 6: Invalid file rejection**
    - **Property 7: Image processing produces valid JPEG**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.8**

- [x] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement image upload service and API endpoints
  - [x] 6.1 Create `ImageUploadService`
    - Create `backend/app/services/image_upload_service.py`
    - Implement `upload_profile_image()`: validate, process, generate UUID filename, upload both variants, update person record, clean up old image if exists
    - Implement `delete_profile_image()`: delete files from storage, clear person record
    - Implement `get_image_urls()`: return main and thumbnail URLs
    - _Requirements: 3.1, 3.2, 3.3, 3.6, 3.7_
  - [x] 6.2 Create response schemas
    - Create `PersonImageResponse` and `PersonImageUploadResponse` schemas
    - _Requirements: 3.2_
  - [x] 6.3 Add profile image API endpoints to person routes
    - Add `/me/profile-image` endpoints (POST, GET, DELETE) before `/{person_id}` routes
    - Add `/{person_id}/profile-image` endpoints (POST, GET, DELETE) with access validation
    - Use `UploadFile` for multipart file upload
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  - [ ]* 6.4 Write property tests for image upload service
    - **Property 8: Image replacement cleans up old files**
    - **Property 9: Unique filename generation**
    - **Validates: Requirements 3.6, 3.7**
  - [ ]* 6.5 Write unit tests for API endpoints
    - Test upload, get, delete flows for /me and /{person_id} endpoints
    - Test auth (401) and access control (403) error cases
    - Test file size and format validation error cases
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [x] 7. Configure local development serving and Docker
  - [x] 7.1 Add conditional static file mount in `main.py`
    - Mount `/api/v1/uploads` to serve from `uploads/` directory when `ENVIRONMENT=local`
    - _Requirements: 5.1, 5.2_
  - [x] 7.2 Add uploads volume mount to `docker-compose.override.yml`
    - Mount `./backend/uploads` to `/app/uploads` in the backend container
    - _Requirements: 5.3_
  - [x] 7.3 Add `Pillow` and `boto3` to backend dependencies
    - Update `pyproject.toml` with new dependencies
    - _Requirements: 2.1, 1.5_

- [x] 8. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties using Hypothesis
- Unit tests validate specific examples and edge cases
