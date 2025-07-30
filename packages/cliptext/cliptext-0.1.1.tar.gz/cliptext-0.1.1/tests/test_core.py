from cliptext import clip_text

text = "This is a long description. It has many sentences! But not all will fit in a short box?"

# Try a short limit to test clipping
short = clip_text(text, limit=200)
print("Clipped Text:", short)
