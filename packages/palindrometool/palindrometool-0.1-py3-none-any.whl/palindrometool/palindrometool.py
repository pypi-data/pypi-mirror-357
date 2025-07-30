def palindrome(word):
    cleaned=''.join(word.lower().split())

    return cleaned==cleaned[::-1]

