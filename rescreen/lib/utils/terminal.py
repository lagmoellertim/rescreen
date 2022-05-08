def prompt(question: str) -> bool:
    yes_options = ["y", "yes"]
    no_options = ["n", "no"]

    while (val := input(f"{question.strip()} ").lower()) not in [*yes_options, *no_options]:
        print("Invalid Option, choose yes (y) or no (n)")

    return val in yes_options
