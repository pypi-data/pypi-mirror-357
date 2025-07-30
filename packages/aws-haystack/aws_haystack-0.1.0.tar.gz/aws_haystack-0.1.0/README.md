# Haystack

[![PyPI version](https://badge.fury.io/py/aws-haystack.svg)](https://badge.fury.io/py/aws-haystack)
[![Python versions](https://img.shields.io/pypi/pyversions/aws-haystack.svg)](https://pypi.org/project/aws-haystack/)
[![Downloads](https://pepy.tech/badge/aws-haystack)](https://pepy.tech/project/aws-haystack)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/niklas-palm/haystack/workflows/Test/badge.svg)](https://github.com/niklas-palm/haystack/actions)

Managing a multi-account AWS organization? Haystack searches CloudFormation stacks across all your AWS accounts from the command line.

```bash
pip install aws-haystack
haystack platform-network
```

## Why?

**Before**: ClickOps through AWS console → switch account → switch region → CloudFormation → list stacks → repeat 50 times  
**After**: `haystack platform-network` → see all matches across all accounts

## Usage

```bash
# Find any stack containing "api"
haystack api

# Search specific region only  
haystack database --region us-east-1

# First run: authenticate once via browser, then fast searches for ~8 hours
```

**Search is smart**: case-insensitive, partial matching
- `haystack api` finds "user-api-prod", "api-gateway", "API-Service"
- `haystack prod` finds "api-prod", "production-db", "PROD-Web"

## What You Get

**Clean results**:
```
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Stack Name         ┃ Account ID  ┃ Account Name       ┃ Region    ┃ Status           ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ user-api-prod      │ 123456789   │ Production         │ us-east-1 │ CREATE_COMPLETE  │
│ user-api-staging   │ 987654321   │ Staging            │ us-east-1 │ CREATE_COMPLETE  │
└────────────────────┴─────────────┴────────────────────┴───────────┴──────────────────┘
```

**Fast & secure**:
- Searches all accounts/regions in parallel  
- Uses AWS SSO (no hardcoded credentials)
- Caches authentication for hours
- Smart role selection (admin > power > first available)

## Commands

```bash
haystack <search-term>                     # Search all accounts/regions
haystack <search-term> --region us-east-1 # Search specific region  
haystack --clear                           # Clear cached credentials
haystack --help                            # Show all options
```

## Requirements

- Python 3.8+
- AWS Identity Center (SSO) access  
- Web browser (for one-time auth)

**First run**: Authenticate via browser, then fast searches for ~8 hours.