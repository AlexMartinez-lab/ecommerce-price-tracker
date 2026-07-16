"""Integration tests for ProductRepository."""

import unittest
from uuid import uuid4

from src.models.product import Product
from src.repositories.product_repository import ProductRepository


class ProductRepositoryTestCase(unittest.TestCase):
    """Validate product persistence operations."""

    def setUp(self) -> None:
        """Create repository and unique test product."""

        self.repository = ProductRepository()
        unique_value = uuid4().hex[:8]

        self.product = self.repository.create(
            Product(
                name=f"Repository Test Product {unique_value}",
                brand="Test Brand",
                model=f"TEST-{unique_value}",
            )
        )

    def tearDown(self) -> None:
        """Disable the test product after every test."""

        if self.product.id is not None:
            self.repository.disable(self.product.id)

    def test_create_and_get_by_id(self) -> None:
        """A created product must be retrievable by ID."""

        self.assertIsNotNone(self.product.id)

        retrieved = self.repository.get_by_id(
            self.product.id
        )

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, self.product.name)
        self.assertEqual(retrieved.model, self.product.model)

    def test_search_by_name(self) -> None:
        """Partial product searches must return matches."""

        results = self.repository.search_by_name(
            self.product.name
        )

        result_ids = {
            product.id
            for product in results
        }

        self.assertIn(self.product.id, result_ids)

    def test_update_product(self) -> None:
        """Product information must be updateable."""

        self.product.description = "Updated description"

        updated = self.repository.update(self.product)

        self.assertEqual(
            updated.description,
            "Updated description",
        )

    def test_disable_product(self) -> None:
        """Disabling a product must set active to false."""

        result = self.repository.disable(
            self.product.id
        )

        retrieved = self.repository.get_by_id(
            self.product.id
        )

        self.assertTrue(result)
        self.assertIsNotNone(retrieved)
        self.assertFalse(retrieved.active)


if __name__ == "__main__":
    unittest.main()