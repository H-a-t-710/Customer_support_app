import re
import unicodedata
from typing import List, Dict, Any

def preprocess_text(text: str) -> str:
    """
    Preprocess text to improve quality for embeddings and search.
    
    Args:
        text (str): Input text
        
    Returns:
        str: Preprocessed text
    """
    if not text:
        return ""
    
    # Normalize unicode characters
    text = unicodedata.normalize("NFKD", text)
    
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()
    
    # Remove URLs
    text = re.sub(r"http[s]?://\S+", "", text)
    
    # Fix common punctuation issues
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    
    return text

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract potential keywords from text.
    This is a simple implementation. For production,
    consider using NLP libraries like spaCy.
    
    Args:
        text (str): Input text
        max_keywords (int): Maximum number of keywords
        
    Returns:
        List[str]: Extracted keywords
    """
    # Preprocess text
    text = preprocess_text(text)
    
    # Split into words
    words = re.findall(r"\b\w+\b", text.lower())
    
    # Filter stop words (basic English stop words)
    stop_words = {
        "a", "an", "the", "this", "that", "these", "those",
        "is", "are", "was", "were", "be", "been", "being",
        "and", "or", "but", "if", "then", "else", "when",
        "to", "of", "in", "on", "at", "by", "for", "with",
        "about", "against", "between", "into", "through",
        "during", "before", "after", "above", "below",
        "from", "up", "down", "out", "off", "over", "under",
        "again", "further", "then", "once", "here", "there",
        "all", "any", "both", "each", "few", "more", "most",
        "other", "some", "such", "no", "nor", "not", "only",
        "own", "same", "so", "than", "too", "very", "can",
        "will", "just", "should", "now"
    }
    
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Count frequency
    from collections import Counter
    word_counts = Counter(keywords)
    
    # Get the most common keywords
    top_keywords = [word for word, _ in word_counts.most_common(max_keywords)]
    
    return top_keywords

def clean_html(text: str) -> str:
    """
    Clean HTML tags from text.
    
    Args:
        text (str): Input text with HTML
        
    Returns:
        str: Cleaned text
    """
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    
    # Fix HTML entities
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&quot;", "\"", text)
    text = re.sub(r"&#39;", "'", text)
    
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()
    
    return text

def detect_language(text: str) -> str:
    """
    Detect the language of a text.
    This is a simple implementation using regular expressions.
    For production, consider using a language detection library.
    
    Args:
        text (str): Input text
        
    Returns:
        str: Detected language code (e.g., 'en', 'fr', 'es')
    """
    # Default to English
    if not text or len(text.strip()) < 10:
        return "en"
    
    # Very basic language detection based on common words
    text = text.lower()
    
    # Check for Spanish
    if re.search(r"\b(el|la|los|las|de|en|y|es|por|que|con|para|una|su)\b", text):
        return "es"
    
    # Check for French
    if re.search(r"\b(le|la|les|des|du|de|en|et|est|que|qui|pour|dans|un|une)\b", text):
        return "fr"
    
    # Check for German
    if re.search(r"\b(der|die|das|den|dem|ein|eine|zu|und|ist|für|mit|auf)\b", text):
        return "de"
    
    # Default to English
    return "en" 