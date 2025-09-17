# LangSmith Integration Setup Guide

## Overview
This guide explains how to set up LangSmith for comprehensive evaluation and monitoring of the AI Recruitment System.

## Prerequisites
- Python 3.11+
- OpenAI API Key (for LLM email generation)
- LangChain API Key (for LangSmith)

## Installation Steps

### 1. Install LangSmith Dependencies
```bash
pip install langsmith langchain-openai
```

### 2. Environment Configuration
Add these variables to your `.env` file:

```env
# LangSmith Configuration
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_PROJECT=ai-recruitment-system
LANGCHAIN_TRACING_V2=true

# OpenAI Configuration (for LLM email generation)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini  # Cost-effective model

# Email Configuration (optional - for actual SMTP)
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### 3. LangSmith Account Setup
1. Go to [LangSmith](https://smith.langchain.com/)
2. Create an account or sign in
3. Create a new project: "ai-recruitment-system"
4. Get your API key from Settings > API Keys
5. Add the API key to your `.env` file

## Features Implemented

### 1. Workflow Step Tracing
- **LinkedIn Scraper**: Traces job scraping performance and results
- **Indeed Scraper**: Monitors API calls and data quality
- **Google Scraper**: Tracks multi-source aggregation
- **LLM Email Outreach**: Traces email generation and sending

### 2. Email Generation Evaluation
- **Personalization Score**: How well emails are customized
- **Professionalism Score**: Grammar, tone, business appropriateness
- **Relevance Score**: Content relevance to recruitment context
- **Clarity Score**: Message structure and call-to-action effectiveness

### 3. Job Matching Quality Assessment
- **Match Accuracy**: Quality of candidate-job matching
- **Skill Alignment**: Technical skill overlap analysis
- **Experience Matching**: Seniority and experience alignment
- **Overall Quality Score**: Comprehensive matching evaluation

### 4. Performance Monitoring
- **Execution Time Tracking**: Monitor workflow performance
- **Error Rate Analysis**: Track and analyze failure patterns
- **Resource Usage**: Monitor API calls and token consumption
- **Success Rate Metrics**: Track overall workflow success

## Usage Examples

### 1. Running Workflow with Tracing
```python
# Workflow automatically traces all steps
result = await orchestrator.run_workflow(keywords="Python Developer")

# Check LangSmith dashboard for detailed traces
```

### 2. Email Generation Evaluation
```python
from services.app.services.langsmith_integration import langsmith_service

# Evaluate generated email
evaluation = await langsmith_service.evaluate_email_generation(
    email_data=generated_email,
    job_details=job_info,
    company_info=company_data
)

print(f"Overall Score: {evaluation['overall_score']}")
print(f"Detailed Scores: {evaluation['detailed_scores']}")
```

### 3. Creating Evaluation Datasets
```python
# Create dataset for A/B testing
examples = [
    {
        "inputs": {"job_title": "Senior Python Developer", "company": "TechCorp"},
        "outputs": {"email_subject": "...", "email_body": "..."},
        "metadata": {"email_type": "cold_outreach", "tone": "professional"}
    }
]

dataset_id = await langsmith_service.create_evaluation_dataset(
    dataset_name="email_generation_test",
    examples=examples
)
```

## Monitoring Dashboard

### Key Metrics to Track
1. **Workflow Success Rate**: % of workflows completing successfully
2. **Email Generation Quality**: Average quality scores over time
3. **API Performance**: Response times and error rates
4. **Token Usage**: OpenAI API cost tracking
5. **Job Matching Accuracy**: Quality of candidate matches

### Setting Up Alerts
1. Go to your LangSmith project dashboard
2. Navigate to "Monitoring" section
3. Set up alerts for:
   - Workflow failure rate > 5%
   - Email quality score < 0.7
   - API response time > 10 seconds
   - Daily token usage > threshold

## A/B Testing Framework

### Email Variant Testing
```python
# Generate multiple email variants
variants = await llm_email_service.generate_multiple_variants(
    job_details=job_info,
    company_info=company_data,
    variant_count=3
)

# Each variant automatically logged to LangSmith
# Compare performance in dashboard
```

### Evaluation Criteria
- **Open Rates** (simulated in demo)
- **Response Rates** (simulated in demo)
- **Quality Scores** (LLM-evaluated)
- **Personalization Effectiveness**

## Cost Management

### OpenAI Token Usage
- **gpt-4o-mini**: ~$0.15 per 1M input tokens
- **Average email**: ~200-400 tokens
- **Daily estimate**: $0.50-2.00 for 100 emails

### LangSmith Pricing
- **Free Tier**: 5,000 traces/month
- **Pro Tier**: $39/month for 100K traces
- **Enterprise**: Custom pricing

## Troubleshooting

### Common Issues

#### 1. LangSmith Not Tracing
```bash
# Check environment variables
echo $LANGCHAIN_API_KEY
echo $LANGCHAIN_TRACING_V2

# Verify project name matches
echo $LANGCHAIN_PROJECT
```

#### 2. OpenAI API Errors
```python
# Check API key and model
import openai
client = openai.OpenAI()
models = client.models.list()
print([m.id for m in models.data if 'gpt-4' in m.id])
```

#### 3. Email Generation Failures
- Check OpenAI API quota and billing
- Verify model name (gpt-4o-mini vs gpt-4)
- Review prompt length (max 4096 tokens for input)

### Debug Mode
```python
# Enable debug logging
import logging
logging.getLogger("langsmith").setLevel(logging.DEBUG)
logging.getLogger("openai").setLevel(logging.DEBUG)
```

## Best Practices

### 1. Evaluation Strategy
- Run evaluations on representative sample data
- Use consistent evaluation criteria
- Track metrics over time for trends
- Compare different approaches (A/B testing)

### 2. Cost Optimization
- Use gpt-4o-mini for cost-effective generation
- Implement caching for repeated requests
- Monitor token usage and set alerts
- Batch API calls when possible

### 3. Data Privacy
- Never log sensitive candidate information
- Use anonymized data for evaluation
- Implement data retention policies
- Follow GDPR/privacy regulations

## Integration with Existing Workflow

The LangSmith integration is designed to be:
- **Non-intrusive**: Works alongside existing workflow
- **Optional**: Can be disabled via environment variables
- **Backward Compatible**: Doesn't break existing functionality
- **Performance Optimized**: Minimal overhead on workflow execution

## Next Steps

1. **Set up LangSmith account and API key**
2. **Run test workflow to verify tracing**
3. **Review evaluation metrics in dashboard**
4. **Set up monitoring alerts**
5. **Create evaluation datasets for A/B testing**
6. **Implement continuous improvement based on metrics**

For questions or issues, check the LangSmith documentation or create an issue in the project repository.
