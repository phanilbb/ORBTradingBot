'''
Introduce an operation for retrieving statistics about how frequently records are updated.

top_n_keys(self, n: int) -> list[str] — should return the keys of the top n records when all records are sorted in descending order by the number of successful modifications to them, such as adding, deleting, or changing a field within the record. Increasing a value by 0 is considered a successful modification. In case of a tie, keys must be sorted in lexicographical order of their names. The result should be a string in the following format: ["<key_1>(<number_of_modifications_1>)", "<key_2>(<number_of_modifications_2>)", ..., "<key_n>(<number_of_modifications_n>)"]. If less than n records exist in the system, return all keys in the described format. If there are no records at all, return an empty list. If a record is deleted from the database (i.e., if all of its fields are deleted), the counter for the number of successful modifications to the record must also be deleted.

'''

from __future__ import annotations


class InMemoryDB:
    def __init__(self):
        self.db = {}  # Stores records as { key: { field: value } }
        self.modifications = {}  # Tracks the number of successful modifications per key

    def set_or_inc(self, key: str, field: str, value: int) -> int:
        if key not in self.db:
            self.db[key] = {}
            self.modifications[key] = 0  # Initialize modification counter

        if field not in self.db[key]:
            self.db[key][field] = value
        else:
            self.db[key][field] += value

        self.modifications[key] += 1  # Increment modification count
        return self.db[key][field]

    def get(self, key: str, field: str) -> int | None:
        return self.db.get(key, {}).get(field, None)

    def delete(self, key: str, field: str) -> bool:
        if key in self.db and field in self.db[key]:
            del self.db[key][field]
            self.modifications[key] += 1  # Increment modification count

            if not self.db[key]:  # Remove record if empty
                del self.db[key]
                del self.modifications[key]  # Delete modification counter
            return True
        return False

    def top_n_keys(self, n: int) -> list[str]:
        sorted_keys = sorted(self.modifications.items(),
                             key=lambda x: (-x[1], x[0]))  # Sort by count desc, then lexicographically
        return [f"{key}({count})" for key, count in sorted_keys[:n]]
