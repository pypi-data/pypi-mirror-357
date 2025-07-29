import jwt

def create_token(secret_key: str, user: dict, recipient: dict = None) -> str:
    """
    Create a JWT token for a user (and optional recipient) for Teemboom Chat.

    Args:
        secret_key (str): The secret key to sign the token.
        user (dict): A dictionary with at least an 'id' key.
        recipient (dict, optional): A dictionary with at least an 'id' key.

    Returns:
        str: A JWT token string.
    """
    if not isinstance(user, dict):
        raise ValueError("User must be a dictionary")

    if not user.get('id'):
        raise ValueError("User must have an 'id'")

    if recipient is not None:
        if not isinstance(recipient, dict):
            raise ValueError("Recipient must be a dictionary")
        if not recipient.get('id'):
            raise ValueError("Recipient must have an 'id'")

    payload = {"user": user}
    if recipient is not None:
        payload["recipient"] = recipient

    return jwt.encode(payload, key=secret_key, algorithm="HS256")
