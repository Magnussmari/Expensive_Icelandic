import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import tiktoken

# Set page config
st.set_page_config(
    page_title="Dýr íslenska - Token Cost Analysis",
    page_icon="💰",
    layout="wide"
)

# Define pricing constants FIRST
PRICE_PER_1K_TOKENS = {
    'input': 0.0025 / 1000,  # $2.50 per 1M tokens = $0.0025 per 1K tokens = $0.0000025 per token
    'output': 0.01 / 1000    # $10.00 per 1M tokens = $0.01 per 1K tokens = $0.00001 per token
}

# For batch pricing
BATCH_PRICE_PER_1K_TOKENS = {
    'input': 0.00125 / 1000,  # $1.25 per 1M tokens = $0.00125 per 1K tokens = $0.00000125 per token
    'output': 0.01 / 1000     # $10.00 per 1M tokens = $0.01 per 1K tokens = $0.00001 per token
}

# Add tiktoken encoding
@st.cache_resource
def get_encoding():
    return tiktoken.encoding_for_model('gpt-4o')

encoding = get_encoding()

def count_tokens(text):
    """Count tokens in text using GPT-4o encoding."""
    if pd.isna(text) or text == "":
        return 0
    return len(encoding.encode(str(text)))

# Load and prepare data
@st.cache_data
def load_data(price_per_1k_tokens):
    try:
        df = pd.read_csv('token_comp.csv')
        
        # Calculate total statistics
        total_eng_tokens = df['english_tokens'].sum()
        total_ice_tokens = df['icelandic_tokens'].sum()
        total_eng_words = df['english'].str.split().str.len().sum()
        total_ice_words = df['icelandic'].str.split().str.len().sum()
        
        # Create a new dataframe with the structure we need
        df_processed = pd.DataFrame()
        
        # Add English entries
        english_rows = pd.DataFrame({
            'language': ['English'] * len(df),
            'text': df['english'],
            'tokens': df['english_tokens'],
            'estimated_input_cost': df['english_tokens'] * price_per_1k_tokens['input'],
            'estimated_output_cost': df['english_tokens'] * price_per_1k_tokens['output']
        })
        
        # Add Icelandic entries
        icelandic_rows = pd.DataFrame({
            'language': ['Icelandic'] * len(df),
            'text': df['icelandic'],
            'tokens': df['icelandic_tokens'],
            'estimated_input_cost': df['icelandic_tokens'] * price_per_1k_tokens['input'],
            'estimated_output_cost': df['icelandic_tokens'] * price_per_1k_tokens['output']
        })
        
        # Combine the entries
        df_processed = pd.concat([english_rows, icelandic_rows], ignore_index=True)
        
        return df_processed, {
            'total_eng_tokens': total_eng_tokens,
            'total_ice_tokens': total_ice_tokens,
            'total_eng_words': total_eng_words,
            'total_ice_words': total_ice_words,
            'avg_eng_tokens': df['english_tokens'].mean(),
            'avg_ice_tokens': df['icelandic_tokens'].mean(),
            'max_difference': df['token_difference'].max(),
            'min_difference': df['token_difference'].min(),
            'avg_difference': df['token_difference'].mean(),
            'sample_count': len(df)
        }
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None

# Load the data
df, stats = load_data(PRICE_PER_1K_TOKENS)

# Check if data loaded successfully before proceeding
if df is None:
    st.stop()

# Add title and description
st.title("Dýr íslenska (Expensive Icelandic)")
st.markdown("""
    This dashboard demonstrates the relative cost of processing Icelandic text 
    compared to English in terms of AI tokens.
    
    ### About the Data
    - The analysis is based on **102 text samples** in both English and Icelandic
    - Each sample contains the same content translated between languages
    - Token counts are calculated using GPT-4o's tokenizer
    - The samples include various topics and sentence structures
    - All texts are real-world examples of natural language usage
    
    ### What are Tokens?
    Tokens are the basic units that AI models process text with. They can be:
    - Parts of words
    - Whole words
    - Punctuation marks
    - Special characters
    
    ### Why Does This Matter?
    Higher token counts in Icelandic affect two crucial aspects:
    
    1. **Cost**: 
        - More tokens = Higher processing costs
        - Each token has a specific price in AI models
    
    2. **Context Window Limitations**:
        - AI models have fixed context window sizes (e.g., 8K, 16K, 32K tokens)
        - Icelandic text uses more tokens for the same content
        - This means you can fit less actual content in each conversation
        - Example: A 32K context window might fit only 25K tokens worth of Icelandic content that would fit as 32K in English
""")

# Create main metrics
col1, col2, col3 = st.columns(3)
with col1:
    avg_tokens = df['tokens'].mean()
    st.metric("Average Tokens", f"{avg_tokens:.1f}")
with col2:
    ice_tokens = df[df['language'] == 'Icelandic']['tokens'].iloc[0]
    st.metric("Icelandic Tokens", f"{ice_tokens:.1f}")
with col3:
    percent_difference = ((ice_tokens - avg_tokens) / avg_tokens) * 100
    st.metric("% Above Average", f"{percent_difference:.1f}%")

# Create main bar chart
fig = px.bar(
    df.sort_values('tokens', ascending=True),
    x='tokens',
    y='language',
    orientation='h',
    title='Token Usage by Language',
    color='tokens',
    color_continuous_scale='Viridis'
)

fig.update_layout(
    height=500,
    xaxis_title="Number of Tokens",
    yaxis_title="Language",
    yaxis={'categoryorder':'total ascending'}
)

# Highlight Icelandic
fig.add_traces(
    go.Bar(
        x=[ice_tokens],
        y=['Icelandic'],
        marker_color='red',
        name='Icelandic'
    )
)

st.plotly_chart(fig, use_container_width=True)

# Add contextual information
st.markdown("""
### Why is this important?

The number of tokens used affects the cost of using AI services like GPT-4o. 
More tokens mean higher costs for:
- Translation services
- Text analysis
- AI-powered applications

This visualization shows how processing Icelandic text can be more expensive 
due to its complex morphological structure and longer word forms.
""")

# Add cost comparison
st.subheader("Cost Comparison")

# Add pricing information
st.markdown("""
### GPT-4o Pricing Information
- Input tokens: $2.50 per 1M tokens
- Output tokens: $10.00 per 1M tokens

*Pricing source: OpenAI (as of February 2024)*
""")

# Calculate total costs
eng_input_cost = (stats['total_eng_tokens'] * PRICE_PER_1K_TOKENS['input'])
ice_input_cost = (stats['total_ice_tokens'] * PRICE_PER_1K_TOKENS['input'])
eng_output_cost = (stats['total_eng_tokens'] * PRICE_PER_1K_TOKENS['output'])
ice_output_cost = (stats['total_ice_tokens'] * PRICE_PER_1K_TOKENS['output'])

st.markdown("""
### Total Cost Analysis

#### English Text
- Input cost: ${:.2f}
- Output cost: ${:.2f}
- Total cost: ${:.2f}

#### Icelandic Text
- Input cost: ${:.2f}
- Output cost: ${:.2f}
- Total cost: ${:.2f}

#### Cost Difference
- Input difference: ${:.2f}
- Output difference: ${:.2f}
- Total difference: ${:.2f}
- Percentage increase: {:.1f}%
""".format(
    eng_input_cost,
    eng_output_cost,
    eng_input_cost + eng_output_cost,
    ice_input_cost,
    ice_output_cost,
    ice_input_cost + ice_output_cost,
    ice_input_cost - eng_input_cost,
    ice_output_cost - eng_output_cost,
    (ice_input_cost + ice_output_cost) - (eng_input_cost + eng_output_cost),
    ((ice_input_cost + ice_output_cost) - (eng_input_cost + eng_output_cost)) / (eng_input_cost + eng_output_cost) * 100
))

# Add cost comparison visualization
cost_fig = px.bar(
    df.sort_values('estimated_input_cost', ascending=True),
    x=['estimated_input_cost', 'estimated_output_cost'],
    y='language',
    orientation='h',
    title='Estimated Costs per Language (USD per text sample)',
    color_discrete_map={
        'estimated_input_cost': 'lightblue',
        'estimated_output_cost': 'darkred'
    },
    labels={
        'estimated_input_cost': 'Input Cost (USD)',
        'estimated_output_cost': 'Output Cost (USD)',
        'value': 'Cost (USD)',
        'variable': 'Cost Type'
    }
)

cost_fig.update_layout(
    height=500,
    xaxis_title="Estimated Cost (USD)",
    yaxis_title="Language",
    yaxis={'categoryorder':'total ascending'},
    barmode='group',
    showlegend=True,
    legend_title_text="Cost Type"
)

st.plotly_chart(cost_fig, use_container_width=True)

# Add statistics after the description
st.markdown("""
### Dataset Statistics
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### English Text
    - Total words: {:,}
    - Total tokens: {:,}
    - Average tokens per sample: {:.1f}
    """.format(
        stats['total_eng_words'],
        stats['total_eng_tokens'],
        stats['avg_eng_tokens']
    ))

with col2:
    st.markdown("""
    #### Icelandic Text
    - Total words: {:,}
    - Total tokens: {:,}
    - Average tokens per sample: {:.1f}
    """.format(
        stats['total_ice_words'],
        stats['total_ice_tokens'],
        stats['avg_ice_tokens']
    ))

st.markdown("""
#### Token Difference Analysis
- Average difference: {:.1f} tokens
- Maximum difference: {} tokens
- Minimum difference: {} tokens
- Sample size: {} text pairs
- Average increase: {:.1f}%

This means that Icelandic text typically requires about {:.1f}% more tokens than the same content in English, 
which directly affects both costs and context window utilization.
""".format(
    stats['avg_difference'],
    stats['max_difference'],
    stats['min_difference'],
    stats['sample_count'],
    ((stats['total_ice_tokens'] - stats['total_eng_tokens']) / stats['total_eng_tokens'] * 100),
    ((stats['total_ice_tokens'] - stats['total_eng_tokens']) / stats['total_eng_tokens'] * 100)
))

# Calculate average tokens per word
eng_tokens_per_word = stats['total_eng_tokens'] / stats['total_eng_words']
ice_tokens_per_word = stats['total_ice_tokens'] / stats['total_ice_words']

# Estimate for a 20-page research paper (assuming ~500 words per page)
PAGES = 20
WORDS_PER_PAGE = 500
total_words = PAGES * WORDS_PER_PAGE

# Estimate tokens for research paper
estimated_eng_tokens = total_words * eng_tokens_per_word
estimated_ice_tokens = total_words * ice_tokens_per_word

# Calculate costs for research paper
eng_input_cost = (estimated_eng_tokens * PRICE_PER_1K_TOKENS['input'])
ice_input_cost = (estimated_ice_tokens * PRICE_PER_1K_TOKENS['input'])
eng_output_cost = (estimated_eng_tokens * PRICE_PER_1K_TOKENS['output'])
ice_output_cost = (estimated_ice_tokens * PRICE_PER_1K_TOKENS['output'])

st.markdown("""
### Cost Analysis: 20-Page Research Paper

Based on our analysis of {:,} text samples, we can estimate the costs for a typical 20-page research paper 
(approximately {:,} words):

#### English Research Paper
- Estimated tokens: {:,.0f}
- Input cost: ${:.2f}
- Output cost: ${:.2f}
- Total cost: ${:.2f}

#### Icelandic Research Paper
- Estimated tokens: {:,.0f}
- Input cost: ${:.2f}
- Output cost: ${:.2f}
- Total cost: ${:.2f}

#### Cost Difference
- Additional tokens needed: {:,.0f}
- Extra input cost: ${:.2f}
- Extra output cost: ${:.2f}
- Total extra cost: ${:.2f}
- Percentage increase: {:.1f}%

This means processing an Icelandic research paper costs about ${:.2f} more than the same paper in English.
It also uses about {:,.0f} more tokens, which reduces the effective context window by that amount.
""".format(
    stats['sample_count'],
    total_words,
    estimated_eng_tokens,
    eng_input_cost,
    eng_output_cost,
    eng_input_cost + eng_output_cost,
    estimated_ice_tokens,
    ice_input_cost,
    ice_output_cost,
    ice_input_cost + ice_output_cost,
    estimated_ice_tokens - estimated_eng_tokens,
    ice_input_cost - eng_input_cost,
    ice_output_cost - eng_output_cost,
    (ice_input_cost + ice_output_cost) - (eng_input_cost + eng_output_cost),
    ((ice_input_cost + ice_output_cost) - (eng_input_cost + eng_output_cost)) / (eng_input_cost + eng_output_cost) * 100,
    (ice_input_cost + ice_output_cost) - (eng_input_cost + eng_output_cost),
    estimated_ice_tokens - estimated_eng_tokens
))

# After your other statistics, add this calculator section:

st.markdown("""
### Token & Cost Calculator
Enter the number of words to estimate tokens and costs in both languages, based on our analysis of {:,} samples.
""".format(stats['sample_count']))

# Calculator input
word_count = st.number_input(
    "Number of words:",
    min_value=1,
    value=500,
    step=100,
    help="Enter the number of words in your text"
)

# Calculate estimates
est_eng_tokens = word_count * eng_tokens_per_word
est_ice_tokens = word_count * ice_tokens_per_word

# Calculate costs
est_eng_input_cost = est_eng_tokens * PRICE_PER_1K_TOKENS['input']
est_eng_output_cost = est_eng_tokens * PRICE_PER_1K_TOKENS['output']
est_ice_input_cost = est_ice_tokens * PRICE_PER_1K_TOKENS['input']
est_ice_output_cost = est_ice_tokens * PRICE_PER_1K_TOKENS['output']

# Display results in columns
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### English Estimates
    - Estimated tokens: {:,.0f}
    - Input cost: ${:.2f}
    - Output cost: ${:.2f}
    - Total cost: ${:.2f}
    """.format(
        est_eng_tokens,
        est_eng_input_cost,
        est_eng_output_cost,
        est_eng_input_cost + est_eng_output_cost
    ))

with col2:
    st.markdown("""
    #### Icelandic Estimates
    - Estimated tokens: {:,.0f}
    - Input cost: ${:.2f}
    - Output cost: ${:.2f}
    - Total cost: ${:.2f}
    """.format(
        est_ice_tokens,
        est_ice_input_cost,
        est_ice_output_cost,
        est_ice_input_cost + est_ice_output_cost
    ))

# Show difference
st.markdown("""
#### Difference
- Additional tokens needed: {:,.0f}
- Extra cost: ${:.2f}
- Percentage increase: {:.1f}%
- Context window impact: {:,.0f} fewer tokens available

*Note: Estimates based on average token-to-word ratios from our analysis.*
""".format(
    est_ice_tokens - est_eng_tokens,
    (est_ice_input_cost + est_ice_output_cost) - (est_eng_input_cost + est_eng_output_cost),
    ((est_ice_input_cost + est_ice_output_cost) - (est_eng_input_cost + est_eng_output_cost)) / (est_eng_input_cost + est_eng_output_cost) * 100,
    est_ice_tokens - est_eng_tokens
))

# Add some common document length presets
st.markdown("""
### Common Document Lengths
- Short email: ~100 words
- Blog post: ~800 words
- Academic paper: ~5,000 words
- Novel: ~90,000 words
- PhD thesis: ~80,000 words
""")