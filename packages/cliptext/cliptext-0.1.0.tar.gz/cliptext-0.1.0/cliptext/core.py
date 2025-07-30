import re

def clip_text(text: str, limit: int) -> str:
    """
    Smartly clip text at sentence boundaries within a character limit.
    Adds '...' if text is clipped.

    Args:
        text (str): The input text to clip.
        limit (int): The maximum number of characters allowed.

    Returns:
        str: A clipped version of the text ending at a sentence boundary,
             followed by '...' if the text was clipped.
    """

    # Split the text on any space that comes after a punctuation mark (., !, ?)
    # Lookbehind ensures we split at sentence endings only
    sentences = re.split(r'(?<=[.!?]) +', text)

    result = ''
    for sentence in sentences:
        # Check if adding the sentence keeps us within the character limit
        if len(result) + len(sentence) <= limit:
            result += sentence + ' '
        else:
            break

    result = result.strip()

    # If the clipped result is shorter than the original, add ellipsis
    return result + ('...' if len(result) < len(text.strip()) else '')
