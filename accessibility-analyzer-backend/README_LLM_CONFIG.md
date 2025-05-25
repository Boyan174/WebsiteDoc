# LLM Configuration Guide

This accessibility analyzer backend now supports multiple LLM providers. You can easily switch between OpenAI and Anthropic models.

## Supported Providers

1. **OpenAI** (default)
   - Default model: `gpt-4o`

2. **Anthropic**
   - Default model: `claude-3-5-sonnet-20240620`

## Configuration

### Environment Variables

Set the following environment variables in your `.env` file:

```env
# Choose your provider: "openai" or "anthropic"
MODEL_PROVIDER=openai

# For OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o  # Optional, defaults to gpt-4o

# For Anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-5-sonnet-20240620  # Optional, defaults to claude-3-5-sonnet-20240620
```

### Switching Providers

To switch from OpenAI to Anthropic:

1. Update your `.env` file:
   ```env
   MODEL_PROVIDER=anthropic
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

2. Restart your backend server

### Programmatic Usage

You can also use different models programmatically by modifying the `langchain_service.py`:

```python
from services.langchain_service import get_llm

# Use Anthropic for a specific task
anthropic_llm = get_llm(provider="anthropic", model="claude-3-5-sonnet-20240620")

# Use OpenAI with custom parameters
openai_llm = get_llm(provider="openai", model="gpt-4", temperature=0.7, max_tokens=2048)
```

## Installation

Make sure to install the required dependencies:

```bash
pip install -r requirements.txt
```

This will install both `langchain-openai` and `langchain-anthropic` packages.

## Cost Considerations

- **OpenAI GPT-4o**: More cost-effective for general use
- **Anthropic Claude 3.5 Sonnet**: Excellent for complex analysis and longer contexts
- **Anthropic Claude 3 Haiku**: Fast and cost-effective for simpler tasks

## Troubleshooting

1. **API Key Issues**: Ensure your API keys are correctly set in the `.env` file
2. **Model Not Found**: Check that you're using a valid model name for your chosen provider
3. **Rate Limits**: Both providers have rate limits; consider implementing retry logic if needed

## Example Usage

Here's how the service automatically uses your configured provider:

```python
# In langchain_service.py
llm = get_llm()  # Uses MODEL_PROVIDER from .env

# The rest of your code remains the same
html_chain = html_analysis_prompt | llm | StrOutputParser()
```

The modular design ensures that switching between providers requires minimal code changes.
