# io_handlers.py

# Input/output handlers for MagicGuess 

def save_wordlist(wordlist, filename="AwesomeWordlist.txt"):
    """
    Saves the generated wordlist to a file.
    """
    with open(filename, "w", encoding="utf-8") as f:
        for w in wordlist:
            f.write(w + "\n")

    print(f"[+] Wordlist saved to {filename}")


def save_pinlist(pinlist, filename="AwesomePINlist.txt"):
    """
    Saves the generated PIN list to a file.
    """
    with open(filename, "w", encoding="utf-8") as f:
        for p in pinlist:
            f.write(p + "\n")

    print(f"[+] PIN list saved to {filename}")