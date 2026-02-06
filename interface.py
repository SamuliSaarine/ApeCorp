def ask_user_choice(options: list[str]) -> int:
    for i, option in enumerate(options):
        print(f"{i})\n{option}\n")
    choice = input("Choose an option: ")
    return int(choice)