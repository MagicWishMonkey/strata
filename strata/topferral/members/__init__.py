from .members import Members
from .member import Member

Members.__table_name__ = "members"
# Members.__cache_config__["ttl"] = 120

Members.__select_query__ = """
SELECT
    id,
    label,
    username,
    avatar,
    access_code,
    access_token,
    registered
FROM members;
""".strip()

# Members.__lookup_query__ = """
# SELECT id FROM members WHERE username=@label;
# """.strip()

#__insert_query__ = None
#__update_query__ = None
#__delete_query__ = None