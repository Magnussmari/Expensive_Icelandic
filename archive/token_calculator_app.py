import streamlit as st
import tiktoken
from googletrans import Translator
import pandas as pd

# GPT-4o Optimized Pricing (per 1M tokens)
PRICING = {
    'standard': {
        'input': 2.50,  # $2.50 per 1M input tokens for GPT-4o
        'output': 10.00  # $10.00 per 1M output tokens for GPT-4o
    },
    'batch': {
        'input': 1.25,  # $1.25 per 1M input tokens for GPT-4o (cached)
        'output': 10.00  # $10.00 per 1M output tokens for GPT-4o
    }
}

def count_tokens(text, encoding):
    """Count tokens in text using specified GPT-4o encoding."""
    if pd.isna(text) or text == "":
        return 0
    return len(encoding.encode(text))

def calculate_cost(tokens, price_per_million):
    """Calculate cost for given number of GPT-4o tokens."""
    return (tokens * price_per_million) / 1_000_000

def main():
    # Page config
    st.set_page_config(
        page_title="GPT-4o Token Calculator",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

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
                <h1>💬 GPT-4o Token Calculator</h1>
                <p>A powerful tool for analyzing token usage in Icelandic-English translations</p>
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
        This calculator uses GPT-4o model pricing:
        - Input tokens: $2.50 per 1M tokens with GPT-4o
        - Output tokens: $10.00 per 1M tokens with GPT-4o
        
        Pricing source: https://openai.com/api/pricing/  (2.11.2024)
    """)
    
    # Initialize translator and GPT-4o encoding
    translator = Translator()
    encoding = tiktoken.encoding_for_model('gpt-4o')
    
    # Text input
    st.markdown("### Enter Icelandic text for GPT-4o analysis:")
    icelandic_text = st.text_area(
        label="Icelandic text input",
        height=100,
        placeholder="Type or paste Icelandic text here for GPT-4o token counting...",
        label_visibility="collapsed"
    )
    
    # Add analyze button
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
            
            # Display results in two columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🇮🇸 Icelandic (GPT-4o)")
                with st.container():
                    st.markdown('<div class="token-box">', unsafe_allow_html=True)
                    st.markdown(f"**Text:** {icelandic_text}")
                    st.markdown(f'<div class="big-number">{icelandic_tokens} GPT-4o tokens</div>', unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with st.container():
                    st.markdown('<div class="cost-box">', unsafe_allow_html=True)
                    st.markdown('<div class="header-text">GPT-4o Costs:</div>', unsafe_allow_html=True)
                    st.markdown(f"Input: ${calculate_cost(icelandic_tokens, PRICING['standard']['input']):.6f}")
                    st.markdown(f"Output: ${calculate_cost(icelandic_tokens, PRICING['standard']['output']):.6f}")
                    st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("### 🇬🇧 English Translation (GPT-4o)")
                with st.container():
                    st.markdown('<div class="token-box">', unsafe_allow_html=True)
                    st.markdown(f"**Text:** {english_text}")
                    st.markdown(f'<div class="big-number">{english_tokens} GPT-4o tokens</div>', unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with st.container():
                    st.markdown('<div class="cost-box">', unsafe_allow_html=True)
                    st.markdown('<div class="header-text">GPT-4o Costs:</div>', unsafe_allow_html=True)
                    st.markdown(f"Input: ${calculate_cost(english_tokens, PRICING['standard']['input']):.6f}")
                    st.markdown(f"Output: ${calculate_cost(english_tokens, PRICING['standard']['output']):.6f}")
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

    # Footer with links
    st.markdown("""
        <div class="footer">
            <p>Created by <a href="https://www.smarason.is" target="_blank">Smarason</a></p>
            <p>View the source code on <a href="https://github.com/yourusername/gpt4o-token-calculator" target="_blank">GitHub</a></p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
