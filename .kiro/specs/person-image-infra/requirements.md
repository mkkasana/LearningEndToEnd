# Requirements Document

## Introduction

This feature adds the AWS infrastructure needed to support person profile image storage and serving in staging and production environments. It creates a dedicated S3 bucket for images, grants the ECS backend task appropriate permissions, adds a CloudFront behavior for CDN-cached image delivery, passes the required environment variables to the backend container, and updates the deployment runbook.

## Glossary

- **Images_Bucket**: A dedicated S3 bucket for storing person profile images (main and thumbnail variants).
- **CDK_Stack**: The existing single-stack CDK infrastructure definition in `infra/lib/fullstack-app.ts`.
- **CloudFront_Distribution**: The existing CloudFront distribution that serves the frontend SPA and proxies API requests.
- **ECS_Task_Role**: The IAM role assumed by the Fargate backend task, which needs S3 read/write permissions for the images bucket.
- **OAI**: Origin Access Identity used by CloudFront to read from S3 buckets without making them public.

## Requirements

### Requirement 1: S3 Images Bucket

**User Story:** As a system operator, I want a dedicated S3 bucket for person images, so that images are stored securely and separately from the frontend static files.

#### Acceptance Criteria

1. THE CDK_Stack SHALL create a new S3 bucket with all public access blocked
2. THE Images_Bucket SHALL have a removal policy of RETAIN to prevent accidental data loss on stack teardown
3. THE Images_Bucket SHALL be named with the stack prefix pattern (e.g., `fullstack-app-imagesbucket-{hash}`)
4. THE CDK_Stack SHALL grant the OAI read access to the Images_Bucket so CloudFront can serve images

### Requirement 2: ECS Task Permissions

**User Story:** As a backend service, I need read/write access to the images S3 bucket, so that I can upload and delete person profile images.

#### Acceptance Criteria

1. THE CDK_Stack SHALL grant the ECS_Task_Role `s3:PutObject`, `s3:GetObject`, and `s3:DeleteObject` permissions on the Images_Bucket
2. THE CDK_Stack SHALL use the CDK `grantReadWrite` method to apply least-privilege permissions

### Requirement 3: CloudFront Image Serving

**User Story:** As a user, I want profile images to be served through CloudFront with caching, so that images load quickly from edge locations worldwide.

#### Acceptance Criteria

1. THE CDK_Stack SHALL add a CloudFront behavior for the path pattern `/images/*` pointing to the Images_Bucket as origin
2. THE CloudFront behavior for `/images/*` SHALL use the `CACHING_OPTIMIZED` cache policy to cache images at edge locations
3. THE CloudFront behavior for `/images/*` SHALL enforce HTTPS via `REDIRECT_TO_HTTPS` viewer protocol policy
4. THE S3_Storage backend implementation SHALL upload images with the `person-images/` prefix so they are accessible at `/images/person-images/{filename}` via CloudFront

### Requirement 4: Backend Environment Variables

**User Story:** As a developer, I want the S3 bucket name and CloudFront URL passed to the backend container automatically, so that the S3Storage backend can be configured without manual intervention.

#### Acceptance Criteria

1. THE CDK_Stack SHALL pass `S3_IMAGES_BUCKET` environment variable to the ECS task with the Images_Bucket name
2. THE CDK_Stack SHALL pass `CLOUDFRONT_IMAGES_URL` environment variable to the ECS task with the CloudFront distribution URL plus the `/images` path prefix
3. THE environment variables SHALL be added after the CloudFront distribution is created to avoid circular dependencies

### Requirement 5: Infrastructure Outputs

**User Story:** As a developer, I want the images bucket name and CloudFront images URL in the CDK outputs, so that I can reference them in deployment scripts and documentation.

#### Acceptance Criteria

1. THE CDK_Stack SHALL output the Images_Bucket name as `ImagesBucketName`
2. THE CDK_Stack SHALL output the CloudFront images URL as `ImagesUrl`

### Requirement 6: Frontend Image URL Production Support

**User Story:** As a developer, I want the frontend image URL utility to support CloudFront URLs in production, so that profile images load from the CDN instead of the backend API.

#### Acceptance Criteria

1. THE `getPersonImageUrl` utility SHALL check for a `VITE_IMAGES_URL` environment variable
2. WHEN `VITE_IMAGES_URL` is set, THE utility SHALL return URLs in the format `{VITE_IMAGES_URL}/person-images/{key}`
3. WHEN `VITE_IMAGES_URL` is not set, THE utility SHALL fall back to the existing local pattern `{VITE_API_URL}/api/v1/uploads/person-images/{key}`
4. THE thumbnail key derivation logic SHALL remain unchanged regardless of the URL base

### Requirement 7: Deployment Runbook Update

**User Story:** As a developer, I want the AWS deployment documentation updated, so that the image infrastructure is documented for future reference.

#### Acceptance Criteria

1. THE AWS_DEPLOYMENT.md SHALL be updated to include the Images_Bucket in the Architecture Overview diagram
2. THE AWS_DEPLOYMENT.md SHALL document the new CloudFront `/images/*` behavior
3. THE AWS_DEPLOYMENT.md SHALL include the new CDK outputs in the deployment outputs section
4. THE AWS_DEPLOYMENT.md SHALL document how to verify image serving is working after deployment
5. THE AWS_DEPLOYMENT.md SHALL document the `VITE_IMAGES_URL` frontend environment variable and how to set it for production builds
