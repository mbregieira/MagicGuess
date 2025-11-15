from magicguess.core import MasterGuess, Relationship, Child, Pet, Email
from magicguess.utils import validate_date, validate_email
from magicguess.combinators import generate_wordlist  # generate_pinlist (future)
from magicguess.io_handlers import save_wordlist, save_pinlist


def ask_yes_no(prompt):
    answer = input(f"{prompt} (y/yes n/no): ").strip().lower()
    return answer in ["y", "yes"]


def ask_date(prompt):
    while True:
        d = input(prompt).strip()
        if d == "":
            return None
        if validate_date(d):
            day, month, year = map(int, d.split("/"))
            from datetime import date as dt
            return dt(year, month, day)
        print("Invalid date format. Expected DD/MM/YYYY.")


# -------- PERSON COLLECTORS -------- #

def collect_relationships():
    rels = []
    while True:
        name = input("Relationship name: ").strip()
        if not name:
            print("Name cannot be empty.")
            continue

        birth = ask_date("Relationship birth date (DD/MM/YYYY, optional): ")
        nickname = input("Relationship nickname (optional): ").strip()

        # Relationship object
        rels.append(
            Relationship(
                first_name=name,
                last_name=None,
                nickname=nickname or None,
                birthdate=birth
            )
        )

        if not ask_yes_no("Add another relationship?"):
            break
    return rels


def collect_children():
    children = []
    while True:
        name = input("Child name: ").strip()
        if not name:
            print("Name cannot be empty.")
            continue

        birth = ask_date("Child birth date (DD/MM/YYYY, optional): ")
        nickname = input("Child nickname (optional): ").strip()

        children.append(
            Child(
                first_name=name,
                last_name=None,
                nickname=nickname or None,
                birthdate=birth
            )
        )

        if not ask_yes_no("Add another child?"):
            break
    return children


def collect_pets():
    pets = []
    while True:
        name = input("Pet name: ").strip()
        if not name:
            print("Pet name cannot be empty.")
            continue

        birth = ask_date("Pet birth date (DD/MM/YYYY, optional): ")

        pets.append(
            Pet(
                name=name,
                birthdate=birth
            )
        )

        if not ask_yes_no("Add another pet?"):
            break
    return pets


def collect_emails():
    emails = []
    raw = input("Enter comma-separated emails: ").strip()

    if not raw:
        return emails

    for e in [x.strip() for x in raw.split(",")]:
        if validate_email(e):
            emails.append(Email(e))
        else:
            print(f"Warning: {e} ignored (invalid email).")
    return emails


# -------- MASTER CREATION -------- #

def create_masterguess():
    print("\n=== MagicGuess Target Profile ===\n")

    name = input("Target full name: ").strip()
    birth = ask_date("Target birth date (DD/MM/YYYY, optional): ")

    relationships = collect_relationships() if ask_yes_no("Known romantic relationships?") else []
    children = collect_children() if ask_yes_no("Does the target have children?") else []
    pets = collect_pets() if ask_yes_no("Does the target have pets?") else []

    # Important dates
    important_dates = []
    if ask_yes_no("Any important dates for the target?"):
        raw = input("Enter comma-separated dates (DD/MM/YYYY): ").strip()
        if raw:
            for d in [x.strip() for x in raw.split(",")]:
                if validate_date(d):
                    day, month, year = map(int, d.split("/"))
                    from datetime import date as dt
                    important_dates.append(dt(year, month, day))
                else:
                    print(f"Warning: {d} ignored (invalid date).")

    # Important words
    important_words = []
    if ask_yes_no("Any important keywords for the target?"):
        raw = input("Enter comma-separated keywords: ").strip()
        if raw:
            important_words = [w.strip() for w in raw.split(",") if w.strip()]

    # Emails
    emails = []
    if ask_yes_no("Any known email addresses?"):
        emails = collect_emails()

    print("\n[+] Target profile completed!\n")

    return MasterGuess(
        name=name,
        birth=birth,
        relationships=relationships,
        children=children,
        pets=pets,
        important_dates=important_dates,
        keywords=important_words,
        emails=emails
    )


# -------- MAIN CLI -------- #

def main_cli():
    mg = create_masterguess()

    print("Do you want to create a wordlist, a PIN list, or both?")
    valid = ["wordlist", "pinlist", "both", "exit"]
    choice = ""

    while choice not in valid:
        choice = input("Enter 'wordlist', 'pinlist', 'both', or 'exit': ").strip().lower()

    if choice == "exit":
        print("Exiting MagicGuess.")
        return

    # WORDLIST
    if choice in ["wordlist", "both"]:
        mg.leet_enabled = ask_yes_no("Enable leet transformations?")
        mg.wordlist = generate_wordlist(mg)
        save_wordlist(mg)

    # PIN LIST *(future implementation)*
    if choice in ["pinlist", "both"]:
        print("[!] PIN generation not implemented yet in this version.")
        # mg.pinlist = generate_pinlist(mg)
        # save_pinlist(mg)

    print("\n[+] MagicGuess completed!")
