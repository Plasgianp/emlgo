import os
from email import policy
from email.parser import BytesParser
from bs4 import BeautifulSoup
import re

def read_values_from_file(file_path):
    expanded_path = os.path.expanduser(file_path)
    #print(f"Expanded Path: {expanded_path}")  # Debugging

    # Use expanded_path instead of file_path
    values = []
    with open(expanded_path, 'r') as file:
        for line in file:
            values.append(line.strip())
    return values

nomi = read_values_from_file('~/.bin/Liste/nomi_clean.txt')
cognomi = read_values_from_file('~/.bin/Liste/cognomi_clean.txt')

def eml_to_html(eml_file):
    with open(eml_file, 'rb') as file:
        msg = BytesParser(policy=policy.default).parse(file)
    
    html_content = None
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            html_content = part.get_payload(decode=True)
            break
    
    if html_content:
        return html_content.decode('utf-8', errors='replace')
    else:
        plain_text_part = msg.get_body(preferencelist=('plain',))
        if plain_text_part:
            return f"<html><body>{plain_text_part.get_content()}</body></html>"
        else:
            return "<html><body>No content found</body></html>"

def add_href_to_anchor_tags(html_content, new_href): # no support conditional
    soup = BeautifulSoup(html_content, 'html.parser')
    anchor_tags = soup.find_all('a')
    for tag in anchor_tags:
        tag['href'] = new_href
    return str(soup)

def add_href_to_file(file_path, new_href):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    modified_html = add_href_to_anchor_tags(html_content, new_href)
    modified_html = modified_html.replace('</html>', '{{.Tracker}}\n</html>')
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(modified_html)

def anonymizer(html_content,nomi,cognomi): # Still have to think (maybe list of all name possible?) Performance problem???
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    modified_html = re.sub(email_pattern, '{{.Email}}', html_content)
    """for nome in nomi:
        if nome in modified_html:
            modified_html = modified_html.replace(nome,'{{.FirstName}}')
    for cognome in cognomi:
        if cognome in modified_html:
            modified_html = modified_html.replace(cognome,'{{.LastName}}')"""
    
    return modified_html

def gophishing_everything(directory_path):
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.eml'):
                eml_file = os.path.join(root, file)
                html_content = eml_to_html(eml_file)
                modified_html = anonymizer(html_content,nomi,cognomi)
                modified_html_with_href = add_href_to_anchor_tags(modified_html, '{{.URL}}')
                modified_html_with_href = modified_html_with_href.replace('</html>', '{{.Tracker}}\n</html>')
                modified_html_no_script = remove_scripts(modified_html_with_href)

                output_file = os.path.splitext(eml_file)[0] + ".html"
                with open(output_file, 'w') as output:
                    output.write(modified_html_no_script)

def remove_scripts_from_directory(directory_path):
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.html') or file.endswith('.htm'):
                html_file = os.path.join(root, file)
                remove_scripts_from_file(html_file)


def remove_scripts(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove all script tags
    for script in soup(['script']):
        script.extract()
    return str(soup)

def remove_scripts_from_file(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove all script tags
    for script in soup(['script']):
        script.extract()

    # Write the modified HTML content back to the file
    with open(html_file, 'w', encoding='utf-8') as file:
        file.write(str(soup))
