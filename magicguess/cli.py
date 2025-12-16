# cli.py
from magicguess.core import MasterGuess
from magicguess.utils import validate_date, validate_email
from magicguess.generators import generate_wordlist
from magicguess.io_handlers import save_wordlist

from datetime import date as dt

def ask_yes_no(prompt):
    """
    Ask a yes/no question via input() and return True for yes and False for no.
    """
    answer = input(f"{prompt} (y/yes n/no): ").strip().lower()
    return answer in ["y", "yes"]

def ask_date(prompt):
    """
    Ask for a date input in DD/MM/YYYY format. Returns a date object or None.
    """
    while True:
        date_str = input(prompt).strip()
        if date_str == "":
            return None
        if validate_date(date_str):
            day, month, year = map(int, date_str.split("/"))
            return dt(year, month, day)
        print("Invalid date format. Expected DD/MM/YYYY.")

def collect_person(prompt):
    persons = []
    while True:
        name = input(f"{prompt} Name: ").strip()
        birth = ask_date(f"{prompt} Birth date (DD/MM/YYYY, optional): ")
        nickname = input(f"{prompt} Nickname (optional): ").strip()
        person_obj = {"name": name, "birth": birth, "nickname": nickname}
        persons.append(person_obj)
        if not ask_yes_no(f"Add another {prompt.lower()}?"):
            break
    return persons

def create_masterguess():
    print("\n=== MagicGuess Target Profile ===\n")

    name = input("Target name: ").strip()
    birth = ask_date("Target birth date (DD/MM/YYYY, optional): ")

    relationships = collect_person("Relationship") if ask_yes_no("Known romantic relationships?") else []
    children = collect_person("Child") if ask_yes_no("Does the target have children?") else []
    pets = collect_person("Pet") if ask_yes_no("Does the target have pets?") else []

    # Important dates
    important_dates = []
    if ask_yes_no("Any important dates for the target?"):
        raw = input("Enter comma-separated (DD/MM/YYYY): ").strip()
        if raw:
            for d in [x.strip() for x in raw.split(",")]:
                if validate_date(d):
                    day, month, year = map(int, d.split("/"))
                    important_dates.append(dt(year, month, day))
                else:
                    print(f"Invalid date format: {d}")

    # Important words
    important_words = []
    if ask_yes_no("Any important words for the target?"):
        raw = input("Enter comma-separated: ").strip()
        if raw:
            important_words = [w.strip() for w in raw.split(",")]

    # Emails
    emails = []
    if ask_yes_no("Any known email addresses?"):
        raw = input("Enter comma-separated emails: ").strip()
        if raw:
            for e in [em.strip() for em in raw.split(",")]:
                if validate_email(e):
                    emails.append(e)
                else:
                    print(f"Warning: {e} ignored (invalid email).")

    print("\n[+] Profile completed!\n")

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

def main_cli():
    mg = create_masterguess()

    # Choose generation
    print("Do you want to create a wordlist, a PIN list, or both?")
    choice = ""
    valid_choices = ["wordlist", "pinlist", "both", "exit"]
    while choice not in valid_choices:
        choice = input("Enter 'wordlist', 'pinlist', 'both', or 'exit': ").strip().lower()

    if choice == "exit":
        print("Exiting MagicGuess.")
        return

    mg.generate_wordlist = choice in ["wordlist", "both"]
    mg.generate_pinlist = choice in ["pinlist", "both"]

    if mg.generate_wordlist:
        mg.leet_enabled = ask_yes_no("Enable leet transformations?")
        mg.wordlist, mg.wordlist_count = generate_wordlist(mg)
        filename = input("[+] Save wordlist to filename (default: AwesomeWordlist.txt): ").strip()
        if not filename:
            filename = "AwesomeWordlist.txt"
        save_wordlist(mg.wordlist, filename)

    print(f"[+] Wordlist generated with {mg.wordlist_count} entries.")

    print("\n[+] MagicGuess completed!")
