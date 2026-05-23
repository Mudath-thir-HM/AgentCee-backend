from app.db.sql import fetch_one, execute


async def get_user_by_email(email: str):
    query = """
    SELECT * FROM profiles
    WHERE email = $1
    """
    return await fetch_one(query, email)


async def create_user(
    email: str,
    password_hash: str,
    company_name: str
):
    query = """
    INSERT INTO profiles (
        email,
        password_hash,
        company_name
    )
    VALUES ($1, $2, $3)
    RETURNING *
    """

    return await fetch_one(
        query,
        email,
        password_hash,
        company_name
    )