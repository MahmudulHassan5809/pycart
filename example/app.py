from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pycartnext import CartItem, CartService, DbManager, RedisBackend

# Initialize Cache
DbManager.init(backend=RedisBackend(url="redis://:foobared@127.0.0.1:6379"))

# Initialize FastAPI app
app = FastAPI()

# Mount static files for styles
app.mount("/static", StaticFiles(directory="=/static"), name="static")

# Jinja2 templates directory
templates = Jinja2Templates(directory="=/templates")

# Initialize CartService globally
cart_service = CartService(cart_id="user123-cart")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    """Homepage to display the cart."""
    cart = await cart_service.get_cart()
    return templates.TemplateResponse(
        "cart.html",
        {
            "request": request,
            "cart": cart.model_dump() if cart else None,
            "items": cart.items,
        },
    )


@app.post("/add-item/", response_class=HTMLResponse)
async def add_item(
    _: Request,
    title: str = Form(...),
    price: float = Form(...),
    quantity: int = Form(...),
    discount: float = Form(0.0),
) -> RedirectResponse:
    """Add an item to the cart."""
    item = CartItem(
        id=f"item{quantity}",
        title=title,
        price=price,
        quantity=quantity,
        discount=discount,
    )
    await cart_service.add_item(item)
    return RedirectResponse(url="/", status_code=303)


@app.get("/remove-item/{item_id}/", response_class=HTMLResponse)
async def remove_item(_: Request, item_id: str) -> RedirectResponse:
    """Remove an item from the cart."""
    await cart_service.remove_item(item_id)
    return RedirectResponse(url="/", status_code=303)


@app.get("/increment/{item_id}/", response_class=HTMLResponse)
async def increment_item(_: Request, item_id: str) -> RedirectResponse:
    """Increment item quantity."""
    await cart_service.increment_quantity(item_id)
    return RedirectResponse(url="/", status_code=303)


@app.get("/decrement/{item_id}/", response_class=HTMLResponse)
async def decrement_item(_: Request, item_id: str) -> RedirectResponse:
    """Decrement item quantity."""
    await cart_service.decrement_quantity(item_id)
    return RedirectResponse(url="/", status_code=303)


@app.get("/clear-cart/", response_class=HTMLResponse)
async def clear_cart(_: Request) -> RedirectResponse:
    """Clear the cart."""
    await cart_service.clear_cart()
    return RedirectResponse(url="/", status_code=303)


@app.post("/apply-overall-discount/", response_class=HTMLResponse)
async def apply_overall_discount(
    _: Request, overall_discount: float = Form(0.0)
) -> RedirectResponse:
    """Apply an overall discount to the cart."""
    await cart_service.apply_overall_discount(discount=overall_discount)
    return RedirectResponse(url="/", status_code=303)
