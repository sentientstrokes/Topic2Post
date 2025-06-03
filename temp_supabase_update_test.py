import os
from supabase import create_client, Client
import logfire
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Logfire (optional, but good for debugging)
logfire.configure()

def test_supabase_update(topic_id: int):
    """
    Tests updating the 'Processed' column for a specific topic ID in Supabase.
    """
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_API_KEY")
    if not supabase_url or not supabase_key:
        logfire.error("SUPABASE_URL and SUPABASE_API_KEY must be set in environment variables.")
        return False

    try:
        client: Client = create_client(supabase_url, supabase_key)

        logfire.info("Attempting to mark topic {id} as processed.", id=topic_id)
        response = client.from_('Test-Article to Social').update({'Processed': True}).eq('id', topic_id).execute()

        # Check if the update was successful by verifying if data was returned.
        # Based on insert/upsert examples, a successful operation might return data.
        if response is not None and response.data:
            logfire.debug("Successfully marked topic {id} as processed. Response data: {data}. Rows updated (count attribute): {count}", id=topic_id, data=response.data, count=response.count)
            logfire.info("Supabase update test successful for topic {id}.", id=topic_id)
            return True
        else:
            # Log a warning if no data was returned or response is None
            logfire.warn("Supabase update for id {id} returned no data or a None response. Response: {response}", id=topic_id, response=response)
            logfire.error("Supabase update test failed for topic {id}.", id=topic_id)
            return False

    except Exception as e:
        logfire.error("An unexpected error occurred during Supabase update test for topic {id}: {error}", id=topic_id, error=e, exc_info=True)
        return False

if __name__ == "__main__":
    # Test with topic ID 1
    test_supabase_update(1)