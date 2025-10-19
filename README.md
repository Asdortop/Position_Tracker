# Position Tracker API

A comprehensive portfolio management system built with FastAPI that tracks investment positions, calculates Profit & Loss (P&L), and manages tax lots using FIFO (First In, First Out) methodology.

## 🚀 Features

- **Portfolio Management**: Track investment positions across multiple securities
- **Tax Lot Management**: FIFO-based tax lot tracking for accurate capital gains calculations
- **P&L Calculation**: Real-time unrealized and realized profit/loss calculations
- **Tax Calculations**: Automatic short-term and long-term capital gains tax calculations
- **Price Updates**: Real-time price feed integration for market value calculations
- **RESTful API**: Clean, well-documented REST API endpoints
- **Async Processing**: High-performance async/await architecture
- **Docker Support**: Containerized deployment ready

## 🏗️ Architecture

The system follows a clean architecture pattern with the following layers:

- **API Layer**: FastAPI routes and schemas for request/response handling
- **Service Layer**: Business logic for portfolio and trade processing
- **Data Layer**: SQLAlchemy models and CRUD operations
- **Worker Layer**: Background tasks for price updates and trade processing

## 📋 Prerequisites

- Python 3.10+
- Poetry (for dependency management)
- Docker (optional, for containerized deployment)
- SQLite (default) or PostgreSQL (for production)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd position-tracker-main
```

### 2. Install Dependencies

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install
```

### 3. Environment Setup

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Update the following variables in `.env`:

```env
DATABASE_URL=sqlite+aiosqlite:///./local_test.db
SECRET_KEY=your-secret-key-here
API_V1_STR=/api/v1
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Database Setup

The application uses SQLAlchemy with automatic table creation for development. For production, use Alembic migrations:

```bash
# Initialize Alembic (one-time setup)
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Initial models"

# Apply migration
alembic upgrade head
```

## 🚀 Running the Application

### Local Development

```bash
# Activate virtual environment
poetry shell

# Run the FastAPI application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Docker Deployment

```bash
# Build the Docker image
docker build -t position-tracker .

# Run the container
docker run -p 8000:8000 position-tracker
```

## 📚 API Documentation

### Interactive Documentation

Once the application is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Core Endpoints

#### Portfolio Management

- `GET /api/v1/portfolios/{user_id}/snapshot` - Get complete portfolio snapshot
- `GET /api/v1/taxlots/` - List tax lots with filtering options

#### Trade Simulation (Development)

- `POST /api/v1/simulate/trades` - Process buy/sell trades
- `POST /api/v1/simulate/prices` - Update security prices
- `POST /api/v1/simulate/eod-taxes` - End-of-day tax processing

### Example API Usage

#### 1. Get Portfolio Snapshot

```bash
curl -X GET "http://localhost:8000/api/v1/portfolios/123/snapshot"
```

Response:
```json
{
  "summary": {
    "user_id": 123,
    "total_market_value": 15000.00,
    "total_unrealized_pnl": 2500.00,
    "realized_pnl_ytd": 1200.00,
    "stcg_ytd": 300.00,
    "ltcg_ytd": 150.00,
    "last_updated": "2024-01-15T10:30:00Z"
  },
  "positions": [
    {
      "security_id": "AAPL",
      "quantity": 100.0000,
      "avg_cost_basis": 150.0000,
      "current_price": 175.0000,
      "market_value": 17500.0000,
      "unrealized_pnl": 2500.0000
    }
  ]
}
```

#### 2. Process a Buy Trade

```bash
curl -X POST "http://localhost:8000/api/v1/simulate/trades" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123,
    "security_id": 1,
    "side": "BUY",
    "quantity": 100.0,
    "price": 150.0,
    "timestamp": "2024-01-15T10:00:00Z",
    "charges": 5.0
  }'
```

#### 3. Update Security Price

```bash
curl -X POST "http://localhost:8000/api/v1/simulate/prices" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123,
    "security_id": 1,
    "price": 175.0
  }'
```

## 🏛️ Data Models

### Tax Lot Model

The core data structure for tracking individual purchase lots:

```python
class TaxLot:
    id: int                    # Primary key
    user_id: int              # User identifier
    security_id: int          # Security identifier
    open_date: datetime       # Purchase date
    open_qty: Decimal         # Original quantity purchased
    remaining_qty: Decimal    # Current remaining quantity
    open_price: Decimal       # Purchase price per unit
    close_price: Decimal      # Sale price per unit (if sold)
    charges: Decimal          # Associated fees/charges
    realized_pnl: Decimal     # Realized profit/loss
    stcg: Decimal            # Short-term capital gains tax
    ltcg: Decimal            # Long-term capital gains tax
    status: LotStatus        # OPEN, PARTIAL, or CLOSED
```

### Portfolio Position

Aggregated view of holdings per security:

```python
class PortfolioPosition:
    security_id: str         # Security identifier
    quantity: Decimal        # Total quantity held
    avg_cost_basis: Decimal  # Weighted average cost
    current_price: Decimal   # Latest market price
    market_value: Decimal    # Current market value
    unrealized_pnl: Decimal  # Unrealized profit/loss
```

## 🔄 Business Logic

### FIFO Tax Lot Processing

The system implements First In, First Out (FIFO) methodology for tax lot management:

1. **Buy Orders**: Create new tax lots with OPEN status
2. **Sell Orders**: Process against oldest open lots first
3. **Partial Sales**: Update lot status to PARTIAL
4. **Complete Sales**: Mark lots as CLOSED

### Tax Calculations

- **Short-term Capital Gains**: 25% tax on gains from holdings < 365 days
- **Long-term Capital Gains**: 12.5% tax on gains from holdings ≥ 365 days
- **Charges**: Proportionally allocated to reduce taxable gains

### P&L Calculations

- **Realized P&L**: Calculated at trade time using FIFO
- **Unrealized P&L**: Calculated using current market prices
- **Market Value**: Current quantity × current price

## 🧪 Testing

```bash
# Run tests (when test suite is implemented)
poetry run pytest

# Run with coverage
poetry run pytest --cov=app
```

## 📦 Project Structure

```
position-tracker-main/
├── app/
│   ├── api/v1/              # API routes and schemas
│   │   ├── routes/          # Endpoint definitions
│   │   └── schemas/         # Pydantic models
│   ├── core/                # Core configuration
│   ├── crud/                # Database operations
│   ├── db/                  # Database session management
│   ├── models/              # SQLAlchemy models
│   ├── services/            # Business logic
│   └── workers/             # Background tasks
├── Dockerfile               # Container configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite+aiosqlite:///./local_test.db` |
| `SECRET_KEY` | JWT secret key | Required |
| `API_V1_STR` | API version prefix | `/api/v1` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiry | `30` |

### Database Configuration

The application supports multiple database backends:

- **SQLite**: Default for development (`sqlite+aiosqlite:///./local_test.db`)
- **PostgreSQL**: Recommended for production
- **MySQL**: Supported via SQLAlchemy

## 🚀 Deployment

### Production Considerations

1. **Database**: Use PostgreSQL for production
2. **Authentication**: Implement JWT-based authentication
3. **Security**: Use environment variables for secrets
4. **Monitoring**: Add logging and metrics collection
5. **Scaling**: Consider horizontal scaling with load balancers

### Docker Compose Example

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@db:5432/position_tracker
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=position_tracker
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the code examples in this README

## 🔮 Roadmap

- [ ] Authentication and authorization
- [ ] Real-time price feed integration
- [ ] Advanced reporting and analytics
- [ ] Multi-currency support
- [ ] Mobile application
- [ ] Performance optimizations
- [ ] Comprehensive test suite