# Implementation Plan: Person Image Infrastructure (CDK)

## Overview

CDK infrastructure changes to support person profile image storage and CDN delivery in production. All changes are in the existing single CDK stack.

## Tasks

- [ ] 1. Add S3 images bucket and permissions to CDK stack
  - [ ] 1.1 Create S3 images bucket in `infra/lib/fullstack-app.ts`
    - Add `ImagesBucket` with `BLOCK_ALL` public access and `RETAIN` removal policy
    - Grant OAI read access to the bucket
    - _Requirements: 1.1, 1.2, 1.4_
  - [ ] 1.2 Grant ECS task role read/write access to images bucket
    - Use `imagesBucket.grantReadWrite(backendService.taskDefinition.taskRole)`
    - _Requirements: 2.1, 2.2_

- [ ] 2. Add CloudFront behavior for image serving
  - [ ] 2.1 Add `/images/*` behavior to CloudFront distribution
    - Add to `additionalBehaviors` with S3Origin pointing to images bucket
    - Use `CACHING_OPTIMIZED` cache policy and `REDIRECT_TO_HTTPS` viewer protocol
    - _Requirements: 3.1, 3.2, 3.3_

- [ ] 3. Pass environment variables to backend container
  - [ ] 3.1 Add `S3_IMAGES_BUCKET` and `CLOUDFRONT_IMAGES_URL` env vars
    - Add after distribution creation to avoid circular dependencies
    - `S3_IMAGES_BUCKET` = `imagesBucket.bucketName`
    - `CLOUDFRONT_IMAGES_URL` = `https://${distribution.distributionDomainName}/images`
    - _Requirements: 4.1, 4.2, 4.3_

- [ ] 4. Add CDK outputs
  - [ ] 4.1 Add `ImagesBucketName` and `ImagesUrl` outputs
    - _Requirements: 5.1, 5.2_

- [ ] 5. Verify CDK synthesis
  - [ ] 5.1 Run `npx cdk synth` and verify no errors
    - Ensure the stack synthesizes without circular dependency errors
    - Review the generated CloudFormation template for correctness
  - [ ] 5.2 Run `npx cdk diff` to preview changes
    - Verify only additive changes (new bucket, new behavior, new env vars, new outputs)
    - No existing resources should be modified or replaced

- [ ] 6. Update deployment documentation
  - [ ] 6.1 Update `AWS_DEPLOYMENT.md` with image infrastructure details
    - Add Images_Bucket to the architecture diagram
    - Document the `/images/*` CloudFront behavior
    - Add new CDK outputs to the deployment outputs section
    - Add verification steps for image serving
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

## Notes

- This spec should be executed after the backend spec (`person-profile-image-backend`) is complete
- No optional tasks — all infrastructure changes are required for production deployment
- Run `npx cdk diff` before deploying to verify changes are safe
- The CDK changes are additive — no existing resources are modified
