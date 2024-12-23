import os
import glob
from gophish import Gophish
from gophish.models import Campaign, Group, SMTP, Template
import pandas as pd
import subprocess
import tempfile

class CampaignManager:
    def __init__(self, url: str, api_key: str):
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.client = Gophish(api_key, host=url, verify=False)
        self.url = url
        self.api_key = api_key
    
    def check_existence(self, resource_type, name):
        """
            Check if a resource with a given name exists on the Gophish server.
            
            param resource_type: The type of resource to check (e.g., 'groups', 'templates').
            param name: The name of the resource to check.
            return: The resource object if found, otherwise None.
        """
        try:
            resources = getattr(self.client, resource_type).list()
            for resource in resources:
                if resource.name == name:
                    return resource
            return None
        except Exception as e:
            print(f"Error checking existence of {resource_type}: {e}")
            return None

    def get_campaign_summary(self, campaign_id: int):
        try:
            campaign = self.client.campaigns.get(campaign_id=campaign_id)
            return {
                "id": campaign.id,
                "name": campaign.name,
                "status": campaign.status,
                "launch_date": campaign.launch_date,
                "results": campaign.results,
            }
        except Exception as e:
            print(f"Error fetching campaign summary: {e}")
            return None

    def get_campaigns_summaries(self):
        try:
            campaigns = self.client.campaigns.list()
            return [
                {
                    "id": campaign.id,
                    "name": campaign.name,
                    "status": campaign.status,
                    "launch_date": campaign.launch_date,
                }
                for campaign in campaigns
            ]
        except Exception as e:
            print(f"Error fetching campaigns summaries: {e}")
            return None

    def create_group(self, group_name, file):
        """
        Create a new group on the Gophish server using the provided CSV file.

        :param group_name: The name of the group to create.
        :param file: Path to the CSV file containing the target information.
        :return: The created group object or None if creation fails.
        """
        df = pd.read_csv(file)

        # Check for required columns: email, first_name, last_name
        required_columns = ['First Name','Last Name','Email']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Missing required columns: {', '.join(missing_columns)}")
            return None

        # Create a list to hold the target data
        targets = []

        # Iterate over the DataFrame and prepare the target data
        for _, row in df.iterrows():
            email = row['Email'].strip()
            first_name = row['First Name'].strip()
            last_name = row['Last Name'].strip()

            # Handle 'position' safely
            position = row.get('Position', '')  # position is optional
            
            # If position is a float (NaN), convert to empty string
            if isinstance(position, float) and pd.isna(position):
                position = ''

            # Ensure position is a string (even if it's None or NaN)
            position = str(position).strip()

            # Skip rows without a valid email
            if not email:
                print(f"Skipping row with missing email: {first_name} {last_name}")
                continue

            # Create a target dictionary (position is optional)
            target = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email
            }
            if position:  # Only add position if it's not empty
                target['position'] = position

            # Add the target to the list
            targets.append(target)

        # Check if there are valid targets to create the group
        if targets:
            # Create the group using the Gophish Group model
            group = Group(name=group_name, targets=targets)

            # Send the group creation request to the Gophish server
            response = self.client.groups.post(group)
            print(f"Group created successfully with Name: {response.name}")
            # Return the created group object
            return response
        else:
            print("No valid targets to create a group.")
            return None


    def delete_all_templates(self):
        """
        Delete all templates from the Gophish server.

        :return: None
        """
        try:
            # Retrieve all templates using the correct method
            templates = self.client.templates.get()  # Correct method to get all templates

            if not templates:
                print("No templates found to delete.")
                return

            # Iterate over all templates and delete each one
            for template in templates:
                try:
                    # Delete the template
                    self.client.templates.delete(template.id)
                    print(f"Template '{template.name}' with ID {template.id} deleted successfully.")
                except Exception as e:
                    print(f"Error deleting template '{template.name}': {e}")
        except Exception as e:
            print(f"Error fetching templates: {e}")

    import requests

    def _get_url(self):
        return self.url
    def _get_api(self):
        return self.api_key
    def create_template(self, html_source, directory=False):
        import json
        """
        Create a new template in Gophish using an HTML file or all HTML files from a directory using curl.

        :param html_source: The HTML file or directory containing HTML files.
        :param directory: If True, treats html_source as a directory and reads all HTML files in it.
        :return: None if creation fails, otherwise prints the success message.
        """
        try:
            gophish_url = self._get_url()  # Gophish API URL
            api_key = self._get_api()  # Gophish API Key
            
            # If directory is specified, read all HTML files from the directory
            if directory:
                if not os.path.isdir(html_source):
                    print(f"Provided path '{html_source}' is not a valid directory.")
                    return None

                # Collect all HTML files from the directory
                html_files = [f for f in os.listdir(html_source) if f.endswith('.html')]
                if not html_files:
                    print(f"No HTML files found in directory: {html_source}")
                    return None

                # Create templates for each HTML file in the directory
                for html_file in html_files:
                    html_path = os.path.join(html_source, html_file)
                    with open(html_path, 'r') as file:
                        html_body = file.read()
                    
                    # Prepare the payload
                    payload = {
                        "name": html_file[9:-11],
                        "subject": html_file[9:-11],
                        "text": "",
                        "html": html_body
                    }

                    # Convert the payload to JSON
                    payload_json = json.dumps(payload)
                    with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as temp_file:
                        temp_file.write(payload_json)
                        temp_filename = temp_file.name
                    curl_command = [
                    "curl", "-X", "POST",
                    "-H", "Content-Type: application/json",
                    "-d", "@{temp_filename}",
                    "-k" ,f"{gophish_url}api/templates/?api_key={api_key}"
                    ]
                    
                    # Execute the curl command
                    result = subprocess.run(curl_command, capture_output=True, text=True)

                    # Check the result
                    if result.returncode == 0:
                        print(f"Template '{html_file}' created successfully.")
                    else:
                        print(f"Error creating template: {result.stderr}")
            else:
                # Read HTML content from a single file if directory is not specified
                if not os.path.isfile(html_source):
                    print(f"Provided path '{html_source}' is not a valid file.")
                    return None

                with open(html_source, 'r') as file:
                    html_body = file.read()

                # Prepare the payload
                payload = {
                    "name": os.path.basename(html_source)[9:-11],
                    "subject": os.path.basename(html_source)[9:-11],
                    "text": "",
                    "html": html_body
                }

                # Convert the payload to JSON
                payload_json = json.dumps(payload)
                with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as temp_file:
                    temp_file.write(payload_json)
                    temp_filename = temp_file.name
                curl_command = [
                "curl", "-X", "POST",
                "-H", "Content-Type: application/json",
                "-d", "@{temp_filename}",
                "-k" ,f"{gophish_url}api/templates/?api_key={api_key}"
                ]
                # Execute the curl command
                result = subprocess.run(curl_command, capture_output=True, text=True)
                # Check the result
                if result.returncode == 0:
                    print(f"Template '{os.path.basename(html_source)}' created successfully.")
                else:
                    print(f"Error creating template: {result.stderr}")

        except Exception as e:
            print(f"Error creating template: {e}")

    def create_templatesksksks(self, html_source, directory=False):
        """
        Create a new template in Gophish using an HTML file or all HTML files from a directory.

        :param html_source: The HTML file or directory containing HTML files.
        :param directory: If True, treats html_source as a directory and reads all HTML files in it.
        :return: The created template object or None if creation fails.
        """
        try:
            # If directory is specified, read all HTML files from the directory
            if directory:
                if not os.path.isdir(html_source):
                    print(f"Provided path '{html_source}' is not a valid directory.")
                    return None
                
                # Collect all HTML files from the directory
                html_files = [f for f in os.listdir(html_source) if f.endswith('.html')]
                if not html_files:
                    print(f"No HTML files found in directory: {html_source}")
                    return None
                
                # Create templates for each HTML file in the directory
                created_templates = []
                for html_file in html_files:
                    html_path = os.path.join(html_source, html_file)
                    with open(html_path, 'r') as file:
                        html_body = file.read()
                    
                    # Create a Template instance
                    new_template = Template(name=f"{html_file[:-5]}", html=html_body, plain_text="")
                    
                    # Post the template to Gophish
                    response = self.client.templates.post(new_template)
                    print(f"Template created successfully with ID: {response.id}")
                    created_templates.append(response)
                
                return created_templates
            else:
                # Read HTML content from a single file if directory is not specified
                if not os.path.isfile(html_source):
                    print(f"Provided path '{html_source}' is not a valid file.")
                    return None
                
                with open(html_source, 'r') as file:
                    html_body = file.read()

                # Create a Template instance
                new_template = Template(name=f"{html_file[:-5]}", html=html_body, plain_text="",subject=f"{html_file[:-5]}")

                # Create template on Gophish
                response = self.client.templates.post(new_template)
                print(f"Template created successfully with ID: {response.id}")
                return response

        except Exception as e:
            print(f"Error creating template: {e}")
            return None

    def create_campaign(self, name, group_name, targets=None, csv_file=None, template_id=None, smtp_id=None, url=None):
        """
        Create a new campaign with options to create a group from targets or a CSV file.

        :param name: The name of the campaign.
        :param group_name: The name of the group to associate with the campaign.
        :param targets: A list of target dictionaries for the group (used only if a group needs to be created).
        :param csv_file: Path to a CSV file containing target information (used only if a group needs to be created).
        :param template_id: The ID of the template to use for the campaign.
        :param smtp_id: The ID of the SMTP profile to use.
        :param url: The URL for the phishing landing page.
        :return: The created campaign object or None if creation fails.
        """
        try:
            # Check if the group exists
            group = self.check_existence("groups", group_name)

            # Create the group if it doesn't exist
            if not group:
                if not targets and not csv_file:
                    raise ValueError(
                        f"Group '{group_name}' does not exist, and no targets or CSV file were provided to create it."
                    )
                
                # Parse targets from CSV if provided
                if csv_file:
                    targets = self.create_group(group_name, csv_file)
                    if not targets:
                        raise Exception(f"Failed to create group '{group_name}'.")

                # Create the group
                group = self.create_group(group_name, targets)
                if not group:
                    raise Exception(f"Failed to create group '{group_name}'.")

            # Create the campaign
            campaign = Campaign(
                name=name,
                groups=[Group(id=group['id'])],
                template=Template(id=template_id),
                smtp=SMTP(id=smtp_id),
                url=url,
            )
            created_campaign = self.client.campaigns.post(campaign)
            return created_campaign
        except Exception as e:
            print(f"Error creating campaign: {e}")
            return None
