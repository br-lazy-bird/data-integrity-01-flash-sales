# Lazy Bird: Flash Sale System

An educational project for learning data integrity patterns through hands-on practice.

---

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- 2GB+ available RAM
- Ports 3000, 8000, and 5432 available

### Setup

This project includes a `.env.development` file with development configuration. Copy this file to `.env` before running the system:

```bash
cp .env.development .env
```

These settings are for **local development only** and contain no sensitive data. In production applications, always use proper secret management and never commit credentials to version control.

```bash
# Start the system
make run
```

The system will:
- Start PostgreSQL database
- Seed the product catalog (1 book in stock)
- Launch two FastAPI backend instances
- Start nginx load balancer
- Start React frontend

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Database: localhost:5432

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         React Frontend                          │
│                      (http://localhost:3000)                    │
│                   Flash sale product display                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP Request
                             │ POST /api/orders
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      nginx Load Balancer                        │
│                      (http://localhost:8000)                    │
│                   Round-robin distribution                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
┌─────────────────────────┐   ┌─────────────────────────┐
│     Backend API 1       │   │     Backend API 2       │
│       (FastAPI)         │   │       (FastAPI)         │
└────────────┬────────────┘   └────────────┬────────────┘
              │                             │
              └──────────────┬──────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         PostgreSQL                              │
│                      (localhost:5432)                           │
│                   Products & Orders tables                      │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Frontend:** React 18 with TypeScript

**Backend:** FastAPI (Python) with SQLAlchemy ORM

**Database:** PostgreSQL 15 with millisecond timestamp precision

**Infrastructure:**
- nginx for load balancing (round-robin)
- Docker Compose for easy setup
- Hot-reload enabled for development
- Isolated network environment

---

## Meet the Lazy Bird

> The Lazy Bird is a peculiar creature. It has an exceptional talent for catching bugs... but absolutely zero motivation to fix them. You'll find it wandering around codebases, spotting issues, and then immediately looking for someone else to do the hard work.
>
> Today, it found you.

---

## The Problem

> "Hey... so we launched this flash sale thing today, right? Limited edition book, only 1 in stock. Marketing was hyped, everyone was ready..."
>
> "But then customers started complaining. They're saying the system sold the same book twice. Stock went negative. The finance team is losing it."
>
> "I looked at the database and... yeah, two orders, one book. The timestamps are like milliseconds apart. Something's definitely off, but I promised myself a coffee break 10 minutes ago, so... could you figure this out? Thanks!"

**Your Mission:**
1. Investigate why a single purchase creates duplicate orders
2. Diagnose the root cause using appropriate diagnostic tools
3. Implement the fix
4. Verify that the problem is resolved

**Important:** Do NOT remove the second backend instance or disable the load balancer. The multi-instance architecture is intentional to simulate real-world deployments. The fix should work WITH this architecture, not around it.

---

## Success Criteria

You'll know you've successfully fixed the system when:

- Clicking "Buy Now" creates exactly **1 order**
- Stock shows **0** (not negative)
- The fix works consistently across multiple attempts
- The solution doesn't require removing backend instances

Use the Reset button to restore the system to its initial state (1 item in stock, no orders) between attempts.

---

## How to Use the System

### Frontend Interface

**Making a Purchase:**
1. Open http://localhost:3000
2. View the product: "The State and Revolution" by V.I. Lenin ($9.99)
3. Note the current stock (starts at 1)
4. Click "Buy Now"
5. Observe the orders list and final stock count

**Resetting the System:**
- Click the "Reset" button to clear all orders and restore stock to 1

### API Endpoints

**Products:**
- `GET /api/products` - Get product with current stock

**Orders:**
- `POST /api/orders` - Create order (body: `{"product_id": "uuid"}`)
- `GET /api/orders` - List all orders

**System:**
- `POST /api/reset` - Reset system state
- `GET /health` - Health check

### Database Access

**Using psql:**
```bash
make db-shell
```

**Connection Details:**
- Host: localhost
- Port: 5432
- Database: flash_sale
- Username: lazybird_dev
- Password: lazybird_password

---

## Running Tests

The project includes automated integration tests that verify the system behavior.

**Run tests (fast - uses cached images):**
```bash
make test
```

**Rebuild and test (after code changes):**
```bash
make test-build
```

Tests run in an isolated environment with a separate test database on port 5433.

---

## Available Commands

```bash
make help        # Show all available commands
make run         # Start the application
make build       # Build and start the application
make stop        # Stop the application
make clean       # Stop and remove all containers and volumes
make logs        # Show application logs
make db-shell    # Open PostgreSQL shell
make test        # Run integration tests
make test-build  # Rebuild and run tests
```

---

## Documentation

For detailed diagnostic guidance and step-by-step fix instructions, see the [DETONADO Guide](./DETONADO.md).

---

Ready to start? Run `make run` and dive in!
