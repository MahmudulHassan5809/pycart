from .db import DbManager
from .schemas import Cart, CartItem


class CartService:
    """
    Service class for managing a shopping cart.

    This class provides methods to retrieve, update, and manage items within a user's cart,
    as well as apply discounts and clear the cart. It interacts with the cache to store and retrieve cart data.
    """

    def __init__(self, cart_id: str) -> None:
        """
        Initializes the CartService with a cart ID.

        Args:
            cart_id (str): Unique identifier for the cart.
        """
        self.cart_id = cart_id

    async def get_cart(self) -> Cart:
        """
        Retrieves the cart from the cache. If the cart does not exist, a new empty cart is created.

        Returns:
            Cart: The cart object.
        """
        cart_data = await DbManager.get(self.cart_id)

        if not cart_data:
            return Cart(id=self.cart_id)
        try:
            return Cart(**cart_data)
        except ValueError:
            return Cart(id=self.cart_id)

    async def save_cart(self, cart: Cart) -> None:
        """
        Saves the cart object to the cache.

        Args:
            cart (Cart): The cart object to be saved.
        """
        await DbManager.set(self.cart_id, cart.model_dump())

    async def add_item(self, item: CartItem) -> None:
        """
        Adds an item to the cart or updates the quantity if the item already exists in the cart.

        Args:
            item (CartItem): The item to be added or updated.
        """
        cart = await self.get_cart()

        for cart_item in cart.items:
            if cart_item.id == item.id:
                cart_item.quantity += item.quantity
                cart_item.calculate_totals()
                break
        else:
            item.calculate_totals()
            cart.items.append(item)

        cart.calculate_totals()
        await self.save_cart(cart)

    async def remove_item(self, item_id: str) -> None:
        """
        Removes an item from the cart based on its ID.

        Args:
            item_id (str): The ID of the item to be removed.
        """
        cart = await self.get_cart()
        cart.items = [item for item in cart.items if item.id != item_id]
        cart.calculate_totals()
        await self.save_cart(cart)

    async def increment_quantity(self, item_id: str) -> None:
        """
        Increments the quantity of a specific item in the cart by 1.

        Args:
            item_id (str): The ID of the item whose quantity is to be incremented.
        """
        cart = await self.get_cart()
        for item in cart.items:
            if item.id == item_id:
                item.quantity += 1
                item.calculate_totals()
                break
        cart.calculate_totals()
        await self.save_cart(cart)

    async def decrement_quantity(self, item_id: str) -> None:
        """
        Decrements the quantity of a specific item in the cart by 1. If the quantity is 1, the item is removed.

        Args:
            item_id (str): The ID of the item whose quantity is to be decremented.
        """
        cart = await self.get_cart()
        for item in cart.items:
            if item.id == item_id:
                if item.quantity > 1:
                    item.quantity -= 1
                    item.calculate_totals()
                else:
                    cart.items.remove(item)
                break
        cart.calculate_totals()
        await self.save_cart(cart)

    async def apply_overall_discount(self, discount: float) -> None:
        """
        Applies an overall discount to the cart.

        Args:
            discount (float): The discount percentage to apply to the cart.
        """
        cart = await self.get_cart()
        cart.overall_discount = discount
        cart.calculate_totals()
        await self.save_cart(cart)

    async def clear_cart(self) -> None:
        """
        Clears all items from the cart and resets it to an empty state.

        The cart is saved after being cleared.
        """
        cart = Cart(id=self.cart_id)
        await self.save_cart(cart)
