import streamlit as st
import tiktoken
from googletrans import Translator
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config must be first Streamlit command
st.set_page_config(
    page_title="Dýr íslenska - Token Cost Analysis",
    page_icon="💰",
    layout="wide"
)

# GPT-4o Pricing (per 1M tokens)
PRICING = {
    'input': 2.50  # $2.50 per 1M input tokens
}

# Define pricing constant for calculations
PRICE_PER_1M_TOKENS = {
    'input': PRICING['input']  # $2.50 per 1M tokens
}

def count_tokens(text, encoding):
    """Count tokens in text using specified GPT-4o encoding."""
    if pd.isna(text) or text == "":
        return 0
    return len(encoding.encode(text))

def calculate_cost(tokens, price_per_million):
    """Calculate cost for given number of GPT-4o tokens."""
    return (tokens * price_per_million) / 1_000_000

@st.cache_resource
def get_encoding():
    return tiktoken.encoding_for_model('gpt-4o')

@st.cache_data
def load_data(price_per_1m_tokens):
    try:
        df = pd.read_csv('data/sentance_pairs_tokenized.csv')
        
        # Calculate total statistics
        total_eng_tokens = df['english_tokens'].sum()
        total_ice_tokens = df['icelandic_tokens'].sum()
        total_eng_words = df['english'].str.split().str.len().sum()
        total_ice_words = df['icelandic'].str.split().str.len().sum()
        
        # Create a new dataframe with the structure we need
        english_rows = pd.DataFrame({
            'language': ['English'] * len(df),
            'text': df['english'],
            'tokens': df['english_tokens'],
            'estimated_input_cost': df['english_tokens'] * price_per_1m_tokens['input'] / 1_000_000
        })
        
        icelandic_rows = pd.DataFrame({
            'language': ['Icelandic'] * len(df),
            'text': df['icelandic'],
            'tokens': df['icelandic_tokens'],
            'estimated_input_cost': df['icelandic_tokens'] * price_per_1m_tokens['input'] / 1_000_000
        })
        
        df_processed = pd.concat([english_rows, icelandic_rows], ignore_index=True)
        
        stats = {
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
        
        return df_processed, stats
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None

def main():
    # Initialize translator and GPT-4o encoding
    translator = Translator()
    encoding = get_encoding()
    
    # Load the data
    df, stats = load_data(PRICE_PER_1M_TOKENS)
    
    # Check if data loaded successfully before proceeding
    if df is None:
        st.stop()
    
    # Custom CSS
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stTextArea textarea {
            font-size: 1.2rem;
        }
        .token-box {
            background-color: #f0f2f6;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        .cost-box {
            background-color: #e6f3ff;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
        }
        .big-number {
            font-size: 2rem;
            font-weight: bold;
            color: #0066cc;
        }
        .header-text {
            color: #1f1f1f;
            font-size: 1.2rem;
            margin-bottom: 0.5rem;
        }
        .hero-section {
            text-align: center;
            padding: 2rem 0;
            background-color: #f8f9fa;
            margin-bottom: 2rem;
            border-radius: 10px;
        }
        .footer {
            text-align: center;
            padding: 2rem 0;
            margin-top: 3rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Hero section with logo
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
            <div class="hero-section">
                <h1>💬 GPT-4o Token Cost Dashboard for Icelandic</h1>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.image(
            "static/graphics/websitelogo.png",
            width=150,
            caption=None,
            use_column_width=False
        )
    
    st.markdown("""
        ## The Hidden Cost of Icelandic in AI: A Token Analysis
        *By [Magnus Smari](https://www.smarason.is) (2024)*

        Based on my analysis of 101 parallel English-Icelandic sentence pairs, Icelandic text consistently requires more tokens when processed by GPT-4o. The data shows that Icelandic uses on average 187% more tokens than English for the same content, with typical Icelandic sentences requiring 40 tokens compared to English's 14 tokens.

        At GPT-4o's current rates ($2.50 per million input tokens), this token disparity creates a significant cost difference for Icelandic language processing. This analysis also reveals implications for context window utilization, where Icelandic content effectively reduces the usable space in AI interactions.

        The complete dataset, analysis code, and interactive visualization tools are available in my open-source repository. Feel free to explore, use, or build upon this research to better understand token economics in different languages.

        **Current GPT-4o Pricing:**
        - Input tokens: $2.50 per 1M tokens (standard)
        
        *Pricing source: [OpenAI](https://openai.com/api/pricing/) (2.11.2024)*
    """)
    
    # Tabs for navigation
    tabs = st.tabs(["Token & Cost Calculator", "Cost Analysis Dashboard"])
    
    with tabs[0]:
        st.markdown("### Enter Icelandic text for GPT-4o analysis:")
        icelandic_text = st.text_area(
            label="Icelandic text input",
            height=150,
            placeholder="Type or paste Icelandic text here for GPT-4o token counting...",
            label_visibility="collapsed"
        )
        
        # Analyze button
        analyze_button = st.button("Analyze Text")
        
        if analyze_button and icelandic_text:
            try:
                # Translate to English
                translation = translator.translate(icelandic_text, src='is', dest='en')
                english_text = translation.text
                
                # Count GPT-4o tokens
                icelandic_tokens = count_tokens(icelandic_text, encoding)
                english_tokens = count_tokens(english_text, encoding)
                token_difference = icelandic_tokens - english_tokens
                
                # Calculate costs
                icelandic_input_cost = calculate_cost(icelandic_tokens, PRICING['input'])
                english_input_cost = calculate_cost(english_tokens, PRICING['input'])
                
                # Display results in two columns
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🇮🇸 Icelandic (GPT-4o)")
                    with st.container():
                        st.markdown('<div class="token-box">', unsafe_allow_html=True)
                        st.markdown(f"**Text:** {icelandic_text}")
                        st.markdown(f'<div class="big-number">{icelandic_tokens} tokens</div>', unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with st.container():
                        st.markdown('<div class="cost-box">', unsafe_allow_html=True)
                        st.markdown('<div class="header-text">GPT-4o Costs:</div>', unsafe_allow_html=True)
                        st.markdown(f"Input: ${icelandic_input_cost:.6f}")
                        st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown("### 🇬🇧 English Translation (GPT-4o)")
                    with st.container():
                        st.markdown('<div class="token-box">', unsafe_allow_html=True)
                        st.markdown(f"**Text:** {english_text}")
                        st.markdown(f'<div class="big-number">{english_tokens} tokens</div>', unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with st.container():
                        st.markdown('<div class="cost-box">', unsafe_allow_html=True)
                        st.markdown('<div class="header-text">GPT-4o Costs:</div>', unsafe_allow_html=True)
                        st.markdown(f"Input: ${english_input_cost:.6f}")
                        st.markdown("</div>", unsafe_allow_html=True)
                
                # Comparison section
                st.markdown("### 📊 GPT-4o Token Comparison")
                comparison_col1, comparison_col2 = st.columns(2)
                
                with comparison_col1:
                    st.markdown('<div class="token-box">', unsafe_allow_html=True)
                    st.markdown("**GPT-4o Token Difference:**")
                    st.markdown(f'<div class="big-number">{token_difference:+d} tokens</div>', unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with comparison_col2:
                    st.markdown('<div class="token-box">', unsafe_allow_html=True)
                    st.markdown("**GPT-4o Percentage Difference:**")
                    percentage = (token_difference / english_tokens * 100) if english_tokens > 0 else 0
                    st.markdown(f'<div class="big-number">{percentage:+.1f}%</div>', unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Translation error in GPT-4o analysis: {str(e)}")
    
    with tabs[1]:
        st.title("Dýr íslenska (Expensive Icelandic) - Token Cost Analysis")
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
            ice_tokens = df[df['language'] == 'Icelandic']['tokens'].mean()
            st.metric("Average Icelandic Tokens", f"{ice_tokens:.1f}")
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
                name='Icelandic Average'
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
        - Input tokens: $2.50 per 1M tokens (Standard)
        
        *Pricing source: OpenAI (as of February 2024)*
        """)
        
        # Calculate total costs
        eng_input_cost = stats['total_eng_tokens'] * PRICE_PER_1M_TOKENS['input']
        ice_input_cost = stats['total_ice_tokens'] * PRICE_PER_1M_TOKENS['input']
        
        st.markdown("""
        ### Total Cost Analysis
        
        #### English Text
        - Input cost: ${:.2f}
        
        #### Icelandic Text
        - Input cost: ${:.2f}
        
        #### Cost Difference
        - Input difference: ${:.2f}
        - Percentage increase: {:.1f}%
        """.format(
            eng_input_cost / 1_000_000,  # Convert to actual cost
            ice_input_cost / 1_000_000,  # Convert to actual cost
            (ice_input_cost - eng_input_cost) / 1_000_000,  # Convert difference to actual cost
            ((ice_input_cost - eng_input_cost) / eng_input_cost * 100)  # Calculate percentage
        ))
        
        # Add cost comparison visualization
        cost_fig = px.bar(
            df.groupby('language').sum().reset_index(),
            x=['English', 'Icelandic'],
            y=['estimated_input_cost'],
            barmode='group',
            title='Estimated Costs per Language (USD)',
            labels={
                'value': 'Cost (USD)',
                'variable': 'Cost Type'
            },
            color_discrete_sequence=['lightblue', 'darkred']
        )
        
        cost_fig.update_layout(
            height=500,
            xaxis_title="Language",
            yaxis_title="Estimated Cost (USD)",
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
        eng_input_cost_paper = estimated_eng_tokens * PRICE_PER_1M_TOKENS['input']
        ice_input_cost_paper = estimated_ice_tokens * PRICE_PER_1M_TOKENS['input']
        
        st.markdown("""
        ### Cost Analysis: 20-Page Research Paper
        
        Based on our analysis of {:,} text samples, we can estimate the costs for a typical 20-page research paper 
        (approximately {:,} words):
        
        #### English Research Paper
        - Estimated tokens: {:,.0f}
        - Input cost: ${:.2f}
        
        #### Icelandic Research Paper
        - Estimated tokens: {:,.0f}
        - Input cost: ${:.2f}
        
        #### Cost Difference
        - Additional tokens needed: {:,.0f}
        - Extra input cost: ${:.2f}
        - Percentage increase: {:.1f}%
        
        This means processing an Icelandic research paper costs about ${:.2f} more than the same paper in English.
        It also uses about {:,.0f} more tokens, which reduces the effective context window by that amount.
        """.format(
            stats['sample_count'],
            total_words,
            estimated_eng_tokens,
            eng_input_cost_paper / 1_000_000,  # Convert to actual cost
            estimated_ice_tokens,
            ice_input_cost_paper / 1_000_000,  # Convert to actual cost
            estimated_ice_tokens - estimated_eng_tokens,
            (ice_input_cost_paper - eng_input_cost_paper) / 1_000_000,  # Convert difference to actual cost
            ((ice_input_cost_paper - eng_input_cost_paper) / eng_input_cost_paper * 100),
            (ice_input_cost_paper - eng_input_cost_paper) / 1_000_000,  # Convert difference to actual cost
            estimated_ice_tokens - estimated_eng_tokens
        ))
        
        # Token & Cost Calculator
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
        
        # Calculate costs (divide by 1M to get cost in dollars)
        est_eng_input_cost = (est_eng_tokens * PRICE_PER_1M_TOKENS['input']) / 1_000_000
        est_ice_input_cost = (est_ice_tokens * PRICE_PER_1M_TOKENS['input']) / 1_000_000
        
        # Display results in columns
        calc_col1, calc_col2 = st.columns(2)
        
        with calc_col1:
            st.markdown("""
            #### English Estimates
            - Estimated tokens: {:,.0f}
            - Input cost: ${:.4f}
            """.format(
                est_eng_tokens,
                est_eng_input_cost
            ))
        
        with calc_col2:
            st.markdown("""
            #### Icelandic Estimates
            - Estimated tokens: {:,.0f}
            - Input cost: ${:.4f}
            """.format(
                est_ice_tokens,
                est_ice_input_cost
            ))
        
        # Show difference
        st.markdown("""
        #### Difference
        - Additional tokens needed: {:,.0f}
        - Extra cost: ${:.4f}
        - Percentage increase: {:.1f}%
        - Context window impact: {:,.0f} fewer tokens available
        
        *Note: Estimates based on average token-to-word ratios from our analysis.*
        """.format(
            est_ice_tokens - est_eng_tokens,
            est_ice_input_cost - est_eng_input_cost,
            ((est_ice_input_cost - est_eng_input_cost) / est_eng_input_cost * 100),
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
        
    # Footer with links
    st.markdown("""
        <div class="footer">
            <p>Created by <a href="https://www.smarason.is" target="_blank">Smarason</a></p>
            <p>View the source code on <a href="https://github.com/yourusername/gpt4o-token-calculator" target="_blank">GitHub</a></p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()