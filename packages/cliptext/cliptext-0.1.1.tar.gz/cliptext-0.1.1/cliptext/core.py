import re

def clip_text(text: str, limit: int = 130) -> str:
    """
    Smartly clip text at sentence boundaries within a character limit.
    If no sentence fits, clip the first sentence by words.
    If even one word can't fit, allow mid-word clipping.
    Adds '...' if clipped.
    """
    sentences = re.split(r'(?<=[.!?]) +', text)
    result = ''

    for sentence in sentences:
        if len(result) + len(sentence) <= limit:
            result += sentence + ' '
        else:
            break

    result = result.strip()

    # Case: No full sentence fit
    if not result:
        words = text.strip().split()
        clipped = ''
        for word in words:
            # Check if word fits
            if len(clipped) + len(word) + (1 if clipped else 0) <= limit:
                clipped += (' ' if clipped else '') + word
            else:
                break

        # Case: even first word didn't fit
        if not clipped:
            return text[:limit].rstrip() + '...'

        return clipped + '...'

    # Case: sentences fit normally
    return result + ('...' if len(result) < len(text.strip()) else '')
