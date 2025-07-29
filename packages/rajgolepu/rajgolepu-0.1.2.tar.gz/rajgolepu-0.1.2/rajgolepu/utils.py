import time
from functools import wraps

def format_title_case(text: str) -> str:
    return text.title()

def reverse_string(text: str) -> str:
    return text[::-1]

def count_vowels(text: str) -> int:
    return sum(1 for char in text.lower() if char in "aeiou")

def ascii_art_banner(text: str) -> str:
    return f"""
     ___       _       _                 
    | _ \_ _ _(_)___ __| |_  ___ _ _ ___  
    |  _/ '_| '_/ -_|_-< ' \/ -_) '_/ -_) 
    |_| |_| |_| \___/__/_||_\___|_| \___| 
         :: {text.upper()} ::
"""

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"⏱️ Function '{func.__name__}' executed in {end - start:.4f}s")
        return result
    return wrapper

def help():
    print("🛠️ Available Functions in rajgolepu:")
    print("- info()             → Display developer profile")
    print("- format_title_case  → Convert a string to Title Case")
    print("- reverse_string     → Reverse the input string")
    print("- count_vowels       → Count vowels in a string")
    print("- timer              → Time any function (decorator)")
    print("- ascii_art_banner   → Show ASCII art for text")
    print("- help()             → Show this help menu")
