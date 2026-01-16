import asyncio
import httpx
import pytest


def test_concurrent_purchase_creates_duplicate_orders(api_url):
    """
    Test that verifies the system behavior under concurrent purchases.
    """
    print("\n" + "=" * 60)
    print("FLASH SALE CONCURRENT PURCHASE TEST")
    print("=" * 60)

    with httpx.Client(timeout=30.0) as client:
        # Step 1: Reset the system
        print("\n[1] Resetting system...")
        reset_response = client.post(f"{api_url}/api/reset")
        assert reset_response.status_code == 200
        reset_data = reset_response.json()
        print(f"    Reset complete: quantity_reset_to={reset_data['quantity_reset_to']}")

        # Step 2: Verify initial state
        print("\n[2] Verifying initial state...")
        product_response = client.get(f"{api_url}/api/products")
        assert product_response.status_code == 200
        product = product_response.json()
        product_id = product["id"]
        print(f"    Product: {product['title']}")
        print(f"    Initial stock: {product['quantity']}")
        assert product["quantity"] == 1, "Initial stock should be 1"

        # Step 3: Send concurrent purchase requests
        print("\n[3] Sending concurrent purchase requests...")
        print("    Request 1 -> nginx -> backend-1")
        print("    Request 2 -> nginx -> backend-2 (50ms delay)")

        async def send_concurrent_orders():
            async with httpx.AsyncClient(timeout=30.0) as client:
                request1 = client.post(
                    f"{api_url}/api/orders",
                    json={"product_id": product_id}
                )

                request2 = client.post(
                    f"{api_url}/api/orders",
                    json={"product_id": product_id}
                )

                results = await asyncio.gather(request1, request2, return_exceptions=True)
                return results

        results = asyncio.run(send_concurrent_orders())

        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                print(f"    Request {i}: Failed with exception: {result}")
            elif result.status_code == 200:
                backend = result.headers.get("X-Backend", "unknown")
                print(f"    Request {i}: Order created successfully (handled by {backend})")
            else:
                print(f"    Request {i}: Failed with status {result.status_code}")

        # Step 4: Verify final state
        print("\n[4] Verifying final state...")

        orders_response = client.get(f"{api_url}/api/orders")
        assert orders_response.status_code == 200
        orders = orders_response.json()
        print(f"    Total orders created: {len(orders)}")

        product_response = client.get(f"{api_url}/api/products")
        assert product_response.status_code == 200
        product = product_response.json()
        print(f"    Final stock: {product['quantity']}")

        # Step 5: Assert the expected behavior
        print("\n[5] Validating results...")
        print("=" * 60)

        assert len(orders) == 2, f"Expected 2 orders, got {len(orders)}"
        print("    PASS: 2 orders were created from 1 available item")

        assert product["quantity"] == -1, f"Expected stock=-1 (oversold), got {product['quantity']}"
        print("    PASS: Stock is -1 (oversold)")

        print("\n    BUG CONFIRMED: System allows overselling!")
        print("=" * 60)
