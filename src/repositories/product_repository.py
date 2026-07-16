"""Data access operations for canonical products."""

from typing import Any

from src.models.product import Product
from src.repositories.base_repository import BaseRepository


class ProductRepository(BaseRepository):
    """Manage product records in PostgreSQL."""

    @staticmethod
    def _row_to_product(row: dict[str, Any] | None) -> Product | None:
        """Convert a database row into a Product object."""

        if row is None:
            return None

        return Product(
            id=row["id"],
            name=row["name"],
            brand=row["brand"],
            model=row["model"],
            sku=row["sku"],
            description=row["description"],
            active=row["active"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def create(self, product: Product) -> Product:
        """Insert and return a new canonical product."""

        query = """
            INSERT INTO products (
                name,
                brand,
                model,
                sku,
                description,
                active
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING
                id,
                name,
                brand,
                model,
                sku,
                description,
                active,
                created_at,
                updated_at;
        """

        parameters = (
            product.name,
            product.brand,
            product.model,
            product.sku,
            product.description,
            product.active,
        )

        row = self.fetch_one(query, parameters)
        created_product = self._row_to_product(row)

        if created_product is None:
            raise RuntimeError("Product creation returned no data.")

        return created_product

    def get_by_id(self, product_id: int) -> Product | None:
        """Return one product by its identifier."""

        query = """
            SELECT
                id,
                name,
                brand,
                model,
                sku,
                description,
                active,
                created_at,
                updated_at
            FROM products
            WHERE id = %s;
        """

        row = self.fetch_one(query, (product_id,))
        return self._row_to_product(row)

    def get_all(self, active_only: bool = False) -> list[Product]:
        """Return all products."""

        query = """
            SELECT
                id,
                name,
                brand,
                model,
                sku,
                description,
                active,
                created_at,
                updated_at
            FROM products
        """

        parameters = None

        if active_only:
            query += " WHERE active = %s"
            parameters = (True,)

        query += " ORDER BY name;"

        rows = self.fetch_all(query, parameters)

        return [
            product
            for row in rows
            if (product := self._row_to_product(row)) is not None
        ]

    def search_by_name(self, search_term: str) -> list[Product]:
        """Search products using a case-insensitive partial match."""

        query = """
            SELECT
                id,
                name,
                brand,
                model,
                sku,
                description,
                active,
                created_at,
                updated_at
            FROM products
            WHERE name ILIKE %s
            ORDER BY name;
        """

        rows = self.fetch_all(query, (f"%{search_term}%",))

        return [
            product
            for row in rows
            if (product := self._row_to_product(row)) is not None
        ]

    def update(self, product: Product) -> Product:
        """Update and return an existing product."""

        if product.id is None:
            raise ValueError("Product ID is required for updates.")

        query = """
            UPDATE products
            SET
                name = %s,
                brand = %s,
                model = %s,
                sku = %s,
                description = %s,
                active = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING
                id,
                name,
                brand,
                model,
                sku,
                description,
                active,
                created_at,
                updated_at;
        """

        parameters = (
            product.name,
            product.brand,
            product.model,
            product.sku,
            product.description,
            product.active,
            product.id,
        )

        row = self.fetch_one(query, parameters)
        updated_product = self._row_to_product(row)

        if updated_product is None:
            raise LookupError(
                f"Product with ID {product.id} was not found."
            )

        return updated_product

    def disable(self, product_id: int) -> bool:
        """Disable tracking without deleting historical information."""

        query = """
            UPDATE products
            SET
                active = FALSE,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
              AND active = TRUE;
        """

        affected_rows = self.execute(query, (product_id,))
        return affected_rows == 1