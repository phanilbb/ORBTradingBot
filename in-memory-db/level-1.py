'''

Level 1
The basic level of the in-memory database contains records. Each record can be accessed with a unique identifier key, which is of string type. A record contains several field-value pairs, with field as string type and value as integer type.

set_or_inc(self, key: str, field: str, value: int) -> int | None — should insert a field-value pair to the record associated with key. All value should be integers. If the field in the record already exists, increase the current value by the specified value. If the record or field does not exist, a new one should be created with the value set to the value. This operation should return the inserted or updated value (in this level, None is never returned).

get(self, key: str, field: str) -> int | None — should return the value within field of the record associated with key. If the record or the field does not exist, should return None.

delete(self, key: str, field: str) -> bool — should remove field from the record associated with key. Returns True if the field was deleted, and False otherwise. If all fields in a record have been deleted, the record should be deleted.

'''

from __future__ import annotations


class InMemoryDB:
    def __init__(self):
        self.db = {}  # Stores records as { key: { field: value } }

    def set_or_inc(self, key: str, field: str, value: int) -> int:
        if key not in self.db:
            self.db[key] = {}
        if field not in self.db[key]:
            self.db[key][field] = value
        else:
            self.db[key][field] += value
        return self.db[key][field]

    def get(self, key: str, field: str) -> int | None:
        return self.db.get(key, {}).get(field, None)

    def delete(self, key: str, field: str) -> bool:
        if key in self.db and field in self.db[key]:
            del self.db[key][field]
            if not self.db[key]:  # Remove record if empty
                del self.db[key]
            return True
        return False
