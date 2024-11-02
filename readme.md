

Ah yes, let me correct that for GPT-4o specifically:

```markdown
# Dýr íslenska (Expensive Icelandic) - Token Analysis

A comparative analysis of token usage between English and Icelandic texts, demonstrating the cost implications when using GPT-4o.

## Method

### Data Collection
- 102 text samples in both English and Icelandic
- Generated using GPT-4o and Claude 3.5 Sonnet
- Edited and verified using Cursor IDE
- Stored in `token_comp.csv`

### Token Counting
We use `tiktoken`, OpenAI's fast BPE tokenizer, for accurate token counting:

```python
import tiktoken

# Get the tokenizer for GPT-4o
enc = tiktoken.encoding_for_model("gpt-4o")

# Count tokens
def count_tokens(text):
    if pd.isna(text) or text == "":
        return 0
    return len(enc.encode(str(text)))
```

### Pricing Structure (GPT-4o)
```
Model     Input                   Output
GPT-4o    $2.50 / 1M tokens      $10.00 / 1M tokens
         ($1.25 / 1M batch)
```

### Analysis Components
1. Token comparison between languages
2. Cost calculation using current GPT-4o pricing:
   - Standard Input: $2.50 per 1M tokens
   - Batch Input: $1.25 per 1M tokens
   - Output: $10.00 per 1M tokens
3. Context window impact assessment
4. Interactive cost calculator

## Key Findings
- Icelandic texts consistently require more tokens than English
- Average increase: {:.1f}% more tokens for Icelandic
- Impact on both cost and context window utilization
- Significant implications for large-scale text processing

## Tools Used
- Python with Streamlit for visualization
- tiktoken for token counting
- pandas for data management
- plotly for interactive charts

## Installation

```bash
pip install tiktoken streamlit pandas plotly
```

## Usage

```bash
streamlit run dashboard.py
```

## Resources
- Token counting: [OpenAI Tokenizer](https://platform.openai.com/tokenizer)
- Pricing reference: [OpenAI GPT-4o Pricing](https://openai.com/api/pricing/)
- More about BPE tokenization: [tiktoken documentation](https://github.com/openai/tiktoken)

## Author
Magnus Smari  
[smarason.is](https://smarason.is)  
2024

## License
MIT License
```

The key changes:
1. Updated model name to GPT-4o throughout
2. Added batch pricing information
3. Clarified the pricing structure with a dedicated section
4. Updated the tokenizer model name to "gpt-4o"