# Position Tracker API - Project Structure

## 🏗️ **Clean, Modular Architecture**

This document explains the improved project structure that follows best practices for maintainability, scalability, and code organization.

## 📁 **Directory Structure**

```
position-tracker-main/
├── app/                           # Main application package
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   │
│   ├── api/                       # API Layer
│   │   ├── __init__.py
│   │   ├── v1/                    # API Version 1
│   │   │   ├── __init__.py
│   │   │   ├── dependencies.py    # API dependencies (DB, Auth)
│   │   │   ├── routes/            # Route handlers
│   │   │   │   ├── __init__.py
│   │   │   │   ├── portfolios.py  # Portfolio endpoints
│   │   │   │   ├── simulations.py # Simulation endpoints
│   │   │   │   └── taxlots.py     # Tax lot endpoints
│   │   │   └── schemas/           # Request/Response schemas
│   │   │       ├── __init__.py
│   │   │       ├── portfolio.py   # Portfolio schemas
│   │   │       ├── tax_lot.py     # Tax lot schemas
│   │   │       └── trade.py       # Trade schemas
│   │   └── middleware/            # Custom middleware
│   │       └── __init__.py
│   │
│   ├── core/                      # Core Configuration
│   │   ├── __init__.py
│   │   ├── config.py              # Application configuration
│   │   ├── exceptions.py          # Custom exceptions
│   │   └── security.py            # Security utilities
│   │
│   ├── database/                  # Database Layer
│   │   ├── __init__.py
│   │   ├── connection.py          # DB connection & session management
│   │   ├── models/                # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── portfolio.py       # Portfolio model
│   │   │   ├── price.py           # Price model
│   │   │   └── tax_lot.py         # Tax lot model
│   │   └── migrations/            # Database migrations
│   │       └── __init__.py
│   │
│   ├── services/                  # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── portfolio_service.py   # Portfolio management logic
│   │   ├── processing_service.py  # Trade processing logic
│   │   ├── tax_service.py         # Tax calculation logic
│   │   └── price_service.py       # Price management logic
│   │
│   ├── repositories/              # Data Access Layer
│   │   ├── __init__.py
│   │   ├── base.py                # Base repository class
│   │   ├── crud_operations.py     # CRUD operations
│   │   └── crud_portfolio.py      # Portfolio-specific CRUD
│   │
│   ├── utils/                     # Utility Functions
│   │   ├── __init__.py
│   │   ├── datetime_utils.py      # Date/time helper functions
│   │   ├── calculation_utils.py   # Mathematical calculations
│   │   └── validation_utils.py    # Data validation functions
│   │
│   └── workers/                   # Background Workers
│       ├── __init__.py
│       ├── price_updater.py       # Price update worker
│       └── trade_consumer.py      # Trade processing worker
│
├── tests/                         # Test Suite
│   ├── test_api_endpoints.py      # API endpoint tests
│   ├── test_edge_cases.py         # Edge case tests
│   ├── test_fifo_scenarios.py     # FIFO scenario tests
│   ├── test_performance.py        # Performance tests
│   └── test_processing_service.py # Service layer tests
│
├── docker-compose.yml             # Development Docker setup
├── docker-compose.prod.yml        # Production Docker setup
├── Dockerfile                     # Application container
├── init-db.sql                    # Database initialization
├── nginx.conf                     # Web server configuration
├── requirements.txt               # Python dependencies
├── start.sh                       # Linux/Mac startup script
├── start.bat                      # Windows startup script
├── README.md                      # Main documentation
├── SRS.md                         # Requirements specification
├── EVENT_MASTER_INTEGRATION.md    # Event Master integration docs
├── DOCKER_SETUP.md                # Docker setup guide
└── PROJECT_STRUCTURE.md           # This file
```

## 🎯 **Architecture Principles**

### **1. Separation of Concerns**
- **API Layer**: Handles HTTP requests/responses, validation, routing
- **Service Layer**: Contains business logic and orchestration
- **Repository Layer**: Manages data access and persistence
- **Database Layer**: Models and connection management
- **Utils Layer**: Reusable utility functions

### **2. Modular Design**
- Each layer has a specific responsibility
- Clear interfaces between layers
- Easy to test individual components
- Easy to modify without affecting other parts

### **3. Scalability**
- Easy to add new features
- Easy to add new API versions
- Easy to add new database models
- Easy to add new services

## 📋 **Layer Responsibilities**

### **API Layer (`app/api/`)**
- **Routes**: Define HTTP endpoints and handle requests
- **Schemas**: Validate request/response data using Pydantic
- **Dependencies**: Provide database sessions, authentication, etc.
- **Middleware**: Cross-cutting concerns (logging, CORS, etc.)

### **Service Layer (`app/services/`)**
- **Business Logic**: Core application logic
- **Orchestration**: Coordinate between different services
- **Validation**: Business rule validation
- **Processing**: Complex operations and calculations

### **Repository Layer (`app/repositories/`)**
- **Data Access**: Database operations
- **Query Building**: Complex database queries
- **Data Mapping**: Convert between database and domain objects
- **Transaction Management**: Handle database transactions

### **Database Layer (`app/database/`)**
- **Models**: SQLAlchemy ORM models
- **Connection**: Database connection and session management
- **Migrations**: Database schema changes

### **Utils Layer (`app/utils/`)**
- **Helper Functions**: Reusable utility functions
- **Calculations**: Mathematical operations
- **Validation**: Data validation helpers
- **Formatting**: Data formatting utilities

## 🔧 **Key Improvements**

### **1. Better Organization**
- Related files are grouped together
- Clear naming conventions
- Easy to find specific functionality

### **2. Enhanced Maintainability**
- Single responsibility principle
- Clear separation of concerns
- Easy to modify individual components

### **3. Improved Testability**
- Each layer can be tested independently
- Clear interfaces for mocking
- Isolated business logic

### **4. Better Scalability**
- Easy to add new features
- Easy to add new API versions
- Easy to add new database models

### **5. Cleaner Imports**
- Clear import paths
- No circular dependencies
- Easy to understand dependencies

## 🚀 **Usage Examples**

### **Adding a New Service**
```python
# app/services/new_service.py
class NewService:
    def __init__(self):
        self.repository = SomeRepository()
    
    async def do_something(self, data):
        # Business logic here
        return await self.repository.save(data)
```

### **Adding a New Repository**
```python
# app/repositories/new_repository.py
class NewRepository:
    async def create(self, db: AsyncSession, data):
        # Database operations here
        pass
```

### **Adding a New API Endpoint**
```python
# app/api/v1/routes/new_routes.py
@router.post("/new-endpoint")
async def new_endpoint(
    data: NewSchema,
    db: AsyncSession = Depends(get_db)
):
    service = NewService()
    return await service.process(data)
```

## 📚 **Documentation**

- **README.md**: Main project documentation
- **SRS.md**: Software Requirements Specification
- **EVENT_MASTER_INTEGRATION.md**: Event Master integration guide
- **DOCKER_SETUP.md**: Docker setup and deployment guide
- **PROJECT_STRUCTURE.md**: This architecture guide

## 🧪 **Testing**

The project includes comprehensive tests:
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **Edge Case Tests**: Boundary condition testing
- **Performance Tests**: Load and stress testing

## 🔄 **Migration Notes**

The project has been restructured from the original structure:
- `app/db/` → `app/database/`
- `app/models/` → `app/database/models/`
- `app/crud/` → `app/repositories/`
- Added `app/utils/` for utility functions
- Added `app/services/tax_service.py` and `app/services/price_service.py`
- Added `app/core/security.py` for security utilities

All imports have been updated to reflect the new structure.
