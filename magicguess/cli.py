from magicguess.core import MasterGuess
from magicguess.utils import validate_date, validate_email 
from magicguess.combinators import generate_wordlist, generate_pinlist, dedupe
from magicguess.io_handlers import save_wordlist, save_pinlist

def ask_yes_no(prompt):
    answer = input(f"{prompt} (y/yes n/no): ").strip().lower()
    if answer in ["y", "yes"]:
        return True
    return False

def ask_date(prompt):
    while True:
        date = input(prompt).strip()
        if date == "":
            return ""
        if validate_date(date):
            return date
        print("Invalid date format. Expected DD/MM/YYYY.")

def main_cli():
    mg = create_masterguess()

    # default values in case future features depend on them
    mg.generate_wordlist = False
    mg.generate_pinlist = False

    print("Do you want to create a wordlist, a PIN list, or both?")

    valid_choices = ["wordlist", "pinlist", "both", "exit"]
    choice = ""

    while choice not in valid_choices:
        choice = input("Enter 'wordlist', 'pinlist', 'both', or 'exit': ").strip().lower()

    if choice == "exit":
        print("Exiting MagicGuess.")
        return

    if choice == "wordlist":
        mg.generate_wordlist = True
        mg.generate_pinlist = False

    elif choice == "pinlist":
        mg.generate_wordlist = False
        mg.generate_pinlist = True

    elif choice == "both":
        mg.generate_wordlist = True
        mg.generate_pinlist = True

    # Now call the processing functions
    if mg.generate_wordlist:
        mg.wordlist = generate_wordlist(mg)
        save_wordlist(mg)

    if mg.generate_pinlist:
        mg.pinlist = generate_pinlist(mg)
        save_pinlist(mg)

    # final cleanup: combine and dedupe
    mg.final_output = dedupe(mg)

    print("\n[+] MagicGuess completed!")


def create_masterguess():
    print("\n=== MagicGuess Target Profile ===\n")

    # ---- Basic Information ----
    name = input("Target name: ").strip()
    birth = ask_date("Target birth date (DD/MM/YYYY): ")

    relationships = []
    if ask_yes_no("Are known romantic relationships?"):
        while True:
            r_name = input("Name: ").strip()
            r_birth = ask_date("Birth date (DD/MM/YYYY): ")
            r_nick = input("Nickname (optional): ").strip()

            relationships.append({
                "name": r_name,
                "birth": r_birth,
                "nickname": r_nick
            })

            if not ask_yes_no("Add another relationship?"):
                break

    # ---- Children ----
    children = []
    if ask_yes_no("Does the target have children?"):
        while True:
            c_name = input("Name: ").strip()
            c_birth = ask_date("Birth date (DD/MM/YYYY): ")
            c_nick = input("Nickname (optional): ").strip()

            children.append({
                "name": c_name,
                "birth": c_birth,
                "nickname": c_nick
            })

            if not ask_yes_no("Add another child?"):
                break

    # ---- Pets ----
    pets = []
    if ask_yes_no("Does the target have pets?"):
        while True:
            p_name = input("Name: ").strip()
            p_birth = ask_date("Birth date (DD/MM/YYYY): ")

            pets.append({
                "name": p_name,
                "birth": p_birth
            })

            if not ask_yes_no("Add another pet?"):
                break

    # ---- Important Dates ----
    important_dates = []
    if ask_yes_no("Are there important dates for the target?"):
        raw = input("Enter them comma-separated (DD/MM/YYYY): ").strip()
        if raw:
            dates = [d.strip() for d in raw.split(",")]
            for d in dates:
                if validate_date(d):
                    important_dates.append(d)
                else:
                    print(f"Warning: {d} ignored (invalid format).")

    # ---- Important Words ----
    important_words = []
    if ask_yes_no("Are there important words for the target?"):
        raw = input("Enter them comma-separated: ").strip()
        if raw:
            important_words = [w.strip() for w in raw.split(",")]

    # ---- Emails Known -----
    emails = []
    if ask_yes_no("Are there known email addresses for the target?"):
        raw = input("Enter them comma-separated: ").strip()
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
