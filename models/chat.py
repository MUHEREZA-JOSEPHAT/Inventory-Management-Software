from database import Database

class Chat:
    def __init__(self):
        self.db = Database()

    def send_message(self, sender, message):
        """Save a new chat message"""
        query = "INSERT INTO chat_messages (sender, message) VALUES (?, ?)"
        return self.db.execute_query(query, (sender, message))

    def get_messages(self, limit=50):
        """Retrieve recent chat messages"""
        query = "SELECT sender, message, timestamp FROM chat_messages ORDER BY timestamp ASC LIMIT ?"
        return self.db.execute_query(query, (limit,))

    def clear_history(self):
        """Clear all chat history"""
        query = "DELETE FROM chat_messages"
        return self.db.execute_query(query)
