def codec(phrase: str):
    array = phrase.split(':', 1)
    if len(array) < 2:
        raise ValueError("Decoding error. Could not split '" + phrase + "' with a ':' ")
    return array
