# Question Generation Service

Modular FastAPI service for generating educational questions using OpenSearch and LLMs.

## Features

- Generate multiple choice questions (MCQ)
- Generate fill-in-the-blank questions (FIB)
- Generate true/false questions (TF)
- Configurable difficulty levels and Bloom's taxonomy levels
- Integration with AWS OpenSearch for content retrieval
- Uses AWS Bedrock for LLM-based question generation
- Modular architecture with dependency injection
- Async processing support

## Project Structure

```
question-generation-service/
├── app.py                  # Main FastAPI application
├── src/
│   ├── api/               # API routes and dependencies
│   ├── core/              # Core configuration and utilities
│   ├── db/                # Database connections
│   ├── models/            # Pydantic models
│   ├── services/          # Business logic services
│   └── utils/             # Helper utilities
├── requirements.txt
└── Dockerfile
```

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env` file
4. Run the application: `python app.py`

## Environment Variables

- `AWS_REGION`: AWS region for services
- `AWS_PROFILE_NAME`: AWS profile name
- `OPENSEARCH_HOST`: OpenSearch endpoint
- `LLM_MODEL`: Bedrock model ARN
- `DYNAMODB_REGION`: DynamoDB region
- `QUESTION_HISTORY_TABLE`: DynamoDB table for question history

## API Endpoints

- `GET /health`: Health check endpoint
- `POST /questionBankService/generate`: Generate questions
- `GET /questionBankService/status/{session_id}`: Check generation status
