from magicguess.core import MasterGuess
from magicguess.utils import validate_date, validate_email
from magicguess.combinators import generate_wordlist, generate_pinlist
from magicguess.generators import dedupe
from magicguess.io_handlers import save_wordlist, save_pinlist

def ask_yes_no(prompt):
    answer = input(f"{prompt} (y/yes n/no): ").strip().lower()
    return answer in ["y", "yes"]

def ask_date(prompt):
    while True:
        date = input(prompt).strip()
        if date == "":
            return None
        if validate_date(date):
            day, month, year = map(int, date.split("/"))
            from datetime import date as dt
            return dt(year, month, day)
        print("Invalid date format. Expected DD/MM/YYYY.")

def collect_person(prompt):
    persons = []
    while True:
        name = input(f"{prompt} Name: ").strip()
        birth = ask_date(f"{prompt} Birth date (DD/MM/YYYY, optional): ")
        nickname = input(f"{prompt} Nickname (optional): ").strip()
        person = {"name": name, "birth": birth, "nickname": nickname}
        persons.append(person)
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
                dt_obj = ask_date(f"Validate {d}? (press Enter to accept or retype)")
                if dt_obj:
                    important_dates.append(dt_obj)

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

    # Generate wordlist
    if mg.generate_wordlist:
        mg.wordlist = generate_wordlist(mg)
        save_wordlist(mg)

    # Generate pinlist
    if mg.generate_pinlist:
        mg.pinlist = generate_pinlist(mg)
        save_pinlist(mg)

    # Combine and dedupe
    mg.final_output = dedupe(mg)

    print("\n[+] MagicGuess completed!")
