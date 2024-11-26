from pydantic import BaseModel


class CartItem(BaseModel):
    id: str
    title: str
    description: str | None = None
    price: float
    quantity: int
    discount: float | None = 0.0
    total: float = 0.0
    total_discount: float = 0.0

    def calculate_totals(self) -> None:
        """Calculate the total and total discount for the item."""
        self.total_discount = self.quantity * (self.discount or 0.0)
        self.total = (self.price * self.quantity) - self.total_discount


class Cart(BaseModel):
    id: str
    items: list[CartItem] = []
    subtotal: float = 0.0
    total_discount: float = 0.0
    grand_total: float = 0.0
    overall_discount: float | None = 0.0

    def calculate_totals(self) -> None:
        """Recalculate the subtotal, total discount, and grand total with global discount."""
        self.subtotal = sum(item.price * item.quantity for item in self.items)
        self.total_discount = sum(item.total_discount for item in self.items)
        self.grand_total = self.subtotal - self.total_discount
        if self.overall_discount:
            self.grand_total -= self.overall_discount
