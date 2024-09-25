def remove_duplicates(input_file, output_file):
    try:
        # Open the input file and read all names into a list
        with open(input_file, 'r') as file:
            names = file.readlines()

        # Remove duplicates by converting the list to a set and strip whitespace/newlines
        unique_names = set(name.strip() for name in names)

        # Write the unique names back to the output file
        with open(output_file, 'w') as file:
            for name in sorted(unique_names):  # Sort the names if needed
                file.write(name + '\n')

        print(f"Duplicates removed. Unique names have been written to {output_file}.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
input_file = 'cognomi.txt'  # Your input file with names
output_file = 'cognomi_clean.txt'  # Output file for unique names
remove_duplicates(input_file, output_file)