import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecsPatterns from 'aws-cdk-lib/aws-ecs-patterns';
import * as ecr_assets from 'aws-cdk-lib/aws-ecr-assets';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as path from 'path';
import { Construct } from 'constructs';

interface AppConfig {
  database: {
    instanceClass: string;
    instanceSize: string;
    allocatedStorage: number;
    maxAllocatedStorage: number;
  };
  backend: {
    cpu: number;
    memory: number;
    desiredCount: number;
    minCapacity: number;
    maxCapacity: number;
    scalingCpuPercent: number;
    scalingMemoryPercent: number;
  };
}

interface FullStackAppProps extends cdk.StackProps {
  config: AppConfig;
}

export class FullStackApp extends cdk.Stack {
  constructor(scope: Construct, id: string, props: FullStackAppProps) {
    super(scope, id, props);

    const { config } = props;

    // === VPC ===
    const vpc = new ec2.Vpc(this, 'Vpc', {
      maxAzs: 2,
      natGateways: 1,
      subnetConfiguration: [
        { name: 'Public', subnetType: ec2.SubnetType.PUBLIC, cidrMask: 24 },
        { name: 'Private', subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS, cidrMask: 24 },
        { name: 'Isolated', subnetType: ec2.SubnetType.PRIVATE_ISOLATED, cidrMask: 24 },
      ],
    });

    // === DATABASE ===
    const dbSecret = new secretsmanager.Secret(this, 'DbSecret', {
      secretName: `${id}-db-credentials`,
      generateSecretString: {
        secretStringTemplate: JSON.stringify({ username: 'postgres' }),
        generateStringKey: 'password',
        excludePunctuation: true,
        passwordLength: 32,
      },
    });

    const instanceClass = ec2.InstanceClass[config.database.instanceClass.toUpperCase() as keyof typeof ec2.InstanceClass];
    const instanceSize = ec2.InstanceSize[config.database.instanceSize.toUpperCase() as keyof typeof ec2.InstanceSize];

    const database = new rds.DatabaseInstance(this, 'Database', {
      engine: rds.DatabaseInstanceEngine.postgres({ version: rds.PostgresEngineVersion.VER_16 }),
      instanceType: ec2.InstanceType.of(instanceClass, instanceSize),
      vpc,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_ISOLATED },
      credentials: rds.Credentials.fromSecret(dbSecret),
      databaseName: 'app',
      allocatedStorage: config.database.allocatedStorage,
      maxAllocatedStorage: config.database.maxAllocatedStorage,
      backupRetention: cdk.Duration.days(7),
      deletionProtection: false,
      removalPolicy: cdk.RemovalPolicy.SNAPSHOT,
    });

    // === BACKEND ===
    const cluster = new ecs.Cluster(this, 'Cluster', { vpc });

    const appSecret = new secretsmanager.Secret(this, 'AppSecret', {
      secretName: `${id}-app-secrets`,
      generateSecretString: {
        secretStringTemplate: JSON.stringify({
          SECRET_KEY: 'change-me-in-console',
          FIRST_SUPERUSER: 'admin@example.com',
          FIRST_SUPERUSER_PASSWORD: 'changethis',
        }),
        generateStringKey: 'dummy',
      },
    });

    const backendImage = new ecr_assets.DockerImageAsset(this, 'BackendImage', {
      directory: path.join(__dirname, '../../backend'),
      platform: ecr_assets.Platform.LINUX_AMD64,
    });

    const backendService = new ecsPatterns.ApplicationLoadBalancedFargateService(this, 'BackendService', {
      cluster,
      cpu: config.backend.cpu,
      memoryLimitMiB: config.backend.memory,
      desiredCount: config.backend.desiredCount,
      enableExecuteCommand: true,
      taskImageOptions: {
        image: ecs.ContainerImage.fromDockerImageAsset(backendImage),
        containerPort: 8000,
        environment: {
          ENVIRONMENT: 'production',
          POSTGRES_SERVER: database.dbInstanceEndpointAddress,
          POSTGRES_PORT: '5432',
          POSTGRES_DB: 'app',
          PROJECT_NAME: 'FullStack App',
          BACKEND_CORS_ORIGINS: '',
        },
        secrets: {
          POSTGRES_USER: ecs.Secret.fromSecretsManager(dbSecret, 'username'),
          POSTGRES_PASSWORD: ecs.Secret.fromSecretsManager(dbSecret, 'password'),
          SECRET_KEY: ecs.Secret.fromSecretsManager(appSecret, 'SECRET_KEY'),
          FIRST_SUPERUSER: ecs.Secret.fromSecretsManager(appSecret, 'FIRST_SUPERUSER'),
          FIRST_SUPERUSER_PASSWORD: ecs.Secret.fromSecretsManager(appSecret, 'FIRST_SUPERUSER_PASSWORD'),
        },
        logDriver: ecs.LogDrivers.awsLogs({
          streamPrefix: 'backend',
          logRetention: logs.RetentionDays.ONE_WEEK,
        }),
      },
      publicLoadBalancer: true,
      assignPublicIp: false,
    });

    backendService.targetGroup.configureHealthCheck({
      path: '/api/v1/utils/health-check/',
      healthyHttpCodes: '200',
    });

    database.connections.allowFrom(backendService.service, ec2.Port.tcp(5432));

    const scaling = backendService.service.autoScaleTaskCount({
      minCapacity: config.backend.minCapacity,
      maxCapacity: config.backend.maxCapacity,
    });
    scaling.scaleOnCpuUtilization('CpuScaling', {
      targetUtilizationPercent: config.backend.scalingCpuPercent,
    });
    scaling.scaleOnMemoryUtilization('MemoryScaling', {
      targetUtilizationPercent: config.backend.scalingMemoryPercent,
    });

    // === IMAGES BUCKET ===
    const imagesBucket = new s3.Bucket(this, 'ImagesBucket', {
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    imagesBucket.grantReadWrite(backendService.taskDefinition.taskRole);

    // === FRONTEND (S3 + CloudFront with API proxy) ===
    const websiteBucket = new s3.Bucket(this, 'WebsiteBucket', {
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });

    const originAccessIdentity = new cloudfront.OriginAccessIdentity(this, 'OAI');
    websiteBucket.grantRead(originAccessIdentity);
    imagesBucket.grantRead(originAccessIdentity);

    // API origin (ALB) - no caching, forward all headers
    const apiOrigin = new origins.HttpOrigin(
      backendService.loadBalancer.loadBalancerDnsName,
      { protocolPolicy: cloudfront.OriginProtocolPolicy.HTTP_ONLY },
    );

    const distribution = new cloudfront.Distribution(this, 'Distribution', {
      defaultBehavior: {
        origin: new origins.S3Origin(websiteBucket, { originAccessIdentity }),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
      },
      additionalBehaviors: {
        '/api/*': {
          origin: apiOrigin,
          viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
          allowedMethods: cloudfront.AllowedMethods.ALLOW_ALL,
          cachePolicy: cloudfront.CachePolicy.CACHING_DISABLED,
          originRequestPolicy: cloudfront.OriginRequestPolicy.ALL_VIEWER,
        },
        '/docs': {
          origin: apiOrigin,
          viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
          allowedMethods: cloudfront.AllowedMethods.ALLOW_ALL,
          cachePolicy: cloudfront.CachePolicy.CACHING_DISABLED,
          originRequestPolicy: cloudfront.OriginRequestPolicy.ALL_VIEWER,
        },
        '/openapi.json': {
          origin: apiOrigin,
          viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
          cachePolicy: cloudfront.CachePolicy.CACHING_DISABLED,
          originRequestPolicy: cloudfront.OriginRequestPolicy.ALL_VIEWER,
        },
        '/images/*': {
          origin: new origins.S3Origin(imagesBucket, { originAccessIdentity }),
          viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
          cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
        },
      },
      defaultRootObject: 'index.html',
      errorResponses: [
        { httpStatus: 404, responseHttpStatus: 200, responsePagePath: '/index.html' },
        { httpStatus: 403, responseHttpStatus: 200, responsePagePath: '/index.html' },
      ],
    });

    // Add FRONTEND_HOST to the task definition
    backendService.taskDefinition.defaultContainer!.addEnvironment(
      'FRONTEND_HOST', `https://${distribution.distributionDomainName}`
    );

    // Add image infrastructure env vars (after distribution to avoid circular deps)
    backendService.taskDefinition.defaultContainer!.addEnvironment(
      'S3_IMAGES_BUCKET', imagesBucket.bucketName
    );
    backendService.taskDefinition.defaultContainer!.addEnvironment(
      'CLOUDFRONT_IMAGES_URL', `https://${distribution.distributionDomainName}/images`
    );

    // === OUTPUTS ===
    new cdk.CfnOutput(this, 'AppUrl', { value: `https://${distribution.distributionDomainName}` });
    new cdk.CfnOutput(this, 'ApiUrl', { value: `https://${distribution.distributionDomainName}/api/v1` });
    new cdk.CfnOutput(this, 'BucketName', { value: websiteBucket.bucketName });
    new cdk.CfnOutput(this, 'DistributionId', { value: distribution.distributionId });
    new cdk.CfnOutput(this, 'DbEndpoint', { value: database.dbInstanceEndpointAddress });
    new cdk.CfnOutput(this, 'AppSecretArn', { value: appSecret.secretArn });
    new cdk.CfnOutput(this, 'ImagesBucketName', { value: imagesBucket.bucketName });
    new cdk.CfnOutput(this, 'ImagesUrl', { value: `https://${distribution.distributionDomainName}/images` });
  }
}
