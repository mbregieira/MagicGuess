# io_handlers.py
# Funções de load/save para wordlist e pinlist

def save_wordlist(wordlist, filename="AwesomeWordlist.txt"):
    """Grava a wordlist num ficheiro."""
    with open(filename, "w", encoding="utf-8") as f:
        for w in wordlist:
            f.write(w + "\n")

    print(f"[+] Wordlist saved to {filename}")


def save_pinlist(pinlist, filename="AwesomePINlist.txt"):
    """Grava a PIN list num ficheiro."""
    with open(filename, "w", encoding="utf-8") as f:
        for p in pinlist:
            f.write(p + "\n")

    print(f"[+] PIN list saved to {filename}")