from database import Database

class Category:
    def __init__(self):
        self.db = Database()

    def add_category(self, name, description=""):
        """Add a new category"""
        query = "INSERT INTO categories (name, description) VALUES (?, ?)"
        try:
            return self.db.execute_query(query, (name, description))
        except:
            return False

    def get_all_categories(self):
        """Get all categories"""
        query = "SELECT * FROM categories ORDER BY name ASC"
        return self.db.execute_query(query)

    def delete_category(self, category_id):
        """Delete a category"""
        # Note: You might want to handle products in this category before deleting
        query = "DELETE FROM categories WHERE category_id = ?"
        return self.db.execute_query(query, (category_id,))

    def update_category(self, category_id, name, description):
        """Update a category"""
        query = "UPDATE categories SET name = ?, description = ? WHERE category_id = ?"
        return self.db.execute_query(query, (name, description, category_id))
