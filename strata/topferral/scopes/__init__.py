from .scopes import Scopes
from .scope import Scope

Scopes.__table_name__ = "members"

Scopes.__select_query__ = """
SELECT
    id,
    label,
    member_id,
    description,
    website,
    created
FROM scopes;
""".strip()

# Members.__lookup_query__ = """
# SELECT id FROM members WHERE username=@label;
# """.strip()

#__insert_query__ = None
#__update_query__ = None
#__delete_query__ = None