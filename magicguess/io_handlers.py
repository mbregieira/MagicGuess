# escrever ficheiro, formatos (txt, csv)

def save_wordlist(mg):
    filename = "AwesomeWordlist.txt"

    with open(filename, "w", encoding="utf-8") as f:
        for w in mg.wordlist:
            f.write(w + "\n")

    print(f"[+] Wordlist save in {filename}")
    input("Enter to continue...")

def save_pinlist(mg):
    filename = "AwesomePINlist.txt"

    with open(filename, "w", encoding="utf-8") as f:
        for p in mg.pinlist:
            f.write(p + "\n")

    print(f"[+] PIN list saved in {filename}")
    input("Enter to continue...")