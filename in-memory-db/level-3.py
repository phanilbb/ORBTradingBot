'''

Level 3

Introduce operations to support users locking access to records.

Users can request to temporarily lock a particular record, acquiring exclusive modification access.
If a record is already locked by another user, locking requests are put in a first-in-first-out queue.
Repeated locking requests for a record from the same user should be ignored.
Each modification operation from the previous levels now has an alternative version with a caller_id parameter, which represents a unique string identifier associated with a user. These operations should function the same way as the original version if the user with the given caller_id has locked the record and thus is eligible to modify the record; otherwise, the operation will not change the database. The prior versions should not modify locked records due to the lack of a caller_id to establish permissions. When a user waits for modification access to a locked record, any modification operations they execute on the record are ignored (instead of delayed).

Note that locking should not affect the get operation - values of records can be read at any time, regardless of who has locked access to the record.

set_or_inc_by_caller(self, key: str, field: str, value: int, caller_id: str) -> int | None — if a record with the given key does not exist, or is not locked, or the user associated with caller_id is the one who has locked it, perform the set_or_inc operation described in Level 1. Otherwise, ignore the operation and return the existing value if the field exists; otherwise, return None.

delete_by_caller(self, key: str, field: str, caller_id: str) -> bool — if the record with the given key exists, and it is either not locked or the user associated with caller_id is the one who has locked it, perform the delete operation described in Level 1. Otherwise, ignore the operation and return False.

lock(self, caller_id: str, key: str) -> str | None — should request to lock the record associated with key to the user associated with caller_id. After locking a record, the set_or_inc and delete operations cannot be performed on that record, so they should be ignored if called. The operation returns one of the following to signal lock status:

"acquired" - if the key is valid and the record is successfully locked to the user;
"wait" - if the record is already locked by another user, the user should be added to the queue for locking this record, and will be able to lock the record when it gets released from the previous user;
None - if there is an existing lock request from the same user or the record is already locked by the same user;
"invalid_request" - if the key doesn't exist in the database.
unlock(self, key: str) -> str | None — should release the current lock on the record associated with key. The next user in the lock queue for this record, if any, should automatically obtain a lock. The only way to release the lock from any record is to call the unlock operation explicitly. It does nothing if the record is not currently locked by any users. If the record is not present in the database when unlocked, meaning it was entirely deleted and then unlocked, all lock requests for this record should be deleted. Note that if the key was entirely deleted and re-created with the same key during one lock, it is considered the same record. Returns one of the following to signal lock status:

"released" - if the lock was released during the operation, including the case when the record was locked, entirely deleted and then unlocked;
None - if the key exists, but was not locked;
"invalid_request" - if the key doesn't exist in the database.

'''

from __future__ import annotations

from collections import deque


class InMemoryDB:
    def __init__(self):
        self.db = {}  # Stores records as { key: { field: value } }
        self.modifications = {}  # Tracks the number of successful modifications per key
        self.locks = {}  # Tracks locked records as { key: caller_id }
        self.lock_queues = {}  # Tracks lock wait queues as { key: deque([caller_id_1, caller_id_2, ...]) }

    def set_or_inc(self, key: str, field: str, value: int) -> int | None:
        """Original method, now ignored if the record is locked."""
        if key in self.locks:
            return None  # Ignore modification if record is locked

        return self._set_or_inc_internal(key, field, value)

    def set_or_inc_by_caller(self, key: str, field: str, value: int, caller_id: str) -> int | None:
        """Caller-specific modification method with lock checking."""
        if key in self.locks and self.locks[key] != caller_id:
            return self.get(key, field)  # Ignore modification if another user has the lock

        return self._set_or_inc_internal(key, field, value)

    def _set_or_inc_internal(self, key: str, field: str, value: int) -> int:
        """Internal helper for modifying records."""
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
        """Retrieves a value, unaffected by locks."""
        return self.db.get(key, {}).get(field, None)

    def delete(self, key: str, field: str) -> bool:
        """Original method, now ignored if the record is locked."""
        if key in self.locks:
            return False  # Ignore deletion if record is locked

        return self._delete_internal(key, field)

    def delete_by_caller(self, key: str, field: str, caller_id: str) -> bool:
        """Caller-specific deletion method with lock checking."""
        if key in self.locks and self.locks[key] != caller_id:
            return False  # Ignore deletion if another user has the lock

        return self._delete_internal(key, field)

    def _delete_internal(self, key: str, field: str) -> bool:
        """Internal helper for deleting fields."""
        if key in self.db and field in self.db[key]:
            del self.db[key][field]
            self.modifications[key] += 1  # Increment modification count

            if not self.db[key]:  # Remove record if empty
                del self.db[key]
                del self.modifications[key]  # Delete modification counter

            return True
        return False

    def lock(self, caller_id: str, key: str) -> str | None:
        """Locks a record for exclusive modification access."""
        if key not in self.db:
            return "invalid_request"  # Key doesn't exist

        if key in self.locks:
            if self.locks[key] == caller_id:
                return None  # Already locked by the same user
            if caller_id in self.lock_queues.get(key, []):
                return None  # Already waiting in queue

            self.lock_queues.setdefault(key, deque()).append(caller_id)
            return "wait"

        self.locks[key] = caller_id  # Acquire lock
        return "acquired"

    def unlock(self, key: str) -> str | None:
        """Releases a lock and assigns it to the next user in the queue, if any."""
        if key not in self.db:
            if key in self.locks:
                del self.locks[key]  # Remove lock if record was deleted
                self.lock_queues.pop(key, None)  # Clear any lock queues
                return "released"
            return "invalid_request"

        if key not in self.locks:
            return None  # No active lock

        del self.locks[key]  # Release lock

        if self.lock_queues.get(key):
            next_caller = self.lock_queues[key].popleft()
            self.locks[key] = next_caller  # Assign lock to next user
            if not self.lock_queues[key]:
                del self.lock_queues[key]  # Remove empty queue

        return "released"

    def top_n_keys(self, n: int) -> list[str]:
        """Returns the top N most modified keys."""
        sorted_keys = sorted(self.modifications.items(),
                             key=lambda x: (-x[1], x[0]))  # Sort by count desc, then lexicographically
        return [f"{key}({count})" for key, count in sorted_keys[:n]]
