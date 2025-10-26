import re #regular expressions 

def clean_markdown(text: str) -> str:
    """
    Remove Markdown symbols like **, *, #, etc. 
    and format lists nicely for terminal/PDF output.
    """
    text = re.sub(r"#+\s*", "", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()