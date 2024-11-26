# pycartnext

pycartnext is a simple shopping cart service built using FastAPI and Redis for caching. It provides basic cart management functionalities like adding/removing items, modifying quantities, and applying discounts.

## Features

- Add, remove, and modify items in the shopping cart
- Apply discounts to the cart
- Use Redis for caching cart data
- Easy-to-use service interface for managing the cart

## Installation

### Prerequisites

Ensure you have Python 3.10+ and Redis installed.

### Steps to install



1. Install dependencies using Poetry:
   ```bash
   pip install pycartnext
   ```

2. Set up Redis:
   - Install Redis locally or use a Redis cloud service.
   - Make sure Redis is running on `redis://127.0.0.1:6379`.

3. Example:
   - Check example folder how to use.

## Usage

### CartService

The `CartService` class handles all cart-related operations. Here's how you can use it:

1. **Create a CartService instance**:
   ```python
   from cart_service import CartService

   cart_service = CartService(redis_url="redis://127.0.0.1:6379")
   ```

2. **Add an item to the cart**:
   ```python
   cart_service.add_item(title="Product A", price=100.0, quantity=2)
   ```

3. **Remove an item from the cart**:
   ```python
   cart_service.remove_item(item_id=1)
   ```

4. **Increment item quantity**:
   ```python
   cart_service.increment_item_quantity(item_id=1)
   ```

5. **Decrement item quantity**:
   ```python
   cart_service.decrement_item_quantity(item_id=1)
   ```

6. **Apply a discount to the cart**:
   ```python
   cart_service.apply_discount(discount_percentage=10)
   ```

7. **Clear the entire cart**:
   ```python
   cart_service.clear_cart()
   ```

8. **View the current cart**:
   ```python
   cart = cart_service.get_cart()
   print(cart)
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
