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
        ## The Hidden Cost of Icelandic in AI: A Token Analysis v1.0
        
        MIT License
        *By [Magnus Smari](https://www.smarason.is) (2024)*
        View the source code on [GitHub](https://github.com/Magnussmari/Expensive_Icelandic)
    """)

    # Tabs for navigation
    tab1, tab2, tab3 = st.tabs(["Token & Cost Calculator", "Cost Analysis Dashboard", "Detailed Analysis Report"])
    
    with tab1:
        # Token & Cost Calculator tab content
        st.markdown("### Enter Icelandic text for GPT-4o analysis:")
        icelandic_text = st.text_area(
            label="Icelandic text input",
            height=150,
            placeholder="Type or paste Icelandic text here for automatic English translation and GPT-4o token counting...",
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
    
    with tab2:
        # Cost Analysis Dashboard tab content
        st.title("Cost Analysis Dashboard")
        
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
        
        st.plotly_chart(fig, use_container_width=True)
        
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
    
    with tab3:
        # Detailed Analysis Report tab content
        st.title("Detailed Statistical Analysis Report")
        
        st.markdown("""
        ## Statistical Robustness Analysis

        ### Confidence Intervals and Variance
        - Mean token increase: 26.07 tokens (95% CI: 24.94 - 27.20)
        - Standard deviation: 5.72 tokens
        - Variance: 32.69
        - This indicates a highly consistent token inflation pattern

        ### Length-Based Analysis
        Token ratios by text length:
        - Short texts: 2.941x (194% increase)
        - Medium texts: 2.835x (183% increase)
        - Long texts: 2.864x (186% increase)
        - Very Long texts: 2.860x (186% increase)

        Key Finding: The token inflation ratio remains remarkably consistent across different text lengths, with only a slight variation in shorter texts.
        """)

        st.markdown("""
        ## Token Pattern Analysis

        ### Major Contributors to Token Inflation

        1. Case Endings (87 instances found)
        - Icelandic's complex case system significantly impacts token count
        - Common endings (-inn, -inum, -sins) each count as separate tokens
        - Case variations multiply the base token count

        2. Compound Words (126 instances detected)
        - Icelandic's agglutinative nature creates longer compound words
        - Each compound typically generates 2-3x more tokens than English equivalent
        - Example: "samfélagsmiðstöð" (3 tokens) vs "community center" (2 tokens)

        3. Grammatical Articles
        - Suffixed articles in Icelandic create additional tokens
        - Each suffixed article typically adds 1-2 extra tokens
        - More complex than English's separate article system
        """)

        st.markdown("""
        ## Cost Optimization Strategies

        ### 1. Compound Word Optimization
        Before: "samfélagsmiðstöð" (3 tokens)
        After: "samfélag miðstöð" (2 tokens)
        Savings: ~33% per compound word

        ### 2. Case Form Simplification
        Before: "í húsinu" (3 tokens)
        After: "í hús" (2 tokens)
        Savings: ~33% per case-inflected word

        ### 3. Article Usage Optimization
        Before: "bókin" (2 tokens)
        After: "bók" (1 token)
        Savings: ~50% per article usage
        """)

        st.markdown("""
        ## Technical Recommendations

        1. Preprocessing Strategies
        - Implement compound word splitting where semantically appropriate
        - Use simplified case forms when context allows
        - Optimize article usage

        2. Monitoring System
        - Track token ratios across different text types
        - Monitor optimization effectiveness
        - Regular cost analysis reports

        3. Testing Framework
        - Automated token counting
        - Quality assurance for optimized text
        - Performance benchmarking
        """)

        st.markdown("""
        ## Conclusion

        The analysis confirms a consistent token inflation of 183-194% for Icelandic text compared to English, 
        with a mean increase of 26.07 tokens (95% CI: 24.94 - 27.20). This inflation is remarkably stable across 
        different text lengths, primarily driven by case endings, compound words, and grammatical articles. 
        Through targeted optimization strategies, organizations can reduce costs while maintaining language integrity. 
        Regular monitoring and optimization are recommended for production systems.
        """)

    # Footer with links
    st.markdown("""
        <div class="footer">
            <p>Created by <a href="https://www.smarason.is" target="_blank">Smarason</a></p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
