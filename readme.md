# GPT-4o Token Cost Calculator for Icelandic

A Streamlit application that analyzes and compares token costs between Icelandic and English text using GPT-4o's tokenizer.

## Features

- Real-time token counting for Icelandic and English text
- Cost estimation for GPT-4o input tokens
- Translation between Icelandic and English
- Comparative analysis dashboard with visualizations
- Token cost calculator for common document lengths

## Pricing

Current GPT-4o pricing used in calculations:
- Input: $2.50 per 1M tokens

*Pricing source: OpenAI (as of February 2024)*

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit application:
```bash
streamlit run icetoke.py
```

## Data

The analysis is based on 102 text samples in both English and Icelandic.