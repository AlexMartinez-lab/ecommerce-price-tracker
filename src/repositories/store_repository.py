"""Data access operations for stores."""

from typing import Any

from src.models.store import Store
from src.repositories.base_repository import BaseRepository


class StoreRepository(BaseRepository):
    """Manage store records in PostgreSQL."""

    @staticmethod
    def _row_to_store(row: dict[str, Any] | None) -> Store | None:
        """Convert a database row into a Store object."""

        if row is None:
            return None

        return Store(
            id=row["id"],
            name=row["name"],
            domain=row["domain"],
            country_code=row["country_code"],
            active=row["active"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def create(self, store: Store) -> Store:
        """Insert and return a new store."""

        query = """
            INSERT INTO stores (
                name,
                domain,
                country_code,
                active
            )
            VALUES (%s, %s, %s, %s)
            RETURNING
                id,
                name,
                domain,
                country_code,
                active,
                created_at,
                updated_at;
        """

        row = self.fetch_one(
            query,
            (
                store.name,
                store.domain,
                store.country_code,
                store.active,
            ),
        )

        created_store = self._row_to_store(row)

        if created_store is None:
            raise RuntimeError("Store creation returned no data.")

        return created_store

    def get_by_id(self, store_id: int) -> Store | None:
        """Return one store by its identifier."""

        query = """
            SELECT
                id,
                name,
                domain,
                country_code,
                active,
                created_at,
                updated_at
            FROM stores
            WHERE id = %s;
        """

        return self._row_to_store(
            self.fetch_one(query, (store_id,))
        )

    def get_by_domain(self, domain: str) -> Store | None:
        """Return one store by its unique domain."""

        query = """
            SELECT
                id,
                name,
                domain,
                country_code,
                active,
                created_at,
                updated_at
            FROM stores
            WHERE domain = %s;
        """

        return self._row_to_store(
            self.fetch_one(query, (domain,))
        )

    def get_all(self, active_only: bool = False) -> list[Store]:
        """Return all stores."""

        query = """
            SELECT
                id,
                name,
                domain,
                country_code,
                active,
                created_at,
                updated_at
            FROM stores
        """

        parameters = None

        if active_only:
            query += " WHERE active = %s"
            parameters = (True,)

        query += " ORDER BY name;"

        rows = self.fetch_all(query, parameters)

        return [
            store
            for row in rows
            if (store := self._row_to_store(row)) is not None
        ]

    def disable(self, store_id: int) -> bool:
        """Disable one store without deleting its history."""

        query = """
            UPDATE stores
            SET
                active = FALSE,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
              AND active = TRUE;
        """

        return self.execute(query, (store_id,)) == 1