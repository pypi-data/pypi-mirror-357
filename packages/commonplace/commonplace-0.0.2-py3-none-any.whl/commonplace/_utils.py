import re
from datetime import datetime


def truncate(text: str, max_length=200) -> str:
    if len(text) > max_length:
        return text[:max_length] + f" (+{len(text) - max_length} more)"
    return text


def slugify(text: str) -> str:
    text = text.lower()
    text = text.replace(" ", "-")
    slug = re.sub("[^a-z0-9-]", "", text)
    return slug
