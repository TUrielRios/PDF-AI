import hashlib

# Simple in-memory caches
pdf_cache = {}
prompt_cache = {}

def generate_text_hash(prompt_str):
    """Create a hash of the prompt string for caching"""
    return hashlib.md5(prompt_str.encode('utf-8')).hexdigest()

def get_from_cache(cache, key):
    """Get an item from a cache if it exists"""
    return cache.get(key)

def add_to_cache(cache, key, value):
    """Add an item to a cache"""
    cache[key] = value
    return value

def generate_summary_cache_key(file_hash, page_num):
    """Generate a cache key for page summaries"""
    return f"{file_hash}page{page_num}"

