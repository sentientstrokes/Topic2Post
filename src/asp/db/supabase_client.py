import os
from supabase import create_client, Client
import logfire
from asp.utils.decorators import retry

class SupabaseClient:
    """
    Client for interacting with the Supabase database.
    """
    def __init__(self):
        """
        Initializes the SupabaseClient.
        """
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_API_KEY")
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables.")
        self.client: Client = create_client(supabase_url, supabase_key)

    @retry()
    def fetch_unprocessed_topics(self, limit: int):
        """
        Fetches unprocessed article topics from the database.

        Args:
            limit (int): The maximum number of topics to fetch.

        Returns:
            List[Dict]: A list of dictionaries, each containing the 'id' and 'topic_name' of an unprocessed topic.
        """
        logfire.info("Fetching unprocessed topics with limit {limit}", limit=limit)
        response = self.client.from_('Test-Article to Social').select('id, "Topics"').eq('Processed', False).order('id').limit(limit).execute()
        # Assuming response.data contains the list of topics
        logfire.debug("Fetched {count} unprocessed topics.", count=len(response.data) if response.data else 0)
        return response.data

    @retry()
    def mark_as_processed(self, id: str, summary: str) -> bool:
        """
        Marks a topic as processed and saves the summary.

        Args:
            id (str): The ID of the topic to mark as processed.
            summary (str): The generated summary for the topic.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        logfire.info("Marking topic {id} as processed.", id=id)
        try:
            response = self.client.from_('Test-Article to Social').update({'Processed': True, 'Summary': summary}).eq('id', id).execute()
            # Check if the update was successful by verifying if data was returned.
            # Based on insert/upsert examples, a successful operation might return data.
            if response is not None and response.data:
                logfire.debug("Successfully marked topic {id} as processed. Response data: {data}. Rows updated (count attribute): {count}", id=id, data=response.data, count=response.count)
                return True
            else:
                # Log a warning if no data was returned or response is None
                logfire.warn("Supabase update for id {id} returned no data or a None response. Response: {response}", id=id, response=response)
                return False
        except Exception as e:
            logfire.error("Error marking topic as processed: {error}", error=e, id=id, exc_info=True)
            return False