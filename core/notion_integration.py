import os
from notion_client import Client
from dotenv import load_dotenv
import streamlit as st
import time

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
        
        # Performance optimization: Cache for campaign and feature details
        self._campaign_cache = {}
        self._feature_cache = {}
        self._last_cache_refresh = 0
        self._cache_ttl = 300  # 5 minutes
        
        # Rate limiting for API calls
        self._last_api_call = 0
        self._min_call_interval = 0.1  # Minimum 100ms between API calls
    
    def _rate_limit_api_call(self):
        """Rate limit API calls to prevent overwhelming the API"""
        current_time = time.time()
        time_since_last_call = current_time - self._last_api_call
        
        if time_since_last_call < self._min_call_interval:
            time.sleep(self._min_call_interval - time_since_last_call)
        
        self._last_api_call = time.time()
    
    def _get_cached_campaign_details(self, campaign_id):
        """Get campaign details with caching"""
        current_time = time.time()
        
        # Refresh cache if expired
        if current_time - self._last_cache_refresh > self._cache_ttl:
            self._campaign_cache.clear()
            self._feature_cache.clear()
            self._last_cache_refresh = current_time
        
        if campaign_id not in self._campaign_cache:
            try:
                self._rate_limit_api_call()
                campaign_details = self.notion.pages.retrieve(campaign_id)
                campaign_name = campaign_details['properties'].get('Campaign Name', {}).get('title', [{}])[0].get('text', {}).get('content', '')
                self._campaign_cache[campaign_id] = campaign_name
            except Exception as e:
                # Don't show error for every failed call, just log it
                print(f"Warning: Error retrieving campaign {campaign_id}: {e}")
                self._campaign_cache[campaign_id] = f"Unknown Campaign ({campaign_id[:8]}...)"
        
        return self._campaign_cache[campaign_id]
    
    def _get_cached_feature_details(self, feature_id):
        """Get feature details with caching"""
        current_time = time.time()
        
        # Refresh cache if expired
        if current_time - self._last_cache_refresh > self._cache_ttl:
            self._campaign_cache.clear()
            self._feature_cache.clear()
            self._last_cache_refresh = current_time
        
        if feature_id not in self._feature_cache:
            try:
                self._rate_limit_api_call()
                feature_details = self.notion.pages.retrieve(feature_id)
                feature_name = feature_details['properties'].get('Name', {}).get('title', [{}])[0].get('text', {}).get('content', '')
                self._feature_cache[feature_id] = feature_name
            except Exception as e:
                # Don't show error for every failed call, just log it
                print(f"Warning: Error retrieving feature {feature_id}: {e}")
                self._feature_cache[feature_id] = f"Unknown Feature ({feature_id[:8]}...)"
        
        return self._feature_cache[feature_id]
    
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
    
    def get_experiments_by_status(self, exclude_statuses=None):
        """Get experiments filtered by status"""
        if exclude_statuses is None:
            exclude_statuses = ["Complete"]  # Only exclude "Complete", allow "Paused" and "Done"
        
        try:
            # Query all experiments
            response = self.notion.databases.query(self.database_id)
            pages = response['results']
            
            # Filter out experiments with excluded statuses
            filtered_experiments = []
            for page in pages:
                # Get the status property
                status_prop = page['properties'].get('Feature Status', {})
                if status_prop.get('type') == 'status' and status_prop.get('status'):
                    current_status = status_prop['status']['name']
                    if current_status not in exclude_statuses:
                        filtered_experiments.append(page)
            
            return filtered_experiments
        except Exception as e:
            print(f"Warning: Error fetching experiments: {e}")
            return []
    
    def get_experiments_by_campaign(self, campaign_name):
        """Get experiments for a specific campaign"""
        try:
            experiments = self.get_experiments_by_status()
            campaign_experiments = []
            
            for experiment in experiments:
                # Check campaign relation
                campaign_prop = experiment['properties'].get('EPCVIP Campaigns', {})
                if campaign_prop.get('type') == 'relation':
                    campaign_relations = campaign_prop.get('relation', [])
                    if campaign_relations:
                        # Get campaign details using cache
                        campaign_id = campaign_relations[0]['id']
                        campaign_title = self._get_cached_campaign_details(campaign_id)
                        
                        if campaign_title == campaign_name:
                            campaign_experiments.append(experiment)
            
            return campaign_experiments
        except Exception as e:
            st.error(f"Error fetching experiments by campaign: {e}")
            return []
    
    def get_initiatives_for_campaign(self, campaign_name):
        """Get initiatives that are actually used in experiments for a specific campaign"""
        try:
            campaign_experiments = self.get_experiments_by_campaign(campaign_name)
            initiatives = set()
            
            for experiment in campaign_experiments:
                # Check feature relation
                feature_prop = experiment['properties'].get('Feature', {})
                if feature_prop.get('type') == 'relation':
                    feature_relations = feature_prop.get('relation', [])
                    if feature_relations:
                        feature_id = feature_relations[0]['id']
                        feature_title = self._get_cached_feature_details(feature_id)
                        if feature_title and not feature_title.startswith("Unknown"):
                            initiatives.add(feature_title)
            
            return list(initiatives)
        except Exception as e:
            print(f"Warning: Error fetching initiatives for campaign: {e}")
            return []
    
    def get_campaigns_with_experiments(self):
        """Get campaigns that actually have experiments"""
        try:
            experiments = self.get_experiments_by_status()
            campaigns = set()
            
            for experiment in experiments:
                # Check campaign relation
                campaign_prop = experiment['properties'].get('EPCVIP Campaigns', {})
                if campaign_prop.get('type') == 'relation':
                    campaign_relations = campaign_prop.get('relation', [])
                    if campaign_relations:
                        # Get campaign details using cache
                        campaign_id = campaign_relations[0]['id']
                        campaign_title = self._get_cached_campaign_details(campaign_id)
                        if campaign_title and not campaign_title.startswith("Unknown"):
                            campaigns.add(campaign_title)
            
            return list(campaigns)
        except Exception as e:
            print(f"Warning: Error fetching campaigns with experiments: {e}")
            return []
    
    def get_experiment_by_campaign_and_feature(self, campaign_name, feature_name):
        """Get a specific experiment by campaign and feature"""
        try:
            experiments = self.get_experiments_by_status()
            
            for experiment in experiments:
                # Check campaign relation
                campaign_prop = experiment['properties'].get('EPCVIP Campaigns', {})
                if campaign_prop.get('type') == 'relation':
                    campaign_relations = campaign_prop.get('relation', [])
                    if campaign_relations:
                        # Get campaign details using cache
                        campaign_id = campaign_relations[0]['id']
                        campaign_title = self._get_cached_campaign_details(campaign_id)
                        
                        if campaign_title == campaign_name:
                            # Check feature relation
                            feature_prop = experiment['properties'].get('Feature', {})
                            if feature_prop.get('type') == 'relation':
                                feature_relations = feature_prop.get('relation', [])
                                if feature_relations:
                                    feature_id = feature_relations[0]['id']
                                    feature_title = self._get_cached_feature_details(feature_id)
                                    
                                    if feature_title == feature_name:
                                        return experiment
            
            return None
        except Exception as e:
            st.error(f"Error fetching experiment by campaign and feature: {e}")
            return None
    
    def get_experiment_content(self, experiment_id):
        """Get the content/body of an experiment page"""
        try:
            blocks = self.notion.blocks.children.list(experiment_id)
            return blocks['results']
        except Exception as e:
            st.error(f"Error fetching experiment content: {e}")
            return []
    
    def parse_experiment_design(self, experiment_content):
        """Parse experiment content to extract design parameters"""
        design_data = {}
        
        try:
            # Look for the paragraph block with experiment details
            for block in experiment_content:
                if block.get('type') == 'paragraph':
                    rich_text = block.get('paragraph', {}).get('rich_text', [])
                    if rich_text:
                        content = rich_text[0].get('text', {}).get('content', '')
                        
                        # Parse the content line by line
                        lines = content.split('\n')
                        for line in lines:
                            line = line.strip()
                            
                            # Extract test type
                            if 'Test Type:' in line:
                                design_data['test_type'] = line.split('Test Type:')[1].strip()
                            
                            # Extract primary metric
                            elif 'Primary Metric:' in line:
                                design_data['primary_metric'] = line.split('Primary Metric:')[1].strip()
                            
                            # Extract baseline value
                            elif 'Baseline Value:' in line:
                                baseline_str = line.split('Baseline Value:')[1].strip()
                                try:
                                    design_data['baseline_value'] = float(baseline_str.replace('%', ''))
                                except:
                                    design_data['baseline_value'] = None
                            
                            # Extract expected lift
                            elif 'Expected Lift:' in line:
                                lift_str = line.split('Expected Lift:')[1].strip().replace('%', '')
                                try:
                                    design_data['expected_lift'] = float(lift_str)
                                except:
                                    design_data['expected_lift'] = None
                            
                            # Extract non-inferiority margin
                            elif 'Non-Inferiority Margin:' in line:
                                margin_str = line.split('Non-Inferiority Margin:')[1].strip().replace('%', '')
                                try:
                                    design_data['non_inferiority_margin'] = float(margin_str)
                                except:
                                    design_data['non_inferiority_margin'] = None
                            
                            # Extract sample size
                            elif 'Sample Size:' in line and 'users per group' in line:
                                sample_str = line.split('Sample Size:')[1].split('users per group')[0].strip().replace(',', '')
                                try:
                                    design_data['sample_size'] = int(sample_str)
                                except:
                                    design_data['sample_size'] = None
                            
                            # Extract total sample size
                            elif 'Total Sample Size:' in line:
                                total_str = line.split('Total Sample Size:')[1].split('users')[0].strip().replace(',', '')
                                try:
                                    design_data['total_sample_size'] = int(total_str)
                                except:
                                    design_data['total_sample_size'] = None
            
            return design_data
            
        except Exception as e:
            st.error(f"Error parsing experiment design: {e}")
            return {}
    
    def parse_post_experiment_results(self, experiment_content):
        """Parse post-experiment results from experiment content"""
        post_experiment_data = {}
        
        try:
            # Look for the paragraph block with post-experiment results
            for block in experiment_content:
                if block.get('type') == 'paragraph':
                    rich_text = block.get('paragraph', {}).get('rich_text', [])
                    if rich_text:
                        content = rich_text[0].get('text', {}).get('content', '')
                        
                        # Check if this is the post-experiment results section
                        if 'POST-EXPERIMENT RESULTS' in content:
                            # Parse the content line by line
                            lines = content.split('\n')
                            for line in lines:
                                line = line.strip()
                                
                                # Extract control sample size
                                if 'Control Sample Size:' in line:
                                    sample_str = line.split('Control Sample Size:')[1].strip().replace(',', '')
                                    # Check if it's still a template placeholder
                                    if '[' in sample_str or sample_str == '':
                                        continue
                                    try:
                                        post_experiment_data['control_sample_size'] = int(sample_str)
                                    except:
                                        post_experiment_data['control_sample_size'] = 0
                                
                                # Extract treatment sample size
                                elif 'Treatment Sample Size:' in line:
                                    sample_str = line.split('Treatment Sample Size:')[1].strip().replace(',', '')
                                    # Check if it's still a template placeholder
                                    if '[' in sample_str or sample_str == '':
                                        continue
                                    try:
                                        post_experiment_data['treatment_sample_size'] = int(sample_str)
                                    except:
                                        post_experiment_data['treatment_sample_size'] = 0
                                
                                # Extract control applications
                                elif 'Control Applications:' in line:
                                    app_str = line.split('Control Applications:')[1].strip().replace(',', '')
                                    # Check if it's still a template placeholder
                                    if '[' in app_str or app_str == '':
                                        continue
                                    try:
                                        post_experiment_data['control_applications'] = int(app_str)
                                    except:
                                        post_experiment_data['control_applications'] = 0
                                
                                # Extract treatment applications
                                elif 'Treatment Applications:' in line:
                                    app_str = line.split('Treatment Applications:')[1].strip().replace(',', '')
                                    # Check if it's still a template placeholder
                                    if '[' in app_str or app_str == '':
                                        continue
                                    try:
                                        post_experiment_data['treatment_applications'] = int(app_str)
                                    except:
                                        post_experiment_data['treatment_applications'] = 0
                                
                                # Extract control mean
                                elif 'Control Mean:' in line:
                                    mean_str = line.split('Control Mean:')[1].strip()
                                    # Check if it's still a template placeholder
                                    if '[' in mean_str or mean_str == '':
                                        continue
                                    try:
                                        post_experiment_data['control_mean'] = float(mean_str)
                                    except:
                                        post_experiment_data['control_mean'] = 0.0
                                
                                # Extract treatment mean
                                elif 'Treatment Mean:' in line:
                                    mean_str = line.split('Treatment Mean:')[1].strip()
                                    # Check if it's still a template placeholder
                                    if '[' in mean_str or mean_str == '':
                                        continue
                                    try:
                                        post_experiment_data['treatment_mean'] = float(mean_str)
                                    except:
                                        post_experiment_data['treatment_mean'] = 0.0
            
            # Check if we have valid data (not template placeholders)
            if (post_experiment_data.get('control_sample_size', 0) > 0 and 
                post_experiment_data.get('treatment_sample_size', 0) > 0):
                return post_experiment_data
            else:
                return None
            
        except Exception as e:
            print(f"Warning: Error parsing post-experiment results: {e}")
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
            experiment_content = self._format_experiment_content(form_data)
            template_content = self._format_post_experiment_template(form_data)
            
            # Check character limits
            if len(experiment_content) > 1900:  # Leave some buffer
                st.warning("⚠️ Experiment content is very long. Some details may be truncated.")
                experiment_content = experiment_content[:1900] + "..."
            
            if len(template_content) > 1900:  # Leave some buffer
                st.warning("⚠️ Template content is very long. Some details may be truncated.")
                template_content = template_content[:1900] + "..."
            
            # Add experiment content as first block
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
                        "rich_text": [{"type": "text", "text": {"content": experiment_content}}]
                    }
                }
            ]
            
            self.notion.blocks.children.append(page_id, children=blocks)
            
            # Add template content as separate block
            template_blocks = [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": template_content}}]
                    }
                }
            ]
            
            self.notion.blocks.children.append(page_id, children=template_blocks)
            
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
    
    def _format_post_experiment_template(self, form_data):
        """Format post-experiment results template as separate content"""
        template_parts = []
        
        template_parts.append("📊 POST-EXPERIMENT RESULTS TEMPLATE")
        template_parts.append("Add your actual experiment results below:")
        template_parts.append("Control Sample Size: [Enter actual control group sample size]")
        template_parts.append("Treatment Sample Size: [Enter actual treatment group sample size]")
        
        if form_data.get('primary_metric') in ["App Rate", "Sold Rate", "Fund Rate"]:
            template_parts.append("Control Applications: [Enter actual control applications]")
            template_parts.append("Treatment Applications: [Enter actual treatment applications]")
        else:
            template_parts.append("Control Mean: [Enter actual control mean]")
            template_parts.append("Treatment Mean: [Enter actual treatment mean]")
        
        template_parts.append("\n💡 **Instructions:** Replace the [bracketed text] with your actual results. The Post-Experiment Analysis tool will automatically read these values.")
        
        return "\n".join(template_parts) 