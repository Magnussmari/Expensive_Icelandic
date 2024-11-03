import pandas as pd
import tiktoken
import logging
import numpy as np
from collections import Counter
from scipy import stats

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# GPT-4 Pricing (per 1M tokens)
PRICING = {
    'standard': {
        'input': 0.03,  # $0.03 per 1K input tokens
        'output': 0.06  # $0.06 per 1K output tokens
    }
}

def calculate_cost(tokens, price_per_thousand):
    """Calculate cost for given number of tokens."""
    return (tokens * price_per_thousand) / 1000

def count_tokens(text, encoding):
    """Count tokens in text using specified encoding."""
    if pd.isna(text):
        return 0
    return len(encoding.encode(text))

def calculate_confidence_interval(data, confidence=0.95):
    """Calculate confidence interval for token differences."""
    n = len(data)
    mean = np.mean(data)
    std_err = stats.sem(data)
    ci = stats.t.interval(confidence, n-1, mean, std_err)
    return {
        'mean': mean,
        'ci_lower': ci[0],
        'ci_upper': ci[1],
        'confidence': confidence
    }

def analyze_by_length(df):
    """Analyze token ratio patterns based on text length."""
    # Create length categories
    df['text_length'] = df['english'].str.len()
    df['length_category'] = pd.qcut(df['text_length'], q=4, labels=['Short', 'Medium', 'Long', 'Very Long'])
    
    # Calculate statistics by length category
    length_analysis = df.groupby('length_category').agg({
        'token_difference': ['mean', 'std', 'count'],
        'icelandic_tokens': 'mean',
        'english_tokens': 'mean'
    }).round(2)
    
    # Calculate token ratio by length category
    length_analysis['token_ratio'] = (
        length_analysis[('icelandic_tokens', 'mean')] / 
        length_analysis[('english_tokens', 'mean')]
    ).round(3)
    
    return length_analysis

def analyze_token_patterns(df):
    """Analyze specific features contributing to token inflation."""
    patterns = {
        'case_endings': 0,
        'compound_words': 0,
        'articles': 0
    }
    
    case_endings = ['inn', 'inum', 'sins', 'num', 'na', 'nir', 'num']
    
    for text in df['icelandic']:
        if pd.isna(text):
            continue
        
        words = text.split()
        patterns['compound_words'] += sum(1 for word in words if len(word) > 12)
        patterns['case_endings'] += sum(
            1 for word in words if any(word.endswith(ending) for ending in case_endings)
        )
        patterns['articles'] += sum(
            1 for word in words if word.lower() in ['hinn', 'hin', 'hið', 'þessi', 'þetta']
        )
    
    return patterns

def analyze_token_differences(df):
    """Analyze token differences and calculate costs."""
    df['token_difference'] = df['icelandic_tokens'] - df['english_tokens']
    
    diff_stats = {
        'mean_difference': df['token_difference'].mean(),
        'median_difference': df['token_difference'].median(),
        'std_difference': df['token_difference'].std(),
        'max_difference': df['token_difference'].max(),
        'min_difference': df['token_difference'].min(),
        'variance': df['token_difference'].var()
    }
    
    ci_stats = calculate_confidence_interval(df['token_difference'])
    diff_stats.update({
        'ci_lower': ci_stats['ci_lower'],
        'ci_upper': ci_stats['ci_upper']
    })
    
    length_stats = analyze_by_length(df)
    pattern_stats = analyze_token_patterns(df)
    
    # Calculate average costs per 1000 tokens
    avg_english_tokens = df['english_tokens'].mean()
    avg_icelandic_tokens = df['icelandic_tokens'].mean()
    
    costs = {
        'english': calculate_cost(1000, PRICING['standard']['input']),
        'icelandic': calculate_cost(1000, PRICING['standard']['input'])
    }
    
    # Find examples
    max_diff_idx = df['token_difference'].idxmax()
    min_diff_idx = df['token_difference'].idxmin()
    
    example_pairs = {
        'largest_difference': {
            'english': df.loc[max_diff_idx, 'english'],
            'icelandic': df.loc[max_diff_idx, 'icelandic'],
            'english_tokens': df.loc[max_diff_idx, 'english_tokens'],
            'icelandic_tokens': df.loc[max_diff_idx, 'icelandic_tokens'],
            'difference': df.loc[max_diff_idx, 'token_difference']
        },
        'smallest_difference': {
            'english': df.loc[min_diff_idx, 'english'],
            'icelandic': df.loc[min_diff_idx, 'icelandic'],
            'english_tokens': df.loc[min_diff_idx, 'english_tokens'],
            'icelandic_tokens': df.loc[min_diff_idx, 'icelandic_tokens'],
            'difference': df.loc[min_diff_idx, 'token_difference']
        }
    }
    
    return diff_stats, example_pairs, length_stats, pattern_stats, costs

def print_analysis(diff_stats, example_pairs, length_stats, pattern_stats, costs):
    """Print detailed analysis of token differences and costs."""
    logging.info("\n=== ENHANCED GPT-4 TOKEN AND COST ANALYSIS ===\n")
    
    logging.info("STATISTICAL ANALYSIS:")
    logging.info(f"Mean difference (Icelandic - English): {diff_stats['mean_difference']:.2f} tokens")
    logging.info(f"95% Confidence Interval: ({diff_stats['ci_lower']:.2f}, {diff_stats['ci_upper']:.2f})")
    logging.info(f"Standard deviation: {diff_stats['std_difference']:.2f}")
    logging.info(f"Variance: {diff_stats['variance']:.2f}")
    logging.info(f"Median difference: {diff_stats['median_difference']:.2f} tokens")
    
    logging.info("\nLENGTH-BASED ANALYSIS:")
    logging.info(length_stats)
    
    logging.info("\nTOKEN PATTERN ANALYSIS:")
    logging.info(f"Case endings found: {pattern_stats['case_endings']}")
    logging.info(f"Compound words detected: {pattern_stats['compound_words']}")
    logging.info(f"Grammatical articles: {pattern_stats['articles']}")
    
    logging.info("\nCOST ANALYSIS (per 1000 tokens):")
    logging.info(f"English: ${costs['english']:.4f}")
    logging.info(f"Icelandic: ${costs['icelandic']:.4f}")
    
    logging.info("\nLARGEST TOKEN DIFFERENCE EXAMPLE:")
    logging.info(f"English ({example_pairs['largest_difference']['english_tokens']} tokens):")
    logging.info(example_pairs['largest_difference']['english'])
    logging.info(f"Icelandic ({example_pairs['largest_difference']['icelandic_tokens']} tokens):")
    logging.info(example_pairs['largest_difference']['icelandic'])

def process_csv(input_csv, output_csv, model='gpt-4'):
    """Process CSV and analyze token differences between English and Icelandic."""
    try:
        encoding = tiktoken.encoding_for_model(model)
        df = pd.read_csv(input_csv)
        
        df['english_tokens'] = df['english'].apply(lambda x: count_tokens(x, encoding))
        df['icelandic_tokens'] = df['icelandic'].apply(lambda x: count_tokens(x, encoding))
        
        diff_stats, example_pairs, length_stats, pattern_stats, costs = analyze_token_differences(df)
        print_analysis(diff_stats, example_pairs, length_stats, pattern_stats, costs)
        
        df.to_csv(output_csv, index=False)
        logging.info(f"\nAnalysis saved to: {output_csv}")
        
    except Exception as e:
        logging.error(f"Error processing CSV: {str(e)}")
        raise

if __name__ == "__main__":
    process_csv('data/sentance_pairs.csv', 'data/sentance_pairs_tokenized.csv')
