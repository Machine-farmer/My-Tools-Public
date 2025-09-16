from itertools import product
import random

def generate_numbers():
    num_digits = int(input("Enter number of digits: "))
    excluded = input("Enter digit to exclude (leave blank if none): ").strip()
    exclusion_type = None
    excluded_positions = []

    if excluded:
        exclusion_type = input("Exclude fully (f) or at specific positions (p)? [f/p]: ").lower()
        if exclusion_type == "p":
            excluded_positions = input(f"Enter positions (0–{num_digits-1}) separated by commas: ")
            excluded_positions = [int(pos.strip()) for pos in excluded_positions.split(",")]

    base_name = input("Enter base filename (default: numbers): ").strip()
    if not base_name:
        base_name = "numbers"

    # Ask about formatting (leading zeros vs plain int)
    print("\nChoose number format:")
    print("1. Fixed length with leading zeros")
    print("2. Plain integers (no leading zeros)")
    format_choice = input("Enter 1 or 2: ").strip()

    # Ask about sorting
    print("\nChoose sorting option:")
    print("1. Sorted ascending")
    print("2. Reverse sorted")
    print("3. Random order")
    print("4. All of the above")
    sort_choice = input("Enter 1, 2, 3, or 4: ").strip()

    results = []

    # Generate all numbers
    for digits in product("0123456789", repeat=num_digits):
        number = "".join(digits)

        if excluded:
            if exclusion_type == "f" and excluded in number:
                continue
            elif exclusion_type == "p" and any(number[pos] == excluded for pos in excluded_positions):
                continue

        if format_choice == "2":  # convert to plain integer
            results.append(str(int(number)))
        else:  # keep fixed-length padded
            results.append(number)

    # --- Save files based on sort choice ---
    if sort_choice in ["1", "4"]:
        sorted_file = f"{base_name}_sorted.txt"
        with open(sorted_file, "w", newline="\n", encoding="utf-8") as f:
            f.write("\n".join(sorted(results, key=lambda x: int(x))) + "\n")
        print(f"   → {sorted_file} (sorted ascending)")

    if sort_choice in ["2", "4"]:
        reverse_file = f"{base_name}_reverse.txt"
        with open(reverse_file, "w", newline="\n", encoding="utf-8") as f:
            f.write("\n".join(sorted(results, key=lambda x: int(x), reverse=True)) + "\n")
        print(f"   → {reverse_file} (reverse sorted)")

    if sort_choice in ["3", "4"]:
        random_file = f"{base_name}_random.txt"
        shuffled = results[:]  # copy before shuffle
        random.shuffle(shuffled)
        with open(random_file, "w", newline="\n", encoding="utf-8") as f:
            f.write("\n".join(shuffled) + "\n")
        print(f"   → {random_file} (random order)")

    print(f"\n✅ Generated {len(results)} numbers")


if __name__ == "__main__":
    generate_numbers()
