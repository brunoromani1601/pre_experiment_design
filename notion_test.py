import os
from notion_client import Client
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_notion_connection():
    """Test Notion API connection and list available databases"""
    
    # Get token from environment variable
    token = os.getenv('NOTION_TOKEN')
    if not token or token == 'your_notion_integration_token_here':
        print("❌ Please set your Notion token in the .env file")
        print("   Edit .env and replace 'your_notion_integration_token_here' with your actual token")
        return None
    
    try:
        # Initialize Notion client
        notion = Client(auth=token)
        print("✅ Successfully connected to Notion API!")
        
        # List all databases the integration has access to
        print("\n📋 Available Databases:")
        print("-" * 50)
        
        response = notion.search(
            filter={"property": "object", "value": "database"}
        )
        
        if response['results']:
            for i, database in enumerate(response['results'], 1):
                db_id = database['id']
                db_title = database.get('title', [{}])[0].get('plain_text', 'Untitled')
                print(f"{i}. {db_title}")
                print(f"   ID: {db_id}")
                print(f"   URL: https://notion.so/{db_id.replace('-', '')}")
                print()
        else:
            print("❌ No databases found. Make sure you've shared a database with your integration.")
            return None
            
        return notion, response['results']
        
    except Exception as e:
        print(f"❌ Error connecting to Notion: {e}")
        return None

def get_database_schema(notion, database_id):
    """Get the schema/properties of a specific database"""
    try:
        database = notion.databases.retrieve(database_id)
        print(f"\n📊 Database Schema for: {database.get('title', [{}])[0].get('plain_text', 'Untitled')}")
        print("-" * 60)
        
        properties = database['properties']
        for prop_name, prop_details in properties.items():
            prop_type = prop_details['type']
            print(f"• {prop_name} ({prop_type})")
            
        return properties
        
    except Exception as e:
        print(f"❌ Error retrieving database schema: {e}")
        return None

def test_insert_experiment(notion, database_id, properties):
    """Test inserting a sample experiment record that fits the Experiments database schema"""
    
    # Create a sample experiment data that matches the actual database schema
    sample_experiment = {
        "Test Order": {
            "title": [{"text": {"content": "Test Dynamic CTA Text Experiment"}}]
        },
        "Ad Chain": {
            "rich_text": [{"text": {"content": "PPC Ad Chain - Testing CTA text change from 'Apply Now' to 'Get Approved Fast'"}}]
        },
        "JIRA Summary (Ad Chain)": {
            "rich_text": [{"text": {"content": "A/B test to improve app rate by changing CTA text to create urgency"}}]
        },
        "JIRA Link (Ad Chain)": {
            "url": "https://jira.company.com/browse/EXP-123"
        },
        "Status": {
            "status": {"name": "Not started"}
        },
        "Status (Ad Chain)": {
            "select": {"name": "Not started"}
        },
        "Feature Status": {
            "status": {"name": "Planned"}
        },
        "Date Set Live": {
            "date": {
                "start": "2024-12-31",
                "end": None
            }
        }
        # Note: ID is auto-generated, Last Synced will be set by Notion
    }
    
    # Filter sample data to only include properties that exist in the database
    filtered_experiment = {}
    for prop_name, prop_value in sample_experiment.items():
        if prop_name in properties:
            filtered_experiment[prop_name] = prop_value
    
    try:
        print(f"\n🧪 Testing experiment insertion...")
        print(f"📝 Sample data: {json.dumps(filtered_experiment, indent=2)}")
        
        new_page = notion.pages.create(
            parent={"database_id": database_id},
            properties=filtered_experiment
        )
        
        print("✅ Successfully created experiment in Notion!")
        print(f"📄 Page ID: {new_page['id']}")
        print(f"🔗 URL: https://notion.so/{new_page['id'].replace('-', '')}")
        
        return new_page
        
    except Exception as e:
        print(f"❌ Error inserting experiment: {e}")
        print(f"Error details: {json.dumps(e.__dict__, indent=2) if hasattr(e, '__dict__') else str(e)}")
        return None

def main():
    """Main test function"""
    print("🧪 Notion API Connection Test")
    print("=" * 50)
    
    # Test connection and get databases
    result = test_notion_connection()
    if not result:
        return
    
    notion, databases = result
    
    # Let user select a database
    if len(databases) == 1:
        selected_db = databases[0]
        print(f"📋 Using the only available database: {selected_db.get('title', [{}])[0].get('plain_text', 'Untitled')}")
    else:
        try:
            choice = int(input(f"\nSelect database (1-{len(databases)}): ")) - 1
            if 0 <= choice < len(databases):
                selected_db = databases[choice]
            else:
                print("❌ Invalid selection")
                return
        except ValueError:
            print("❌ Please enter a valid number")
            return
    
    database_id = selected_db['id']
    
    # Get database schema
    properties = get_database_schema(notion, database_id)
    if not properties:
        return
    
    # Test insertion
    test_insert_experiment(notion, database_id, properties)

if __name__ == "__main__":
    main() 