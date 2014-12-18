from .sessions import Sessions
from .session import Session

Sessions.__table_name__ = "sessions"
# Members.__cache_config__["ttl"] = 120

Sessions.__select_query__ = """
SELECT
    id,
    token,
    member_id,
    created,
    accessed
FROM sessions;
""".strip()


#__insert_query__ = None
#__update_query__ = None
#__delete_query__ = None