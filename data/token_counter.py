import pandas as pd
import tiktoken
import logging
import numpy as np
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# GPT-4 Pricing (per 1M tokens)
PRICING = {
    'standard': {
        'input': 2.50,  # $2.50 per 1M input tokens
        'output': 10.00  # $10.00 per 1M output tokens
    },
    'batch': {
        'input': 1.25,  # $1.25 per 1M input tokens
        'output': 5.00  # $5.00 per 1M output tokens
    }
}

def calculate_cost(tokens, price_per_million):
    """Calculate cost for given number of tokens."""
    return (tokens * price_per_million) / 1_000_000

def count_tokens(text, encoding):
    """Count tokens in text using specified encoding."""
    if pd.isna(text):
        return 0
    return len(encoding.encode(text))

def analyze_token_differences(df):
    """Analyze token differences and calculate costs."""
    # Calculate token differences
    df['token_difference'] = df['icelandic_tokens'] - df['english_tokens']
    
    # Basic statistics about differences
    diff_stats = {
        'mean_difference': df['token_difference'].mean(),
        'median_difference': df['token_difference'].median(),
        'std_difference': df['token_difference'].std(),
        'max_difference': df['token_difference'].max(),
        'min_difference': df['token_difference'].min()
    }
    
    # Calculate costs
    total_english_tokens = df['english_tokens'].sum()
    total_icelandic_tokens = df['icelandic_tokens'].sum()
    
    costs = {
        'standard': {
            'english': {
                'input': calculate_cost(total_english_tokens, PRICING['standard']['input']),
                'output': calculate_cost(total_english_tokens, PRICING['standard']['output'])
            },
            'icelandic': {
                'input': calculate_cost(total_icelandic_tokens, PRICING['standard']['input']),
                'output': calculate_cost(total_icelandic_tokens, PRICING['standard']['output'])
            }
        },
        'batch': {
            'english': {
                'input': calculate_cost(total_english_tokens, PRICING['batch']['input']),
                'output': calculate_cost(total_english_tokens, PRICING['batch']['output'])
            },
            'icelandic': {
                'input': calculate_cost(total_icelandic_tokens, PRICING['batch']['input']),
                'output': calculate_cost(total_icelandic_tokens, PRICING['batch']['output'])
            }
        },
        'per_sentence': {
            'english': {
                'input': calculate_cost(df['english_tokens'].mean(), PRICING['standard']['input']),
                'output': calculate_cost(df['english_tokens'].mean(), PRICING['standard']['output'])
            },
            'icelandic': {
                'input': calculate_cost(df['icelandic_tokens'].mean(), PRICING['standard']['input']),
                'output': calculate_cost(df['icelandic_tokens'].mean(), PRICING['standard']['output'])
            }
        }
    }
    
    # Find sentences with largest and smallest differences
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
    
    # Distribution of differences
    difference_distribution = Counter(df['token_difference'])
    
    return diff_stats, example_pairs, difference_distribution, costs

def print_analysis(diff_stats, example_pairs, difference_distribution, costs):
    """Print detailed analysis of token differences and costs."""
    logging.info("\n=== GPT-4 TOKEN AND COST ANALYSIS ===\n")
    
    # Print model information
    logging.info("MODEL INFORMATION:")
    logging.info("Using GPT-4 model for token counting")
    logging.info("Standard Pricing: $2.50/1M input tokens, $10.00/1M output tokens")
    logging.info("Batch API Pricing: $1.25/1M input tokens, $5.00/1M output tokens\n")
    
    # Print basic statistics
    logging.info("DIFFERENCE STATISTICS:")
    logging.info(f"Average difference (Icelandic - English): {diff_stats['mean_difference']:.2f} tokens")
    logging.info(f"Median difference: {diff_stats['median_difference']:.2f} tokens")
    logging.info(f"Standard deviation: {diff_stats['std_difference']:.2f}")
    logging.info(f"Maximum difference: {diff_stats['max_difference']} tokens")
    logging.info(f"Minimum difference: {diff_stats['min_difference']} tokens\n")
    
    # Print cost analysis
    logging.info("COST ANALYSIS (per sentence average):")
    logging.info("English:")
    logging.info(f"  Input cost: ${costs['per_sentence']['english']['input']:.6f}")
    logging.info(f"  Output cost: ${costs['per_sentence']['english']['output']:.6f}")
    logging.info("Icelandic:")
    logging.info(f"  Input cost: ${costs['per_sentence']['icelandic']['input']:.6f}")
    logging.info(f"  Output cost: ${costs['per_sentence']['icelandic']['output']:.6f}\n")
    
    logging.info("BATCH API COST COMPARISON (total dataset):")
    logging.info("English:")
    logging.info(f"  Standard API Input: ${costs['standard']['english']['input']:.4f}")
    logging.info(f"  Batch API Input: ${costs['batch']['english']['input']:.4f}")
    logging.info("Icelandic:")
    logging.info(f"  Standard API Input: ${costs['standard']['icelandic']['input']:.4f}")
    logging.info(f"  Batch API Input: ${costs['batch']['icelandic']['input']:.4f}\n")
    
    # Print example of largest difference
    logging.info("LARGEST TOKEN DIFFERENCE EXAMPLE:")
    logging.info(f"English ({example_pairs['largest_difference']['english_tokens']} tokens):")
    logging.info(example_pairs['largest_difference']['english'])
    logging.info(f"Icelandic ({example_pairs['largest_difference']['icelandic_tokens']} tokens):")
    logging.info(example_pairs['largest_difference']['icelandic'])
    logging.info(f"Difference: {example_pairs['largest_difference']['difference']} tokens\n")
    
    # Print distribution of differences
    logging.info("DIFFERENCE DISTRIBUTION (Most Common):")
    for diff, count in sorted(difference_distribution.most_common(5)):
        logging.info(f"Difference of {diff} tokens: {count} sentence pairs")

def process_csv(input_csv, output_csv, model='gpt-4o'):
    """Process CSV and analyze token differences between English and Icelandic."""
    try:
        # Load encoding and read CSV
        encoding = tiktoken.encoding_for_model(model)
        df = pd.read_csv(input_csv)
        
        # Count tokens
        df['english_tokens'] = df['english'].apply(lambda x: count_tokens(x, encoding))
        df['icelandic_tokens'] = df['icelandic'].apply(lambda x: count_tokens(x, encoding))
        
        # Analyze differences and costs
        diff_stats, example_pairs, difference_distribution, costs = analyze_token_differences(df)
        print_analysis(diff_stats, example_pairs, difference_distribution, costs)
        
        # Save results
        df.to_csv(output_csv, index=False)
        logging.info(f"\nAnalysis saved to: {output_csv}")
        
    except Exception as e:
        logging.error(f"Error processing CSV: {str(e)}")
        raise

if __name__ == "__main__":
    process_csv('data/sentance_pairs.csv', 'data/sentance_pairs_tokenized.csv')
