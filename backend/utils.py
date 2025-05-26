import re

def process_prompts(prompt_list: list) -> list:
    """
    Processes a list of strings and extracts the content within the first pair of double quotes from each string.

    Args:
        prompt_list: A list of strings, where each string is expected to contain
                     content enclosed in double quotes (e.g., '1. "example prompt"').

    Returns:
        A list of strings, containing the extracted content from within the
        double quotes for each item in the input list.
    """
    prompts = [re.search(r'"(.*?)"', item).group(1) for item in prompt_list]
    return prompts
