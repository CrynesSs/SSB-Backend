from db import get_db

def fetch_user_by_field(field_name: str, value: str):
    """
   Fetch a user from the database using a unique field.

   Parameters:
   - field_name (str): The unique user field to search by. Must be one of:
       - 'username_hash'
       - 'public_key'
       - 'vanity_name'
   - value (str): The value to match for the specified field.

   Returns:
   - dict: A dictionary of the user's data if found, or None if not found.

   Raises:
   - ValueError: If the field_name is not one of the allowed fields.
   """
    # Only allow specific fields to prevent SQL injection
    allowed_fields = {"username_hash", "public_key", "vanity_name"}
    if field_name not in allowed_fields:
        raise ValueError(f"Invalid field name: {field_name}")
    db = get_db()
    user = db.execute(f"SELECT * FROM users WHERE {field_name} = ?", (value,)).fetchone()
    return user

def fetch_user_by_cookie(cookie):
    db = get_db()
    user = db.execute("SELECT users.* FROM cookies JOIN main.users ON cookies.user_id = users.id WHERE cookies.cookie = ?", (cookie,)).fetchone()
    return user if user else None

def fetch_user_current_storage_bytes(field_name: str, value: str):
    """
   Fetch a user from the database using a unique field.

   Parameters:
   - field_name (str): The unique user field to search by. Must be one of:
       - 'username_hash'
       - 'public_key'
       - 'vanity_name'
   - value (str): The value to match for the specified field.

   Returns:
   - dict: A dictionary of the user's data if found, or None if not found.

   Raises:
   - ValueError: If the field_name is not one of the allowed fields.
   """
    allowed_fields = {"username_hash", "public_key", "vanity_name"}
    if field_name not in allowed_fields:
        raise ValueError(f"Invalid field name: {field_name}")
    db = get_db()
    current_storage_bytes = db.execute(f"SELECT COALESCE(SUM(LENGTH(file_size)), 0) as total FROM user_data_file WHERE uploaded_by = (SELECT id FROM users WHERE {field_name} = ?)",
                                       value).fetchone()
    return current_storage_bytes if current_storage_bytes else None



