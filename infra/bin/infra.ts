#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { FullStackApp } from '../lib/fullstack-app';
import * as config from '../config.json';

const app = new cdk.App();

new FullStackApp(app, config.appName, {
  env: {
    account: config.aws.account,
    region: config.aws.region,
  },
  config: {
    database: config.database,
    backend: config.backend,
  },
});

app.synth();
