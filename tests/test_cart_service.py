import unittest
from unittest.mock import AsyncMock, patch

from src.pycartnext import Cart, CartItem, CartService, DbManager


class TestCartService(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.cart_id = "test-cart-id"
        self.cart_service = CartService(self.cart_id)

        # Mock the backend and initialize Cache
        self.mock_backend = AsyncMock()
        DbManager.init(self.mock_backend)

    async def test_get_cart_when_cart_exists(self) -> None:
        mock_cart_data = {
            "id": self.cart_id,
            "items": [{"id": "item1", "title": "Item 1", "quantity": 2, "price": 10.0}],
        }
        with patch(
            "src.pycartnext.core.db.manager.DbManager.get", return_value=mock_cart_data
        ):
            cart = await self.cart_service.get_cart()
            self.assertEqual(cart.id, self.cart_id)
            self.assertEqual(len(cart.items), 1)
            self.assertEqual(cart.items[0].id, "item1")

    async def test_get_cart_when_cart_does_not_exist(self) -> None:
        with patch("src.pycartnext.core.db.manager.DbManager.get", return_value=None):
            cart = await self.cart_service.get_cart()
            self.assertEqual(cart.id, self.cart_id)
            self.assertEqual(len(cart.items), 0)

    async def test_save_cart(self) -> None:
        mock_cart = Cart(
            id=self.cart_id,
            items=[{"id": "item1", "title": "Item 1", "quantity": 2, "price": 10.0}],
        )

        with patch(
            "src.pycartnext.core.db.manager.DbManager.set", AsyncMock()
        ) as mock_cache_set:
            await self.cart_service.save_cart(mock_cart)
            mock_cache_set.assert_awaited_once_with(
                self.cart_id, mock_cart.model_dump()
            )

    async def test_add_item_new_item(self) -> None:
        mock_item = CartItem(id="item1", title="New Item", quantity=2, price=15.0)
        initial_cart = Cart(id=self.cart_id, items=[])

        with patch.object(
            self.cart_service, "get_cart", return_value=initial_cart
        ), patch.object(self.cart_service, "save_cart", AsyncMock()) as mock_save_cart:
            await self.cart_service.add_item(mock_item)
            self.assertEqual(len(initial_cart.items), 1)
            self.assertEqual(initial_cart.items[0].id, "item1")
            self.assertEqual(initial_cart.items[0].quantity, 2)
            mock_save_cart.assert_awaited_once_with(initial_cart)

    async def test_remove_item_existing_item(self) -> None:
        mock_item_to_remove = CartItem(
            id="item1", title="Item 1", quantity=2, price=10.0
        )
        existing_cart = Cart(
            id=self.cart_id,
            items=[
                mock_item_to_remove,
                CartItem(id="item2", title="Item 2", quantity=1, price=20.0),
            ],
        )
        with patch.object(
            self.cart_service, "get_cart", return_value=existing_cart
        ), patch.object(self.cart_service, "save_cart", AsyncMock()) as mock_save_cart:
            await self.cart_service.remove_item("item1")
            self.assertEqual(len(existing_cart.items), 1)
            self.assertEqual(existing_cart.items[0].id, "item2")
            mock_save_cart.assert_awaited_once_with(existing_cart)

    async def test_remove_item_item_not_found(self) -> None:
        existing_cart = Cart(
            id=self.cart_id,
            items=[CartItem(id="item2", title="Item 2", quantity=1, price=20.0)],
        )
        with patch.object(
            self.cart_service, "get_cart", return_value=existing_cart
        ), patch.object(self.cart_service, "save_cart", AsyncMock()) as mock_save_cart:
            await self.cart_service.remove_item("item1")
            self.assertEqual(len(existing_cart.items), 1)
            self.assertEqual(existing_cart.items[0].id, "item2")
            mock_save_cart.assert_awaited_once_with(existing_cart)

    async def test_increment_quantity_existing_item(self) -> None:
        mock_item_to_increment = CartItem(
            id="item1", title="Item 1", quantity=2, price=10.0
        )
        existing_cart = Cart(
            id=self.cart_id,
            items=[
                mock_item_to_increment,
                CartItem(id="item2", title="Item 2", quantity=1, price=20.0),
            ],
        )
        with patch.object(
            self.cart_service, "get_cart", return_value=existing_cart
        ), patch.object(self.cart_service, "save_cart", AsyncMock()) as mock_save_cart:
            await self.cart_service.increment_quantity("item1")
            self.assertEqual(mock_item_to_increment.quantity, 3)
            mock_save_cart.assert_awaited_once_with(existing_cart)

    async def test_increment_quantity_item_not_found(self) -> None:
        existing_cart = Cart(
            id=self.cart_id,
            items=[CartItem(id="item2", title="Item 2", quantity=1, price=20.0)],
        )
        with patch.object(
            self.cart_service, "get_cart", return_value=existing_cart
        ), patch.object(self.cart_service, "save_cart", AsyncMock()) as mock_save_cart:
            await self.cart_service.increment_quantity("item1")
            self.assertEqual(existing_cart.items[0].quantity, 1)
            mock_save_cart.assert_awaited_once_with(existing_cart)

    async def test_decrement_quantity_existing_item(self) -> None:
        # Mock item and cart setup
        mock_item_to_decrement = CartItem(
            id="item1", title="Item 1", quantity=2, price=10.0
        )
        existing_cart = Cart(
            id=self.cart_id,
            items=[
                mock_item_to_decrement,
                CartItem(id="item2", title="Item 2", quantity=1, price=20.0),
            ],
        )

        with patch.object(
            self.cart_service, "get_cart", return_value=existing_cart
        ), patch.object(self.cart_service, "save_cart", AsyncMock()) as mock_save_cart:
            await self.cart_service.decrement_quantity("item1")
            self.assertEqual(mock_item_to_decrement.quantity, 1)
            mock_save_cart.assert_awaited_once_with(existing_cart)

    async def test_decrement_quantity_item_removed(self) -> None:
        mock_item_to_decrement = CartItem(
            id="item1", title="Item 1", quantity=1, price=10.0
        )
        existing_cart = Cart(
            id=self.cart_id,
            items=[
                mock_item_to_decrement,
                CartItem(id="item2", title="Item 2", quantity=1, price=20.0),
            ],
        )

        with patch.object(
            self.cart_service, "get_cart", return_value=existing_cart
        ), patch.object(self.cart_service, "save_cart", AsyncMock()) as mock_save_cart:
            await self.cart_service.decrement_quantity("item1")
            self.assertEqual(len(existing_cart.items), 1)
            mock_save_cart.assert_awaited_once_with(existing_cart)

    async def test_decrement_quantity_item_not_found(self) -> None:
        # Mock cart setup with no "item1"
        existing_cart = Cart(
            id=self.cart_id,
            items=[CartItem(id="item2", title="Item 2", quantity=1, price=20.0)],
        )

        with patch.object(
            self.cart_service, "get_cart", return_value=existing_cart
        ), patch.object(self.cart_service, "save_cart", AsyncMock()) as mock_save_cart:
            await self.cart_service.decrement_quantity("item1")
            self.assertEqual(len(existing_cart.items), 1)
            mock_save_cart.assert_awaited_once_with(existing_cart)


if __name__ == "__main__":
    unittest.main()
