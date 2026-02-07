from typing import TypeAlias

InterfaceType: TypeAlias = str

def ask_user_choice(options: list[InterfaceType]) -> int:
    for i, option in enumerate(options):
        print(f"{i})\n{option}\n")
    choice = input("Choose an option: ")
    return int(choice)