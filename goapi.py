import os
import glob
from gophish import Gophish
from gophish.models import Campaign, Group, SMTP, Template


class CampaignManager:
    def __init__(self, api_url: str, api_key: str):
        self.client = Gophish(api_key, host=url, verify=False)
    
    def check_existence(client, resource_type, name):
        """
            Check if a resource with a given name exists on the Gophish server.
            
            param client: The Gophish client instance.
            param resource_type: The type of resource to check (e.g., 'groups', 'templates').
            param name: The name of the resource to check.
            return: The resource object if found, otherwise None.
        """
        try:
            resources = getattr(client, resource_type).list()
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

    def create_group(self, group_name, targets):
        """
        Create a new group on the Gophish server.

        :param client: The Gophish client instance.
        :param group_name: The name of the group to create.
        :param targets: A list of target dictionaries (e.g., {"email": "...", "first_name": "...", "last_name": "..."}).
        :return: The created group object.
        """
        new_group = Group(name=group_name, targets=targets)
        return self.client.groups.post(new_group)


    def group_csv(file_path):
        import csv
        """
        Parse a CSV file to extract target information.

        :param file_path: The path to the CSV file.
        :return: A list of target dictionaries with keys: email, first_name, last_name.
        """
        targets = []
        try:
            with open(file_path, mode="r") as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    targets.append({
                        "first_name": row.get("first_name", ""),
                        "last_name": row.get("last_name", ""),
                        "email": row.get("email"),
                        "position": row.get("position", "")
                    })
            return targets
        except Exception as e:
            print(f"Error parsing CSV file: {e}")
            return None

    def create_campaign(client, name, group_name, targets=None, csv_file=None, template_id=None, smtp_id=None, url=None):
        """
        Create a new campaign with options to create a group from targets or a CSV file.

        :param client: The Gophish client instance.
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
            group = check_group_exists(client, group_name)

            # Create the group if it doesn't exist
            if not group:
                if not targets and not csv_file:
                    raise ValueError(
                        f"Group '{group_name}' does not exist, and no targets or CSV file were provided to create it."
                    )
                
                # Parse targets from CSV if provided
                if csv_file:
                    targets = parse_csv(csv_file)
                    if not targets:
                        raise Exception(f"Failed to parse targets from CSV file '{csv_file}'.")

                # Create the group
                group = create_group(client, group_name, targets)
                if not group:
                    raise Exception(f"Failed to create group '{group_name}'.")

            # Create the campaign
            campaign = Campaign(
                name=name,
                groups=[Group(id=group.id)],
                template=Template(id=template_id),
                smtp=SMTP(id=smtp_id),
                url=url,
            )
            created_campaign = client.campaigns.post(campaign)
            return created_campaign
        except Exception as e:
            print(f"Error creating campaign: {e}")
            return None