import re

def process_prompts(prompt_list: list) -> list:
    """
    Process list of prompts, remove numbers and quotes, return cleaned prompt list
    
    Args:
        prompt_list: List of prompts containing numbers and quotes
        
    Returns:
        list: List of cleaned prompts
    """
    pattern = r'\d+\.\s*"([^"]+)"'
    cleaned_prompts = []
    for text in prompt_list:
        matches = re.findall(pattern, text)
        cleaned_prompts.extend(matches)
    
    return cleaned_prompts
