# DETONADO: Flash Sale Race Condition Fix

This guide walks you through identifying and fixing the data integrity issue in the Flash Sale application.

---

## Learning Objective

**Primary Skill:** Database concurrency control with pessimistic locking

By completing this exercise, you will:
- Understand the "check-then-act" race condition pattern (TOCTOU)
- Learn how concurrent requests can bypass application-level validation
- Implement pessimistic locking using SQLAlchemy's `with_for_update()`
- Recognize timing evidence in duplicate records

---

## Problem Identification

### Symptoms

When you click "Buy Now" on a product with 1 item in stock:
- Two orders appear in the orders list instead of one
- The stock shows -1 (negative inventory)
- Both orders have timestamps within milliseconds of each other

### Measuring the Problem

1. Start the application: `make run`
2. Open http://localhost:3000
3. Verify stock shows "1 available"
4. Click "Buy Now" once
5. Observe the results

**Expected Observation:** Two orders created, stock at -1, timestamps ~50-100ms apart.

### Initial Questions

- Why does a single click create two orders?
- How can inventory go negative if we check stock before creating an order?
- What does the timing between orders tell us?

---

## Understanding the Problem: Race Conditions

### What Is a Race Condition?

A race condition occurs when the behavior of a system depends on the relative timing of events, particularly when multiple processes access shared data concurrently. The outcome becomes unpredictable and often incorrect.

**TOCTOU (Time-of-Check to Time-of-Use):** A specific type of race condition where there's a gap between checking a condition and acting on it. Another process can change the state between these two operations.

### The Current Architecture

```
Request A (Backend 1)              Request B (Backend 2)
─────────────────────              ─────────────────────
1. SELECT quantity
   → sees 1                        1. SELECT quantity
                                      → sees 1
2. Check: 1 > 0? Yes
                                   2. Check: 1 > 0? Yes
3. INSERT order
                                   3. INSERT order
4. UPDATE quantity - 1
   → quantity = 0                  4. UPDATE quantity - 1
                                      → quantity = -1
```

**The Problem:** Both requests read the same initial state before either commits changes.

### Why This Happens

The purchase logic in `backend/app/services/order_service.py`:

```python
def create_order(self, product_id: UUID) -> Order:
    # Step 1: Read current quantity (no lock)
    product = self.product_repo.get_by_id(product_id)

    # Step 2: Check availability
    if product.quantity <= 0:
        raise HTTPException(status_code=400, detail="Out of stock")

    # Gap: Another request can pass the check here!

    # Step 3: Create order
    order = self.order_repo.create(product_id)

    # Step 4: Decrement quantity
    self.product_repo.decrement_quantity(product_id)

    return order
```

The `get_by_id()` query doesn't lock the row, allowing concurrent reads of the same value.

### What We Need

```
Request A (Backend 1)              Request B (Backend 2)
─────────────────────              ─────────────────────
1. SELECT ... FOR UPDATE
   → locks row, sees 1             1. SELECT ... FOR UPDATE
                                      → BLOCKED (waiting for lock)
2. Check: 1 > 0? Yes
3. INSERT order
4. UPDATE quantity - 1
5. COMMIT
   → releases lock                    → lock acquired, sees 0
                                   2. Check: 0 > 0? No
                                   3. Reject: "Out of stock"
```

### Further Reading

If you want to learn more about database locking:

- [Lazy Bird Blog - Database Locking](https://lazybird.com.br/blog/2026-01-19-lazy-bird---database-locking/)
- [PostgreSQL Explicit Locking](https://www.postgresql.org/docs/current/explicit-locking.html) - Official documentation on row-level locks
- [SQLAlchemy Query.with_for_update()](https://docs.sqlalchemy.org/en/20/orm/queryguide/query.html#sqlalchemy.orm.Query.with_for_update) - ORM-level locking API
- [Martin Kleppmann - Designing Data-Intensive Applications](https://dataintensive.net/) - Chapter 7 covers transactions and concurrency

---

## Diagnosis and Root Cause Analysis

### Step 1: Observe the Behavior

1. Reset the system (click Reset button or `POST /api/reset`)
2. Click "Buy Now"
3. Note: Two orders, stock at -1

### Step 2: Examine the Timestamps

The orders have timestamps milliseconds apart. This indicates:
- Both requests started processing before either completed
- The system is receiving concurrent requests

### Step 3: Trace the Code Path

Look at the order creation service:

**File:** `backend/app/services/order_service.py`

```python
product = self.product_repo.get_by_id(product_id)  # No lock here

if product.quantity <= 0:
    raise HTTPException(status_code=400, detail="Out of stock")

# Window for race condition exists here

order = self.order_repo.create(product_id)
self.product_repo.decrement_quantity(product_id)
```

### Step 4: Identify the Root Cause

**Root Cause:** The `get_by_id()` method performs a regular SELECT without acquiring a row lock. When two concurrent requests execute this query, both see the same quantity (1) and both proceed to create orders.

**File:** `backend/app/repositories/product_repository.py`

```python
def get_by_id(self, product_id: UUID) -> Product | None:
    return self.db.query(Product).filter(Product.id == product_id).first()
```

This is a standard SELECT query - it doesn't prevent other transactions from reading the same row.

---

## Solution Implementation

We'll use pessimistic locking with `SELECT ... FOR UPDATE` to ensure only one transaction can process the product at a time.

### Step 1: Add a Locking Method to the Repository

**File:** `backend/app/repositories/product_repository.py`

Add this new method:

```python
def get_by_id_for_update(self, product_id: UUID) -> Product | None:
    """Retrieve a product by its ID with row-level lock."""
    return self.db.query(Product).filter(Product.id == product_id).with_for_update().first()
```

### Step 2: Update the Service to Use Locking

**File:** `backend/app/services/order_service.py`

Find this line:
```python
product = self.product_repo.get_by_id(product_id)
```

Replace with:
```python
product = self.product_repo.get_by_id_for_update(product_id)
```

### Understanding the Implementation

1. **`with_for_update()`** adds `FOR UPDATE` to the SELECT query, acquiring an exclusive row lock
2. **Blocking behavior:** The second transaction waits until the first commits or rolls back
3. **Fresh read:** When the lock is acquired, the second transaction sees the updated quantity
4. **Automatic release:** The lock is released when the database transaction commits or rolls back

**Transaction Boundaries:** In this implementation, the session uses `autocommit=False` (see `backend/app/core/database.py`), meaning a transaction starts implicitly with the first query and ends with the explicit `db.commit()` call in the service. The lock is held for the duration of this database transaction, not the HTTP request. If using auto-commit or managing transactions differently, lock behavior may vary.

---

## Verification and Expected Results

### Step 1: Restart the Backend

After making changes, rebuild the containers:

```bash
make build
```

### Step 2: Test the Fix

1. Open http://localhost:3000
2. Click Reset to restore stock to 1
3. Click "Buy Now"

**Expected Result:**
- Only **1 order** is created
- Stock shows **0** (not negative)
- One of the concurrent requests receives an "Out of stock" error (handled gracefully)

### Performance Comparison

| Metric | Before Fix | After Fix |
|--------|-----------|-----------|
| Orders created | 2 | 1 |
| Final stock | -1 | 0 |
| Data integrity | Violated | Maintained |

---

## Success Criteria

You've successfully fixed the race condition when:

- Clicking "Buy Now" creates exactly **1 order** (not 2)
- Stock shows **0** after purchase (not negative)
- The fix works consistently across multiple test runs

---

## Production Considerations

### Moving Beyond This Implementation

**1. Lock Timeouts**

In production, configure lock wait timeouts to prevent indefinite blocking:

```python
# SQLAlchemy with_for_update options
.with_for_update(nowait=True)  # Fail immediately if locked
.with_for_update(skip_locked=True)  # Skip locked rows (for batch processing)
```

**2. Optimistic Locking Alternative**

For high-concurrency scenarios, consider optimistic locking with version columns:

```python
class Product(Base):
    version = Column(Integer, default=1)

# Update only if version matches
UPDATE products SET quantity = quantity - 1, version = version + 1
WHERE id = ? AND version = ?
```

**3. Database Constraints**

Add a CHECK constraint as a safety net:

```sql
ALTER TABLE products ADD CONSTRAINT positive_quantity CHECK (quantity >= 0);
```

Note: This doesn't prevent the race condition but ensures data integrity at the database level.

**4. Idempotency Keys**

For payment-critical operations, use idempotency keys to prevent duplicate processing:

```python
@router.post("/orders")
def create_order(request: OrderRequest, idempotency_key: str = Header(...)):
    # Check if this key was already processed
    existing = get_order_by_idempotency_key(idempotency_key)
    if existing:
        return existing
    # ... proceed with order creation
```

---

## Key Takeaways

**What You Learned:**
- Race conditions occur when concurrent operations access shared state without proper synchronization
- The "check-then-act" pattern is inherently unsafe without locking
- Pessimistic locking with `SELECT ... FOR UPDATE` serializes access to critical resources
- Timestamp analysis can reveal evidence of concurrent execution

**When to Use Pessimistic Locking:**
- Inventory management and stock control
- Reservation systems (seats, appointments)
- Financial transactions requiring strict consistency
- Any operation where overselling has significant consequences

**When NOT to Use This Pattern:**
- High-read, low-write scenarios (use optimistic locking instead)
- When lock contention would significantly impact throughput
- Distributed systems where database locks don't span services

---

> "Oh, you actually fixed it? Nice... I mean, I knew you could do it. That's why I picked you, obviously."
>
> "Pessimistic locking, huh? Yeah, I was gonna suggest that... eventually. Anyway, thanks for the help. I'm gonna go back to my nap now. But hey, if I find another bug, I know who to call..."

**Congratulations!** You've successfully fixed the flash sale race condition. This pessimistic locking pattern applies to any scenario where concurrent requests must not exceed a limited resource.
