import os
from notion_client import Client
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

class NotionIntegration:
    def __init__(self):
        """Initialize Notion client with token from environment"""
        self.token = os.getenv('NOTION_TOKEN')
        if not self.token or self.token == 'your_notion_integration_token_here':
            raise ValueError("Notion token not found in .env file. Please run 'python setup_env.py' and configure your token.")
        
        self.notion = Client(auth=self.token)
        
        # Get database IDs from environment variables
        self.database_id = os.getenv('NOTION_EXPERIMENTS_DB_ID')
        self.campaigns_db_id = os.getenv('NOTION_CAMPAIGNS_DB_ID')
        self.affiliates_db_id = os.getenv('NOTION_AFFILIATES_DB_ID')
        self.initiatives_db_id = os.getenv('NOTION_INITIATIVES_DB_ID')
        
        # Validate that database IDs are configured
        if not self.database_id or self.database_id == 'your_experiments_database_id_here':
            raise ValueError("NOTION_EXPERIMENTS_DB_ID not configured in .env file. Please run 'python setup_env.py' and configure your database IDs.")
        
        if not self.campaigns_db_id or self.campaigns_db_id == 'your_campaigns_database_id_here':
            st.warning("NOTION_CAMPAIGNS_DB_ID not configured. EPCVIP Campaigns dropdown will be disabled.")
            self.campaigns_db_id = None
            
        if not self.affiliates_db_id or self.affiliates_db_id == 'your_affiliates_database_id_here':
            st.warning("NOTION_AFFILIATES_DB_ID not configured. EPCVIP Affiliates dropdown will be disabled.")
            self.affiliates_db_id = None
            
        if not self.initiatives_db_id or self.initiatives_db_id == 'your_initiatives_database_id_here':
            st.warning("NOTION_INITIATIVES_DB_ID not configured. EPCVIP Initiatives dropdown will be disabled.")
            self.initiatives_db_id = None
    
    def get_database_schema(self):
        """Get the schema/properties of the Experiments database"""
        try:
            database = self.notion.databases.retrieve(self.database_id)
            return database['properties']
        except Exception as e:
            st.error(f"Error retrieving database schema: {e}")
            return None
    
    def get_dropdown_options(self, property_name):
        """Get existing options for a select/dropdown property"""
        try:
            schema = self.get_database_schema()
            if schema and property_name in schema:
                property_details = schema[property_name]
                if property_details['type'] == 'select':
                    return [option['name'] for option in property_details['select']['options']]
                elif property_details['type'] == 'status':
                    return [option['name'] for option in property_details['status']['options']]
            return []
        except Exception as e:
            st.error(f"Error getting dropdown options: {e}")
            return []
    
    def get_campaign_options(self):
        """Get available EPCVIP Campaign options from the related database"""
        try:
            if not self.campaigns_db_id:
                return []
                
            # Query the campaigns database
            response = self.notion.databases.query(self.campaigns_db_id)
            pages = response['results']
            
            campaigns = []
            for page in pages:
                # Get the title property (assuming it's the first title property)
                title_prop = None
                for prop_name, prop_details in page['properties'].items():
                    if prop_details['type'] == 'title':
                        title_prop = prop_details
                        break
                
                if title_prop and title_prop['title']:
                    page_title = title_prop['title'][0]['text']['content']
                    campaigns.append({
                        'name': page_title,
                        'id': page['id']
                    })
            
            return campaigns
        except Exception as e:
            st.error(f"Error getting campaign options: {e}")
            return []
    
    def get_affiliate_options(self):
        """Get available EPCVIP Affiliate options from the related database"""
        try:
            if not self.affiliates_db_id:
                return []
                
            # Query the affiliates database
            response = self.notion.databases.query(self.affiliates_db_id)
            pages = response['results']
            
            affiliates = []
            for page in pages:
                # Get the title property (assuming it's the first title property)
                title_prop = None
                for prop_name, prop_details in page['properties'].items():
                    if prop_details['type'] == 'title':
                        title_prop = prop_details
                        break
                
                if title_prop and title_prop['title']:
                    page_title = title_prop['title'][0]['text']['content']
                    affiliates.append({
                        'name': page_title,
                        'id': page['id']
                    })
            
            return affiliates
        except Exception as e:
            st.error(f"Error getting affiliate options: {e}")
            return []
    
    def get_initiative_options(self):
        """Get available Initiative options from the related database"""
        try:
            if not self.initiatives_db_id:
                return []
                
            # Query the initiatives database
            response = self.notion.databases.query(self.initiatives_db_id)
            pages = response['results']
            
            initiatives = []
            for page in pages:
                # Get the title property (assuming it's the first title property)
                title_prop = None
                for prop_name, prop_details in page['properties'].items():
                    if prop_details['type'] == 'title':
                        title_prop = prop_details
                        break
                
                if title_prop and title_prop['title']:
                    page_title = title_prop['title'][0]['text']['content']
                    initiatives.append({
                        'name': page_title,
                        'id': page['id']
                    })
            
            return initiatives
        except Exception as e:
            st.error(f"Error getting initiative options: {e}")
            return []
    
    def validate_dropdown_selection(self, property_name, selected_value):
        """Validate if a selected value exists in the dropdown options"""
        if not selected_value:
            return True  # Empty values are allowed
        
        options = self.get_dropdown_options(property_name)
        return selected_value in options
    
    def validate_campaign_selection(self, selected_campaign_name):
        """Validate if a selected campaign exists in the campaigns database"""
        if not selected_campaign_name:
            return True  # Empty values are allowed
        
        campaigns = self.get_campaign_options()
        campaign_names = [campaign['name'] for campaign in campaigns]
        return selected_campaign_name in campaign_names
    
    def validate_affiliate_selection(self, selected_affiliate_name):
        """Validate if a selected affiliate exists in the affiliates database"""
        if not selected_affiliate_name:
            return True  # Empty values are allowed
        
        affiliates = self.get_affiliate_options()
        affiliate_names = [affiliate['name'] for affiliate in affiliates]
        return selected_affiliate_name in affiliate_names
    
    def validate_initiative_selection(self, selected_initiative_name):
        """Validate if a selected initiative exists in the initiatives database"""
        if not selected_initiative_name:
            return True  # Empty values are allowed
        
        initiatives = self.get_initiative_options()
        initiative_names = [initiative['name'] for initiative in initiatives]
        return selected_initiative_name in initiative_names
    
    def get_campaign_id(self, campaign_name):
        """Get the Notion page ID for a given campaign name"""
        if not campaign_name:
            return None
        
        campaigns = self.get_campaign_options()
        for campaign in campaigns:
            if campaign['name'] == campaign_name:
                return campaign['id']
        return None
    
    def get_affiliate_id(self, affiliate_name):
        """Get the Notion page ID for a given affiliate name"""
        if not affiliate_name:
            return None
        
        affiliates = self.get_affiliate_options()
        for affiliate in affiliates:
            if affiliate['name'] == affiliate_name:
                return affiliate['id']
        return None
    
    def get_initiative_id(self, initiative_name):
        """Get the Notion page ID for a given initiative name"""
        if not initiative_name:
            return None
        
        initiatives = self.get_initiative_options()
        for initiative in initiatives:
            if initiative['name'] == initiative_name:
                return initiative['id']
        return None
    
    def create_experiment_page(self, form_data):
        """Create a new experiment page in Notion"""
        try:
            # Prepare Notion properties
            properties = {
                "Test Order": {
                    "title": [{"text": {"content": "1"}}]
                },
                "Ad Chain": {
                    "rich_text": [{"text": {"content": form_data.get('treatment_variant', '')}}]
                }
            }
            
            # Add JIRA Link if provided
            if form_data.get('jira_link'):
                properties["JIRA Link (Ad Chain)"] = {
                    "url": form_data['jira_link']
                }
            
            # Add EPCVIP Campaign if provided
            if form_data.get('epcvip_campaign'):
                campaign_id = self.get_campaign_id(form_data['epcvip_campaign'])
                if campaign_id:
                    properties["EPCVIP Campaigns"] = {
                        "relation": [{"id": campaign_id}]
                    }
                else:
                    st.warning(f"Campaign '{form_data['epcvip_campaign']}' not found in Notion database")
            
            # Add Initiative if provided
            if form_data.get('epcvip_initiative'):
                initiative_id = self.get_initiative_id(form_data['epcvip_initiative'])
                if initiative_id:
                    properties["Feature"] = {
                        "relation": [{"id": initiative_id}]
                    }
                else:
                    st.warning(f"Initiative '{form_data['epcvip_initiative']}' not found in Notion database")
            
            # Add Feature Status (set to "Planned" for new experiments)
            properties["Feature Status"] = {
                "status": {"name": "Planned"}
            }
            
            # Create the page
            new_page = self.notion.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            
            # Add content to the page body
            self._add_page_content(new_page['id'], form_data)
            
            return new_page
            
        except Exception as e:
            st.error(f"Error creating experiment in Notion: {e}")
            return None
    
    def _add_page_content(self, page_id, form_data):
        """Add formatted content to the Notion page"""
        try:
            # Create formatted content
            content = self._format_experiment_content(form_data)
            
            # Add content as blocks to the page
            blocks = [
                {
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [{"type": "text", "text": {"content": "Experiment Design Details"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    }
                }
            ]
            
            self.notion.blocks.children.append(page_id, children=blocks)
            
        except Exception as e:
            st.error(f"Error adding content to page: {e}")
    
    def _format_experiment_content(self, form_data):
        """Format experiment data as readable text"""
        content_parts = []
        
        # Experiment Details
        content_parts.append("📋 EXPERIMENT DETAILS")
        content_parts.append(f"Name: {form_data.get('experiment_name', 'N/A')}")
        content_parts.append(f"Owner: {form_data.get('owner_name', 'N/A')}")
        content_parts.append(f"Stakeholders: {form_data.get('stakeholders', 'N/A')}")
        if form_data.get('epcvip_initiative'):
            content_parts.append(f"EPCVIP Initiative: {form_data.get('epcvip_initiative', 'N/A')}")
        content_parts.append(f"Feature Description: {form_data.get('feature_description', 'N/A')}")
        content_parts.append(f"Hypothesis: {form_data.get('hypothesis', 'N/A')}")
        
        # Configuration
        content_parts.append("\n⚙️ CONFIGURATION")
        content_parts.append(f"Test Type: {form_data.get('test_type', 'N/A')}")
        content_parts.append(f"Primary Metric: {form_data.get('primary_metric', 'N/A')}")
        content_parts.append(f"Baseline Value: {form_data.get('baseline_value', 'N/A')}")
        
        if form_data.get('test_type') == 'Superiority Test':
            content_parts.append(f"Expected Lift: {form_data.get('expected_lift', 'N/A')}%")
        else:
            content_parts.append(f"Non-Inferiority Margin: {form_data.get('non_inferiority_margin', 'N/A')}%")
        
        # Sample Size & Runtime
        content_parts.append(f"Sample Size: {form_data.get('calculated_sample_size', 'N/A'):,} users per group")
        content_parts.append(f"Total Sample Size: {form_data.get('calculated_sample_size', 0) * 2:,} users")
        content_parts.append(f"Estimated Runtime: {form_data.get('estimated_runtime', 'N/A')} days")
        
        # Campaign & Traffic
        content_parts.append("\n🎯 CAMPAIGN & TRAFFIC")
        if form_data.get('epcvip_campaign'):
            content_parts.append(f"EPCVIP Campaign: {form_data.get('epcvip_campaign', 'N/A')}")
        if form_data.get('epcvip_affiliate'):
            content_parts.append(f"EPCVIP Affiliate: {form_data.get('epcvip_affiliate', 'N/A')}")
        content_parts.append(f"Traffic Type: {form_data.get('traffic_type', 'N/A')}")
        content_parts.append(f"User Segment: {form_data.get('user_segment', 'N/A')}")
        content_parts.append(f"Device Type: {form_data.get('device_type', 'N/A')}")
        
        # Variants
        content_parts.append(f"Control Variant: {form_data.get('control_variant', 'N/A')}")
        content_parts.append(f"Treatment Variant: {form_data.get('treatment_variant', 'N/A')}")
        
        # Priority & Business Context
        content_parts.append("\n🚨 PRIORITY & BUSINESS CONTEXT")
        content_parts.append(f"Priority: {form_data.get('priority', 'N/A')}")
        content_parts.append(f"Business Goal: {form_data.get('business_goal', 'N/A')}")
        
        return "\n".join(content_parts) 