# AWS Infrastructure & Deployment Runbook

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Infrastructure Components](#infrastructure-components)
3. [Configuration](#configuration)
4. [Prerequisites](#prerequisites)
5. [First-Time Deployment](#first-time-deployment)
6. [Accessing the Application](#accessing-the-application)
7. [Deployment Runbooks](#deployment-runbooks)
8. [Database Operations](#database-operations)
9. [Secrets Management](#secrets-management)
10. [Monitoring & Debugging](#monitoring--debugging)
11. [Scaling](#scaling)
12. [Cost Estimates](#cost-estimates)
13. [Teardown](#teardown)
14. [Troubleshooting](#troubleshooting)
15. [Lessons Learned](#lessons-learned)

---

## Architecture Overview

```
                         ┌─────────────────────────────────────┐
                         │           CloudFront (CDN)          │
                         │         HTTPS + Global Edge         │
                         │                                     │
                         │  /* ──────► S3 (Frontend SPA)       │
                         │  /api/* ──► ALB (Backend API)       │
                         │  /docs ───► ALB (Swagger UI)        │
                         │  /openapi.json ► ALB                │
                         └──────────┬──────────┬───────────────┘
                                    │          │
                    ┌───────────────┘          └───────────────┐
                    ▼                                          ▼
          ┌─────────────────┐                    ┌─────────────────────┐
          │   S3 Bucket     │                    │  Application Load   │
          │  Static Files   │                    │     Balancer        │
          │  (React SPA)    │                    │   (Public Subnet)   │
          └─────────────────┘                    └──────────┬──────────┘
                                                            │
                                                            ▼
                                                 ┌─────────────────────┐
                                                 │   ECS Fargate       │
                                                 │   (Private Subnet)  │
                                                 │                     │
                                                 │  FastAPI Backend    │
                                                 │  2 vCPU / 5GB RAM  │
                                                 │  Auto-scaling 1-10  │
                                                 └──────────┬──────────┘
                                                            │
                                                            ▼
                                                 ┌─────────────────────┐
                                                 │   RDS PostgreSQL    │
                                                 │  (Isolated Subnet)  │
                                                 │                     │
                                                 │  db.t3.micro        │
                                                 │  20-100 GB storage  │
                                                 │  7-day backups      │
                                                 └─────────────────────┘
```

All traffic enters through a single CloudFront URL over HTTPS. CloudFront routes:
- Static frontend files from S3 (cached at edge)
- API requests to the ALB → ECS Fargate (no caching, all headers forwarded)
- Profile images from the Images S3 bucket (cached at edge with `CACHING_OPTIMIZED`)

This eliminates mixed-content (HTTP/HTTPS) issues since everything is served over HTTPS.

---

## Infrastructure Components

### VPC (Virtual Private Cloud)
- 2 Availability Zones for high availability
- 1 NAT Gateway (for outbound internet from private subnets)
- **Public Subnets** — ALB lives here
- **Private Subnets** — ECS Fargate tasks run here (outbound internet via NAT)
- **Isolated Subnets** — RDS database (no internet access)

### CloudFront Distribution
- Global CDN with automatic HTTPS
- Routes `/*` to S3 (frontend) with optimized caching
- Routes `/api/*`, `/docs`, `/openapi.json` to ALB with caching disabled
- Routes `/images/*` to S3 Images Bucket with optimized caching (profile images served via CDN)
- SPA error handling: 404/403 → `/index.html` (for client-side routing)

### S3 Bucket (Frontend)
- Stores built React frontend static files
- Block all public access (only accessible via CloudFront OAI)
- Auto-delete on stack teardown

### S3 Bucket (Images)
- Stores person profile images (main 400x400 and thumbnail 100x100 variants)
- Block all public access (only accessible via CloudFront OAI)
- Removal policy: RETAIN (images persist even if stack is torn down)
- Key pattern: `person-images/{uuid}.jpg` and `person-images/{uuid}_thumb.jpg`
- Backend uploads via boto3 using ECS task role (grantReadWrite)

### ECS Fargate (Backend)
- Serverless containers — no EC2 instances to manage
- 2 vCPU / 5 GB memory per task
- Auto-scaling: 1–10 tasks based on CPU/memory (70% threshold)
- ECS Exec enabled for remote shell access
- Health check: `GET /api/v1/utils/health-check/`
- Docker image built from `backend/Dockerfile`, cross-compiled for linux/amd64

### Application Load Balancer
- Public-facing, routes traffic to ECS tasks
- Health checks ensure only healthy tasks receive traffic

### RDS PostgreSQL 16
- Instance: db.t3.micro (scalable)
- Storage: 20 GB, auto-scales to 100 GB
- 7-day automated backups
- Isolated subnet (no public access)
- Credentials stored in Secrets Manager

### Secrets Manager
- `fullstack-app-db-credentials` — PostgreSQL username/password (auto-generated)
- `fullstack-app-app-secrets` — SECRET_KEY, FIRST_SUPERUSER, FIRST_SUPERUSER_PASSWORD

### ECR (Elastic Container Registry)
- Stores backend Docker images pushed by CDK during deployment

---

## Configuration

All infrastructure settings are in `infra/config.json`:

```json
{
  "appName": "fullstack-app",
  "aws": {
    "account": "309841440455",
    "region": "us-east-1"
  },
  "database": {
    "instanceClass": "t3",
    "instanceSize": "micro",
    "allocatedStorage": 20,
    "maxAllocatedStorage": 100
  },
  "backend": {
    "cpu": 2048,
    "memory": 5120,
    "desiredCount": 1,
    "minCapacity": 1,
    "maxCapacity": 10,
    "scalingCpuPercent": 70,
    "scalingMemoryPercent": 70
  }
}
```

| Setting | Description | Valid Values |
|---------|-------------|--------------|
| `aws.account` | Target AWS account ID | AWS account number |
| `aws.region` | Deployment region | Any AWS region |
| `database.instanceClass` | RDS instance family | t3, t4g, m5, r5, etc. |
| `database.instanceSize` | RDS instance size | micro, small, medium, large, xlarge |
| `backend.cpu` | Fargate CPU units | 256, 512, 1024, 2048, 4096 |
| `backend.memory` | Fargate memory (MB) | Must be compatible with CPU (see [Fargate docs](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-cpu-memory-error.html)) |
| `backend.desiredCount` | Initial task count | 1+ |
| `backend.minCapacity` | Min auto-scale tasks | 1+ |
| `backend.maxCapacity` | Max auto-scale tasks | minCapacity+ |

---

## Prerequisites

1. **AWS CLI** configured with credentials for account `309841440455`
   ```bash
   aws configure
   aws sts get-caller-identity  # Verify
   ```

2. **Node.js** 18+ installed

3. **Docker runtime** — Colima (recommended for Mac) or Docker Desktop
   ```bash
   # Install Colima
   brew install colima docker
   colima start

   # Set Docker host for current session
   export DOCKER_HOST=unix://$HOME/.colima/docker.sock
   ```

4. **CDK dependencies** installed
   ```bash
   cd infra && npm install
   ```

---

## First-Time Deployment

### Step 1: Bootstrap CDK (one-time)
```bash
cd infra
npx cdk bootstrap aws://309841440455/us-east-1
```

### Step 2: Deploy Infrastructure
```bash
DOCKER_HOST=unix://$HOME/.colima/docker.sock npx cdk deploy --require-approval never
```
This takes ~15-25 minutes and creates all AWS resources.

Save the outputs:
```
fullstack-app.AppUrl = https://d3low8lxbb1cbt.cloudfront.net
fullstack-app.ApiUrl = https://d3low8lxbb1cbt.cloudfront.net/api/v1
fullstack-app.BucketName = fullstack-app-websitebucket75c24d94-vtbs4uyw6n2h
fullstack-app.DistributionId = EMD9I3USQMOI9
fullstack-app.ImagesBucketName = fullstack-app-imagesbucket-xxxxxxxxx
fullstack-app.ImagesUrl = https://d3low8lxbb1cbt.cloudfront.net/images
```

### Step 3: Update Application Secrets
1. Go to AWS Console → Secrets Manager → `fullstack-app-app-secrets`
2. Update:
   - `SECRET_KEY`: Generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`
   - `FIRST_SUPERUSER`: Your admin email
   - `FIRST_SUPERUSER_PASSWORD`: Strong password
3. Force ECS to pick up new secrets:
   ```bash
   aws ecs update-service \
     --cluster <ClusterName> \
     --service <ServiceName> \
     --force-new-deployment
   ```

### Step 4: Run Database Migrations
Via ECS Console:
1. Go to ECS → Cluster → Tasks → Click running task
2. Click "Execute command"
3. Run: `cd /app && alembic upgrade head`

### Step 5: Seed Database (Optional)
In the same ECS exec session:
```bash
cd /app && python init_seed/seed_database.py
```

### Step 6: Build & Deploy Frontend
```bash
cd frontend
VITE_API_URL=https://d3low8lxbb1cbt.cloudfront.net \
VITE_IMAGES_URL=https://d3low8lxbb1cbt.cloudfront.net/images \
npm run build
aws s3 sync dist/ s3://fullstack-app-websitebucket75c24d94-vtbs4uyw6n2h --delete
aws cloudfront create-invalidation --distribution-id EMD9I3USQMOI9 --paths "/*"
```

> `VITE_IMAGES_URL` tells the frontend to load profile images from CloudFront instead of the backend API. Set it to the `ImagesUrl` CDK output value.

---

## Accessing the Application

| What | URL |
|------|-----|
| Frontend (App) | https://d3low8lxbb1cbt.cloudfront.net |
| API Documentation (Swagger) | https://d3low8lxbb1cbt.cloudfront.net/docs |
| OpenAPI Spec | https://d3low8lxbb1cbt.cloudfront.net/openapi.json |
| API Base URL | https://d3low8lxbb1cbt.cloudfront.net/api/v1 |

### Test Credentials (after seeding)
- Email: `testfamily@example.com`
- Password: `TestFamily123!`

---

## Deployment Runbooks

### Frontend Changes Only (React/TypeScript)

When you modify files in `frontend/src/`:

```bash
# 1. Build
cd frontend
VITE_API_URL=https://d3low8lxbb1cbt.cloudfront.net \
VITE_IMAGES_URL=https://d3low8lxbb1cbt.cloudfront.net/images \
npm run build

# 2. Upload to S3
aws s3 sync dist/ s3://fullstack-app-websitebucket75c24d94-vtbs4uyw6n2h --delete

# 3. Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id EMD9I3USQMOI9 --paths "/*"
```

Time: ~2-3 minutes. No downtime.

### Backend Changes Only (Python/FastAPI)

When you modify files in `backend/app/`:

```bash
# 1. Deploy via CDK (rebuilds Docker image, pushes to ECR, updates ECS)
cd infra
DOCKER_HOST=unix://$HOME/.colima/docker.sock npx cdk deploy --require-approval never
```

Time: ~5-10 minutes. Rolling deployment (no downtime).

If CDK says "no changes" (image hash unchanged), force a rebuild:
```bash
# Touch a file to change the hash
echo "# $(date)" >> ../backend/pyproject.toml

# Then deploy
DOCKER_HOST=unix://$HOME/.colima/docker.sock npx cdk deploy --require-approval never
```

### Backend API Changes (New/Modified Endpoints)

When you add or modify API endpoints:

```bash
# 1. Deploy backend (same as above)
cd infra
DOCKER_HOST=unix://$HOME/.colima/docker.sock npx cdk deploy --require-approval never

# 2. Regenerate frontend API client
cd ../frontend
npm run generate-client

# 3. Update frontend code to use new types/methods

# 4. Build and deploy frontend
VITE_API_URL=https://d3low8lxbb1cbt.cloudfront.net \
VITE_IMAGES_URL=https://d3low8lxbb1cbt.cloudfront.net/images \
npm run build
aws s3 sync dist/ s3://fullstack-app-websitebucket75c24d94-vtbs4uyw6n2h --delete
aws cloudfront create-invalidation --distribution-id EMD9I3USQMOI9 --paths "/*"
```

### Infrastructure Changes (Config/CDK)

When you modify `infra/config.json` or `infra/lib/fullstack-app.ts`:

```bash
cd infra
DOCKER_HOST=unix://$HOME/.colima/docker.sock npx cdk deploy --require-approval never
```

Preview changes first:
```bash
npx cdk diff
```

### Full Stack Deployment (Everything)

```bash
# 1. Infrastructure + Backend
cd infra
DOCKER_HOST=unix://$HOME/.colima/docker.sock npx cdk deploy --require-approval never

# 2. Frontend
cd ../frontend
VITE_API_URL=https://d3low8lxbb1cbt.cloudfront.net \
VITE_IMAGES_URL=https://d3low8lxbb1cbt.cloudfront.net/images \
npm run build
aws s3 sync dist/ s3://fullstack-app-websitebucket75c24d94-vtbs4uyw6n2h --delete
aws cloudfront create-invalidation --distribution-id EMD9I3USQMOI9 --paths "/*"
```

---

## Database Operations

### Running Migrations

When you create new Alembic migrations (schema changes):

1. **Create migration locally:**
   ```bash
   cd backend
   alembic revision --autogenerate -m "description of change"
   ```

2. **Deploy backend** (includes new migration file in Docker image):
   ```bash
   cd infra
   DOCKER_HOST=unix://$HOME/.colima/docker.sock npx cdk deploy --require-approval never
   ```

3. **Apply migration** via ECS Exec:
   - ECS Console → Cluster → Tasks → Running task → Execute command
   - Run: `cd /app && alembic upgrade head`

4. **Verify:**
   ```bash
   cd /app && alembic current
   ```

### Rolling Back Migrations

Via ECS Exec:
```bash
cd /app && alembic downgrade -1    # Go back one revision
cd /app && alembic downgrade <rev>  # Go to specific revision
```

### Seeding Data

Via ECS Exec:
```bash
cd /app && python init_seed/seed_database.py
```

### Direct Database Access

The RDS instance is in an isolated subnet (no public access). To connect:

1. Use ECS Exec to get a shell in the container
2. Run:
   ```bash
   python -c "
   from app.core.db import engine
   from sqlmodel import text
   with engine.connect() as conn:
       result = conn.execute(text('SELECT version()'))
       print(result.fetchone())
   "
   ```

---

## Secrets Management

### Locations

| Secret | AWS Secrets Manager Name | Contains |
|--------|--------------------------|----------|
| Database credentials | `fullstack-app-db-credentials` | `username`, `password` (auto-generated) |
| App secrets | `fullstack-app-app-secrets` | `SECRET_KEY`, `FIRST_SUPERUSER`, `FIRST_SUPERUSER_PASSWORD` |

### Updating Secrets

1. Go to AWS Console → Secrets Manager
2. Select the secret → "Retrieve secret value" → "Edit"
3. Update values → Save
4. **Restart ECS** to pick up changes:
   ```bash
   aws ecs update-service \
     --cluster fullstack-app-ClusterEB0386A7-J0zDWmpcpFxE \
     --service fullstack-app-BackendService2147DAF9-3ZWplmuIIoUP \
     --force-new-deployment
   ```

ECS tasks only read secrets at startup. A forced deployment launches new tasks with updated values.

---

## Monitoring & Debugging

### ECS Logs

View backend logs in CloudWatch:
```bash
aws logs tail /aws/ecs/fullstack-app --follow
```

Or via AWS Console: CloudWatch → Log Groups → search "fullstack-app"

### ECS Exec (Remote Shell)

Access a running container:
1. AWS Console → ECS → Cluster → Tasks → Click task → "Execute command"
2. Command: `/bin/bash` or `sh`
3. Container: `web`

Useful commands inside the container:
```bash
cd /app && alembic current          # Check migration status
cd /app && alembic upgrade head     # Apply migrations
cd /app && python init_seed/seed_database.py  # Seed data
ls -la /app/                        # Verify files
env | grep POSTGRES                 # Check env vars
```

### Health Check

```bash
curl https://d3low8lxbb1cbt.cloudfront.net/api/v1/utils/health-check/
```

### Verify Image Serving

After deployment, verify profile images are served correctly through CloudFront:

```bash
# Check CloudFront returns proper headers for the images path
curl -I https://d3low8lxbb1cbt.cloudfront.net/images/person-images/test.jpg
# Should return CloudFront headers (x-cache, x-amz-cf-pop) even if the file doesn't exist (403/404 is fine)

# Upload a test image via the API, then verify it's accessible via CloudFront
# The backend automatically uploads to S3 with the person-images/ prefix
# CloudFront serves from /images/person-images/{uuid}.jpg
```

### ECS Service Status

```bash
aws ecs describe-services \
  --cluster fullstack-app-ClusterEB0386A7-J0zDWmpcpFxE \
  --services fullstack-app-BackendService2147DAF9-3ZWplmuIIoUP \
  --query 'services[0].{running:runningCount,desired:desiredCount,pending:pendingCount}'
```

---

## Scaling

### Auto-Scaling (Configured)

The backend auto-scales based on:
- CPU utilization > 70% → scale out
- Memory utilization > 70% → scale out
- Range: 1 to 10 tasks

### Manual Scaling

Change `desiredCount` in `infra/config.json` and redeploy, or:
```bash
aws ecs update-service \
  --cluster fullstack-app-ClusterEB0386A7-J0zDWmpcpFxE \
  --service fullstack-app-BackendService2147DAF9-3ZWplmuIIoUP \
  --desired-count 3
```

### Database Scaling

Modify `infra/config.json`:
```json
"database": {
  "instanceClass": "t3",
  "instanceSize": "small"   // was "micro"
}
```
Then redeploy. Note: RDS resize causes a few minutes of downtime.

### Scaling Guide

| Users | Backend Config | Database |
|-------|---------------|----------|
| 10-100 | 1 task, 2 vCPU / 5 GB | db.t3.micro |
| 100-1000 | 2-4 tasks, 2 vCPU / 5 GB | db.t3.small |
| 1000+ | 4-10 tasks, 4 vCPU / 8 GB | db.t3.medium or Aurora |

---

## Cost Estimates

| Component | Monthly Cost (approx) |
|-----------|----------------------|
| ECS Fargate (1 task, 2 vCPU/5GB) | ~$70 |
| RDS db.t3.micro | ~$15 |
| NAT Gateway | ~$32 |
| ALB | ~$16 |
| CloudFront | ~$1-5 (depends on traffic) |
| S3 | < $1 |
| S3 (Images) | < $1 (scales with storage) |
| Secrets Manager | ~$1 |
| **Total** | **~$135-140/month** |

To reduce costs:
- Use `cpu: 512, memory: 1024` if your app fits (saves ~$50/month)
- Consider removing NAT Gateway and using VPC endpoints instead

---

## Teardown

Destroy all AWS resources:
```bash
cd infra
npx cdk destroy
```

Note: RDS creates a final snapshot by default. Delete manually from AWS Console → RDS → Snapshots if not needed.

Note: The Images S3 bucket has a RETAIN removal policy and will NOT be deleted by `cdk destroy`. Delete it manually from AWS Console → S3 if you want to remove all image data.

---

## Troubleshooting

### "exec format error" in ECS
**Cause:** Docker image built for ARM64 (Apple Silicon) but ECS runs AMD64.
**Fix:** Ensure `platform: ecr_assets.Platform.LINUX_AMD64` is set in CDK.

### Mixed Content Blocked
**Cause:** Frontend (HTTPS via CloudFront) calling backend (HTTP via ALB).
**Fix:** Route API through CloudFront using `additionalBehaviors` for `/api/*`.

### ECS Tasks Keep Crashing (OOM)
**Cause:** Insufficient memory for FastAPI workers.
**Fix:** Increase `backend.cpu` and `backend.memory` in `config.json`. Current: 2048/5120.

### "relation does not exist" in Database
**Cause:** Alembic migrations not applied.
**Fix:** ECS Exec → `cd /app && alembic upgrade head`

### "DuplicateColumn" Error During Migration
**Cause:** RDS database persists across stack teardown/recreate. The column already exists from a previous deployment, but Alembic's tracking table (`alembic_version`) was reset.
**Fix:** Stamp the migration to mark it as applied without running it:
```bash
cd /app && alembic stamp <migration_name>
cd /app && alembic upgrade head   # Continue with remaining migrations
```
Example: `alembic stamp 008_profile_image_key`

### SECRET_KEY Validation Error on Startup
**Cause:** Backend rejects `SECRET_KEY=changethis` in production (Pydantic validation).
**Fix:** Update `fullstack-app-app-secrets` in AWS Secrets Manager before the first ECS task starts:
- `SECRET_KEY`: Generate with `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
- `FIRST_SUPERUSER_PASSWORD`: Any non-default value
- Do this **immediately after CDK deploy**, before ECS tasks stabilize

### CDK Says "No Changes" But Code Changed
**Cause:** Docker image hash unchanged.
**Fix:** Touch a file to change the hash:
```bash
echo "# $(date)" >> backend/pyproject.toml
```

### ECS Exec Not Available
**Cause:** `enableExecuteCommand` not set, or task launched before it was enabled.
**Fix:** Ensure CDK has `enableExecuteCommand: true`, then force new deployment:
```bash
aws ecs update-service --cluster <cluster> --service <service> --force-new-deployment --enable-execute-command
```

### ECS Exec "Connect" Opens Wrong Shell
**Cause:** AWS Console may show a terminal icon with "Connect" instead of "Execute command".
**Fix:** Both work. Click "Connect", select the `web` container, and you'll get a shell. Run `cd /app && ls` to verify you're in the right place.

### `/app` Directory Not Found in ECS Container
**Cause:** Docker image wasn't rebuilt after adding new files (CDK cached the old image hash).
**Fix:** Force image rebuild by modifying a tracked file:
```bash
echo "# $(date)" >> backend/pyproject.toml
cd infra && DOCKER_HOST=unix://$HOME/.colima/docker.sock npx cdk deploy --require-approval never
```

### AWS Credentials Expired During Deployment
**Cause:** Temporary credentials (e.g., SSO/assumed role) expired mid-deploy.
**Fix:** Refresh credentials and re-run `npx cdk deploy`. CDK is idempotent — it will pick up where it left off.

### Wrong AWS Account in Credentials
**Cause:** `~/.aws/credentials` `[default]` profile points to a different account than `config.json`.
**Fix:** Verify with `aws sts get-caller-identity`. If wrong account, refresh credentials for `309841440455`:
```bash
ada credentials update --account 309841440455 --role IibsAdminAccess-DO-NOT-DELETE --provider isengard
```
Or use `isengardcli credentials`.

### CloudFormation Stack Stuck in DELETE/CREATE
**Cause:** ECS service can't stabilize (bad image, missing env vars, OOM).
**Fix:** Delete the stack from AWS Console (CloudFormation → Stack → Delete), wait for completion, fix the issue, then redeploy. Check ECS task logs in CloudWatch for the root cause.

### Docker Desktop Sign-In Required
**Cause:** Docker Desktop requires organization sign-in on Mac.
**Fix:** Use Colima instead (free Docker alternative):
```bash
brew install colima docker
colima start
export DOCKER_HOST=unix://$HOME/.colima/docker.sock
```
Always prefix CDK deploy with `DOCKER_HOST=unix://$HOME/.colima/docker.sock`.

---

## Lessons Learned

Issues encountered during initial deployment and their resolutions:

1. **Cross-stack circular dependencies** — Solved by using a single CDK stack instead of separate network/database/backend/frontend stacks.

2. **ARM64 vs AMD64** — Apple Silicon builds ARM images by default. Added `platform: ecr_assets.Platform.LINUX_AMD64` to force x86_64 builds.

3. **Docker Desktop sign-in required** — Switched to Colima (`brew install colima docker && colima start`) as a free alternative.

4. **Missing environment variables** — Backend requires `PROJECT_NAME`, `FRONTEND_HOST`, and valid `BACKEND_CORS_ORIGINS`. Added all to CDK environment config.

5. **OOM kills** — Initial 256 CPU / 512 MB was too small for FastAPI with 4 workers. Increased to 2048 CPU / 5120 MB.

6. **Mixed content blocking** — CloudFront (HTTPS) → ALB (HTTP) caused browser blocks. Solved by routing `/api/*` through CloudFront as an additional behavior.

7. **ECS Exec not working** — Required `enableExecuteCommand: true` in CDK AND a forced new deployment to launch tasks with the feature enabled.

8. **CDK image caching** — CDK hashes the Docker context to detect changes. If only non-tracked files change, touch `pyproject.toml` to force rebuild.

---

## File Structure

```
infra/
├── bin/infra.ts           # CDK app entry point
├── lib/fullstack-app.ts   # All infrastructure in one stack
├── config.json            # Environment & sizing configuration
├── package.json           # CDK dependencies
├── tsconfig.json          # TypeScript config
└── cdk.json               # CDK settings

scripts/
├── deploy-aws.sh          # One-command deployment script

backend/
├── Dockerfile             # Backend container (Python 3.10 + uv)
├── app/                   # FastAPI application
├── init_seed/             # Database seed scripts
└── alembic.ini            # Migration config

frontend/
├── Dockerfile             # Frontend container (Node + Nginx)
├── src/                   # React application
└── dist/                  # Built static files (deployed to S3)
```
