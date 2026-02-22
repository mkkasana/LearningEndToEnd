#!/bin/bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Full Stack AWS Deployment ===${NC}"

command -v aws >/dev/null 2>&1 || { echo -e "${RED}AWS CLI required. Install: https://aws.amazon.com/cli/${NC}"; exit 1; }
command -v node >/dev/null 2>&1 || { echo -e "${RED}Node.js required.${NC}"; exit 1; }

cd "$(dirname "$0")/../infra"

# Read config
CONFIG_FILE="config.json"
if [ ! -f "$CONFIG_FILE" ]; then
  echo -e "${RED}Config file not found: $CONFIG_FILE${NC}"
  exit 1
fi

APP_NAME=$(node -p "require('./$CONFIG_FILE').appName")
AWS_ACCOUNT=$(node -p "require('./$CONFIG_FILE').aws.account")
AWS_REGION=$(node -p "require('./$CONFIG_FILE').aws.region")

echo -e "${YELLOW}App Name: $APP_NAME${NC}"
echo -e "${YELLOW}AWS Account: $AWS_ACCOUNT${NC}"
echo -e "${YELLOW}AWS Region: $AWS_REGION${NC}"

# Install dependencies
echo -e "${GREEN}Installing CDK dependencies...${NC}"
npm install

# Bootstrap CDK (first time only)
echo -e "${GREEN}Bootstrapping CDK...${NC}"
npx cdk bootstrap aws://$AWS_ACCOUNT/$AWS_REGION

# Deploy all stacks
echo -e "${GREEN}Deploying infrastructure...${NC}"
npx cdk deploy --all --require-approval never

echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Update app secrets in AWS Secrets Manager (see output above)"
echo "2. Build and deploy frontend:"
echo "   cd frontend"
echo "   VITE_API_URL=<ApiUrl from output> npm run build"
echo "   aws s3 sync dist/ s3://<BucketName from output>"
echo "   aws cloudfront create-invalidation --distribution-id <DistributionId> --paths '/*'"
echo ""
echo "3. Access your app at the DistributionUrl output above"
