# Project Infrastructure Analysis

## Project Overview
This is a **Telegram Bot for Cloud Computing COMP7940** course project with two main features:
1. **News Aggregation**: Retrieves local financial news and uses Gemini API for summarization
2. **AI Image Generation**: Generates images using Gemini API with summarization capabilities

## Technology Stack

### Core Technologies
- **Language**: Python 3.12
- **Main Framework**: python-telegram-bot (v13.7)
- **AI/ML**: Google Gemini API (gemini-2.0-flash model)
- **Database**: MySQL (AWS RDS)
- **Caching**: Redis (v5.2.1)
- **Web Framework**: Flask
- **Image Storage**: AWS S3
- **Container**: Docker

### Key Dependencies
```
python-telegram-bot==13.7
redis==5.2.1
requests==2.32.3
flask
google-genai
python-dotenv
s3fs
pymysql
```

## Infrastructure Architecture

### Cloud Provider: AWS
The project uses a comprehensive AWS infrastructure setup:

#### Core Services
1. **AWS App Runner**: Container-as-a-Service (CaaS) for hosting the application
2. **AWS ECR**: Elastic Container Registry for Docker images
3. **AWS RDS MySQL**: Database service (port 10086)
4. **AWS S3**: Object storage for generated images
5. **AWS Secrets Manager**: Secure storage for environment variables
6. **AWS IAM**: Identity and Access Management

#### Infrastructure as Code (Terraform)
- **Terraform Cloud**: Uses "my_chen" organization with "chatbot" workspace
- **Modular Architecture**: Separate modules for different components
  - `modules/db/`: Database infrastructure
  - `modules/hcp/`: HashiCorp Cloud Platform integration
- **Region**: ap-southeast-1 (Singapore)

### Application Configuration
#### App Runner Service
- **CPU**: 0.25 vCPU
- **Memory**: 0.5 GB
- **Auto Scaling**: Min 3, Max 1 instance (unusual configuration)
- **Max Concurrency**: 100
- **Health Check**: HTTP endpoint `/health_cmy`

#### Database Configuration
- **Engine**: MySQL 8.0
- **Instance**: db.t3.micro
- **Storage**: 20 GB
- **Public Access**: Enabled
- **Custom Port**: 10086
- **Database Name**: chatbot_db
- **Username**: chatbot_user

## CI/CD Pipeline

### GitHub Actions Workflow
**File**: `.github/workflows/ecr.yml`

#### Pipeline Stages
1. **Release Notes Generation**
   - Uses pydoc-markdown for documentation
   - Automatically updates project wiki
   - Triggered on pushes to main branch

2. **Container Deployment**
   - Builds Docker image
   - Pushes to AWS ECR with two tags:
     - Git SHA tag
     - Latest tag
   - Uses GitHub secrets for AWS credentials

#### Required Secrets
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY` 
- `GIT_TOKEN`

#### Environment Variables
- `AWS_REGION`
- `ECR_REPOSITORY`

## Security & Configuration

### Secret Management
- **AWS Secrets Manager**: Centralized secret storage
- **HCP Vault**: HashiCorp Cloud Platform for additional secrets
- **Environment Variables**: Extensive configuration through env vars

### Key Configuration Areas
```bash
# Telegram Bot
ACCESS_TOKEN_TG

# Database
HOST, PASSWORD, DB_NAME, USER_NAME

# Redis
REDISPORT

# AI/ML APIs
GEMINI_API_KEY, ACCESS_TOKEN_LLM
KEY_NEWS (Google News API)

# AWS Services
BASICURL, MODELNAME, APIVERSION
```

## Deployment Strategy

### Local Development
```bash
pip install -r requirements.txt
python3 chatbot.py
```

### Cloud Deployment Options
1. **Automated**: GitHub Actions → ECR → App Runner
2. **Manual**: Terraform provisioning
3. **Containerized**: Docker deployment

## Key Files Structure
```
├── .github/workflows/ecr.yml    # CI/CD pipeline
├── .terraform/                  # Infrastructure as Code
│   ├── main.tf                 # Main Terraform config
│   ├── variables.tf            # Configuration variables
│   └── modules/                # Modular components
│       ├── db/                 # Database module
│       └── hcp/                # HCP integration
├── Dockerfile                   # Container configuration
├── requirements.txt             # Python dependencies
├── chatbot.py                  # Main application
└── README.md                   # Documentation
```

## Architecture Patterns

### Microservices Approach
- Modular Python files for different features
- `chatbot.py`: Main bot logic
- `news.py`: News aggregation
- `ai_image.py`: AI image generation
- `mysql_db.py`: Database operations

### Cloud-Native Design
- Containerized application
- Auto-scaling capabilities
- Managed database service
- Object storage for media files
- Secrets management integration

## Monitoring & Health Checks
- **Health Endpoint**: `/health_cmy`
- **Check Interval**: 20 seconds
- **Protocol**: HTTP

## Notable Infrastructure Decisions
1. **Custom Database Port**: Uses port 10086 instead of standard 3306
2. **Public Database**: RDS instance is publicly accessible
3. **Unusual Auto-scaling**: Min instances (3) > Max instances (1)
4. **Multi-cloud Secrets**: Uses both AWS Secrets Manager and HCP Vault
5. **Container Registry**: Uses AWS ECR with dual tagging strategy

This infrastructure demonstrates a comprehensive cloud-native approach with proper CI/CD, Infrastructure as Code, and security best practices.