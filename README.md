# EMLGO

This Python script processes `.eml` files, converting them to HTML format, and provides several options to modify HTML files in specified ways. It includes functionality to add or modify hyperlinks, anonymize email addresses, and remove script tags from HTML files.

## Prerequisites

- **Python 3**: Ensure that Python 3 is installed on your system.
- **argcomplete**: For command-line auto-completion.

To install `argcomplete`, run:
```bash 
pip3 install -r requirements.txt
```

# Usage
The script provides several command-line options to process .eml and HTML files in bulk or individually. You can specify these options to control its behavior.

## Arguments
| Option                        | Description                                                                           |
|-------------------------------|---------------------------------------------------------------------------------------|
| `--emls_to_htmls, -r`        | Converts all `.eml` files in a specified directory to HTML format.                   |
| `--modify_href, -u`          | Adds a custom `{{.URL}}` hyperlink in all HTML files in the specified directory.     |
| `--script_removal, -sr`      | Removes all `<script>` tags from HTML files in the specified directory or from a specific HTML file. |
| `--modify_email`              | Modifies email addresses in HTML files by anonymizing them.                          |
| `--directory, -d`            | Specifies the directory containing `.eml` or HTML files.                            |
| `--eml_file, -e`             | Converts a single `.eml` file to HTML format.                                       |
| `--html_file, -f`            | Adds `{{.URL}}` hyperlink in a single HTML file.                                    |
| `--go, -a`                   | Combines `--eml_file`, `--html_file`, and `--modify_email` for processing.          |
| `--goes, -all`               | Processes all files in a directory recursively with the same actions as `--go`.      |

### Examples
Convert All .eml Files in a Directory to HTML:

```bash
python3 script_name.py -r -d /path/to/eml_files
```
Add Hyperlink to All HTML Files in a Directory:

```bash
python3 script_name.py -u -d /path/to/html_files
```
Remove "script" Tags from a Specific HTML File:

```bash
python3 script_name.py -sr -f /path/to/file.html
```
Convert a Single .eml File to HTML and Modify the Result:

```bash
python3 script_name.py -a /path/to/file.eml
```
Run All Modifications on a Directory Recursively:

```bash
python3 script_name.py -all -d /path/to/files
```

## Dependencies

emlgolib: Ensure that the emlgolib library is in the same directory as the script.

# Notes
Use the -d or --directory option for processing multiple files in a folder.
You can also specify individual .eml or HTML files using -e or -f depending on the file type(eml or html).

# License
This script is free to use and modify.
