import re

def strip_formatting(text: str) -> str:
    """
    Strip formatting from a message;
    *bold* -> bold
    _italic_ -> italic
    ~strikethrough~ -> strikethrough
    !1 red! -> red
    !2 green! -> green
    !3 blue! -> blue
    !4 yellow! -> yellow
    !5 cyan! -> cyan
    !6 magenta! -> magenta
    """
    bold_pattern = r'\*([^*]+)\*'
    italic_pattern = r'_([^_]+)_'
    strikethrough_pattern = r'~([^~]+)~'
    color_pattern = r'!([1-6]) ([^!]+)!(.*)'

    text = re.sub(bold_pattern, r'\1', text)
    text = re.sub(italic_pattern, r'\1', text)
    text = re.sub(strikethrough_pattern, r'\1', text)
    text = re.sub(color_pattern, r'\2', text)

    return text

