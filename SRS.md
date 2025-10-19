# Software Requirements Specification (SRS)
## Position Tracker API System

**Document Version:** 1.0  
**Date:** January 2024  
**Prepared by:** Development Team  

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [System Features](#3-system-features)
4. [External Interface Requirements](#4-external-interface-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [System Architecture](#6-system-architecture)
7. [Data Models](#7-data-models)
8. [API Specifications](#8-api-specifications)
9. [Database Design](#9-database-design)
10. [Security Requirements](#10-security-requirements)
11. [Performance Requirements](#11-performance-requirements)
12. [Deployment Requirements](#12-deployment-requirements)

---

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) document describes the functional and non-functional requirements for the Position Tracker API system. The system is designed to provide comprehensive portfolio management capabilities, including position tracking, profit/loss calculations, and tax lot management using FIFO methodology.

### 1.2 Scope

The Position Tracker API is a backend service that:
- Tracks investment positions across multiple securities
- Manages tax lots using First In, First Out (FIFO) methodology
- Calculates realized and unrealized profit/loss
- Computes capital gains taxes (short-term and long-term)
- Provides real-time portfolio snapshots
- Supports price updates and trade processing

### 1.3 Definitions, Acronyms, and Abbreviations

- **API**: Application Programming Interface
- **FIFO**: First In, First Out
- **P&L**: Profit and Loss
- **STCG**: Short-Term Capital Gains
- **LTCG**: Long-Term Capital Gains
- **CRUD**: Create, Read, Update, Delete
- **REST**: Representational State Transfer
- **JWT**: JSON Web Token
- **SQL**: Structured Query Language

### 1.4 References

- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- Pydantic Documentation: https://pydantic-docs.helpmanual.io/
- Python 3.10+ Documentation: https://docs.python.org/3/

### 1.5 Overview

This document is organized into sections covering system overview, functional requirements, technical specifications, and implementation details. The system is built using modern Python technologies with FastAPI as the web framework and SQLAlchemy for database operations.

---

## 2. Overall Description

### 2.1 Product Perspective

The Position Tracker API is a standalone backend service that can be integrated with:
- Frontend web applications
- Mobile applications
- Third-party trading platforms
- Portfolio management systems
- Tax reporting tools

### 2.2 Product Functions

The system provides the following core functions:

1. **Portfolio Management**
   - Track investment positions
   - Calculate portfolio values
   - Generate portfolio snapshots

2. **Trade Processing**
   - Process buy and sell orders
   - Manage tax lots using FIFO
   - Calculate realized P&L

3. **Tax Management**
   - Compute capital gains taxes
   - Distinguish between short-term and long-term gains
   - Track tax obligations

4. **Price Management**
   - Update security prices
   - Calculate unrealized P&L
   - Maintain price history

### 2.3 User Classes and Characteristics

**Primary Users:**
- **Portfolio Managers**: Need comprehensive portfolio views and analytics
- **Traders**: Require real-time position tracking and P&L calculations
- **Tax Professionals**: Need accurate tax lot tracking and gain calculations
- **Individual Investors**: Want simple portfolio management tools

**Secondary Users:**
- **System Administrators**: Manage system configuration and monitoring
- **API Consumers**: Integrate with external systems

### 2.4 Operating Environment

**Development Environment:**
- Python 3.10+
- SQLite database
- Local development server

**Production Environment:**
- Linux/Windows servers
- PostgreSQL database
- Docker containers
- Load balancers

### 2.5 Design and Implementation Constraints

- Must use Python 3.10+ for compatibility
- Database must support ACID transactions
- API must follow RESTful principles
- Must support async/await patterns for performance
- Must be containerizable with Docker

### 2.6 Assumptions and Dependencies

**Assumptions:**
- Users have valid authentication credentials
- Price feeds provide accurate and timely data
- Trade data is complete and valid
- Database is available and accessible

**Dependencies:**
- FastAPI framework
- SQLAlchemy ORM
- Pydantic for data validation
- Database server (SQLite/PostgreSQL)
- Python runtime environment

---

## 3. System Features

### 3.1 Portfolio Management

#### 3.1.1 Portfolio Snapshot
**Description:** Generate comprehensive portfolio snapshots including positions and P&L summaries.

**Input:** User ID
**Output:** Portfolio snapshot with positions and summary data

**Processing:**
1. Query all open tax lots for the user
2. Aggregate positions by security
3. Calculate market values and unrealized P&L
4. Compute portfolio summary statistics

**Business Rules:**
- Only include lots with remaining quantity > 0
- Use current market prices for valuation
- Calculate weighted average cost basis

#### 3.1.2 Position Tracking
**Description:** Track individual security positions across multiple tax lots.

**Input:** User ID, Security ID (optional)
**Output:** List of positions with quantities and values

**Processing:**
1. Aggregate tax lots by security
2. Calculate total quantities and cost basis
3. Apply current market prices
4. Compute unrealized P&L

### 3.2 Trade Processing

#### 3.2.1 Buy Order Processing
**Description:** Process buy orders and create new tax lots.

**Input:** Trade data (user_id, security_id, quantity, price, timestamp, charges)
**Output:** Confirmation of trade processing

**Processing:**
1. Validate trade data
2. Create new tax lot with OPEN status
3. Record purchase details
4. Update portfolio summary

**Business Rules:**
- Quantity must be positive
- Price must be positive
- Timestamp must be valid
- Charges are optional but must be non-negative

#### 3.2.2 Sell Order Processing
**Description:** Process sell orders using FIFO methodology.

**Input:** Trade data (user_id, security_id, quantity, price, timestamp, charges)
**Output:** Confirmation of trade processing

**Processing:**
1. Validate trade data
2. Retrieve open tax lots in FIFO order
3. Allocate sell quantity across lots
4. Calculate realized P&L and taxes
5. Update lot statuses

**Business Rules:**
- Must have sufficient quantity to sell
- Process lots in chronological order (FIFO)
- Calculate holding period for tax purposes
- Apply proportional charges

### 3.3 Tax Management

#### 3.3.1 Capital Gains Calculation
**Description:** Calculate short-term and long-term capital gains.

**Input:** Trade data and lot information
**Output:** Tax calculations (STCG, LTCG)

**Processing:**
1. Calculate gross gain (sell_price - buy_price) × quantity
2. Subtract proportional charges
3. Determine holding period
4. Apply appropriate tax rate

**Business Rules:**
- Short-term: < 365 days, 25% tax rate
- Long-term: ≥ 365 days, 12.5% tax rate
- Only tax positive gains
- Charges reduce taxable amount

#### 3.3.2 Tax Lot Status Management
**Description:** Manage tax lot statuses based on remaining quantities.

**Input:** Lot updates from trade processing
**Output:** Updated lot statuses

**Processing:**
1. Update remaining quantities
2. Calculate close quantities
3. Determine new status
4. Record close dates and prices

**Business Rules:**
- OPEN: remaining_qty = open_qty
- PARTIAL: 0 < remaining_qty < open_qty
- CLOSED: remaining_qty = 0

### 3.4 Price Management

#### 3.4.1 Price Updates
**Description:** Update security prices and recalculate unrealized P&L.

**Input:** Security ID, new price
**Output:** Confirmation of price update

**Processing:**
1. Validate price data
2. Update price in database
3. Trigger P&L recalculation
4. Update portfolio values

**Business Rules:**
- Price must be positive
- Price updates are immediate
- Affects all users holding the security

---

## 4. External Interface Requirements

### 4.1 User Interfaces

**API Endpoints:**
- RESTful HTTP endpoints
- JSON request/response format
- Swagger/OpenAPI documentation
- Error handling with appropriate HTTP status codes

### 4.2 Hardware Interfaces

**Minimum Requirements:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 10GB
- Network: 100 Mbps

**Recommended Requirements:**
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 50GB+ SSD
- Network: 1 Gbps

### 4.3 Software Interfaces

**Database:**
- SQLite (development)
- PostgreSQL (production)
- MySQL (supported)

**External Services:**
- Price feed APIs (future)
- Authentication services (future)
- Notification services (future)

### 4.4 Communications Interfaces

**Protocols:**
- HTTP/HTTPS for API communication
- TCP/IP for database connections
- WebSocket (future for real-time updates)

**Data Formats:**
- JSON for API requests/responses
- SQL for database queries
- CSV for data exports (future)

---

## 5. Non-Functional Requirements

### 5.1 Performance Requirements

**Response Times:**
- API endpoints: < 200ms (95th percentile)
- Portfolio snapshots: < 500ms
- Trade processing: < 100ms
- Price updates: < 50ms

**Throughput:**
- Support 1000+ concurrent users
- Process 100+ trades per second
- Handle 10,000+ price updates per minute

**Scalability:**
- Horizontal scaling capability
- Database connection pooling
- Async processing support

### 5.2 Reliability Requirements

**Availability:**
- 99.9% uptime target
- Graceful degradation during failures
- Automatic recovery mechanisms

**Data Integrity:**
- ACID transaction compliance
- Data validation at all levels
- Backup and recovery procedures

### 5.3 Security Requirements

**Authentication:**
- JWT-based authentication (future)
- Role-based access control
- Session management

**Data Protection:**
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- HTTPS encryption

**Audit Trail:**
- Log all trade activities
- Track user actions
- Maintain audit logs

### 5.4 Usability Requirements

**API Design:**
- Intuitive endpoint naming
- Consistent response formats
- Comprehensive error messages
- Interactive documentation

**Documentation:**
- Complete API documentation
- Code examples
- Integration guides

---

## 6. System Architecture

### 6.1 Architectural Overview

The system follows a layered architecture pattern:

```
┌─────────────────────────────────────┐
│           API Layer                 │
│    (FastAPI Routes & Schemas)      │
├─────────────────────────────────────┤
│          Service Layer              │
│    (Business Logic & Processing)   │
├─────────────────────────────────────┤
│           Data Layer                │
│    (SQLAlchemy Models & CRUD)      │
├─────────────────────────────────────┤
│         Database Layer              │
│    (SQLite/PostgreSQL)             │
└─────────────────────────────────────┘
```

### 6.2 Component Architecture

**API Layer Components:**
- `portfolios.py`: Portfolio management endpoints
- `simulations.py`: Trade simulation endpoints
- `taxlots.py`: Tax lot management endpoints
- `schemas/`: Pydantic models for validation

**Service Layer Components:**
- `portfolio_service.py`: Portfolio business logic
- `processing_service.py`: Trade processing logic
- `workers/`: Background task processing

**Data Layer Components:**
- `models/`: SQLAlchemy database models
- `crud/`: Database operation abstractions
- `db/session.py`: Database session management

### 6.3 Data Flow

**Trade Processing Flow:**
1. API receives trade request
2. Service layer validates and processes trade
3. CRUD layer updates database
4. Response returned to client

**Portfolio Snapshot Flow:**
1. API receives snapshot request
2. Service layer queries tax lots
3. Calculations performed on-the-fly
4. Aggregated data returned to client

---

## 7. Data Models

### 7.1 Core Entities

#### 7.1.1 TaxLot Entity

```python
class TaxLot:
    id: int                    # Primary key
    user_id: int              # Foreign key to user
    security_id: int          # Foreign key to security
    version: int              # Version for optimistic locking
    open_date: datetime       # Purchase date
    created_at: datetime      # Record creation timestamp
    close_date: datetime      # Sale date (nullable)
    open_qty: Decimal         # Original quantity purchased
    close_qty: Decimal        # Quantity sold
    remaining_qty: Decimal    # Current remaining quantity
    open_price: Decimal       # Purchase price per unit
    close_price: Decimal      # Sale price per unit (nullable)
    charges: Decimal          # Associated fees/charges
    realized_pnl: Decimal     # Realized profit/loss
    stcg: Decimal            # Short-term capital gains tax
    ltcg: Decimal            # Long-term capital gains tax
    status: LotStatus        # OPEN, PARTIAL, or CLOSED
```

#### 7.1.2 Portfolio Entity (Deprecated)

```python
class Portfolio:
    id: int                   # Primary key
    user_id: int             # Foreign key to user
    security_id: int         # Foreign key to security
    quantity: Decimal        # Total quantity held
    avg_cost_basis: Decimal  # Weighted average cost
    current_price: Decimal   # Latest market price
    unrealized_pnl: Decimal  # Unrealized profit/loss
    realized_pnl_ytd: Decimal # Year-to-date realized P&L
    stcg_ytd: Decimal       # Year-to-date STCG
    ltcg_ytd: Decimal       # Year-to-date LTCG
    last_updated: datetime   # Last update timestamp
```

#### 7.1.3 Price Entity

```python
class Price:
    id: int                  # Primary key
    security_id: int        # Foreign key to security
    price: Decimal          # Current price
    timestamp: datetime     # Price update timestamp
    source: str             # Price source identifier
```

### 7.2 Enumerations

#### 7.2.1 LotStatus Enum

```python
class LotStatus(str, Enum):
    OPEN = "OPEN"           # Lot is fully open
    PARTIAL = "PARTIAL"     # Lot is partially closed
    CLOSED = "CLOSED"       # Lot is fully closed
```

### 7.3 Data Relationships

**User → TaxLot**: One-to-Many
- One user can have multiple tax lots
- Each tax lot belongs to one user

**Security → TaxLot**: One-to-Many
- One security can have multiple tax lots
- Each tax lot belongs to one security

**Security → Price**: One-to-Many
- One security can have multiple price records
- Each price record belongs to one security

---

## 8. API Specifications

### 8.1 Portfolio Endpoints

#### 8.1.1 Get Portfolio Snapshot

**Endpoint:** `GET /api/v1/portfolios/{user_id}/snapshot`

**Description:** Retrieve complete portfolio snapshot for a user.

**Parameters:**
- `user_id` (path): User identifier

**Response:**
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

### 8.2 Tax Lot Endpoints

#### 8.2.1 List Tax Lots

**Endpoint:** `GET /api/v1/taxlots/`

**Description:** Retrieve tax lots with optional filtering.

**Query Parameters:**
- `user_id` (required): User identifier
- `security_id` (optional): Security identifier
- `status` (optional): Lot status filter

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 123,
    "security_id": 1,
    "open_date": "2024-01-01T10:00:00Z",
    "open_qty": 100.0000,
    "remaining_qty": 50.0000,
    "close_qty": 50.0000,
    "status": "PARTIAL",
    "close_date": "2024-01-10T15:30:00Z",
    "close_price": 160.0000,
    "open_price": 150.0000,
    "charges": 5.0000,
    "realized_pnl": 500.0000,
    "stcg": 125.0000,
    "ltcg": 0.0000
  }
]
```

### 8.3 Simulation Endpoints

#### 8.3.1 Process Trade

**Endpoint:** `POST /api/v1/simulate/trades`

**Description:** Process buy or sell trade (simulation endpoint).

**Request Body:**
```json
{
  "user_id": 123,
  "security_id": 1,
  "side": "BUY",
  "quantity": 100.0,
  "price": 150.0,
  "timestamp": "2024-01-15T10:00:00Z",
  "charges": 5.0
}
```

**Response:**
```json
{
  "message": "Trade accepted for processing."
}
```

#### 8.3.2 Update Price

**Endpoint:** `POST /api/v1/simulate/prices`

**Description:** Update security price (simulation endpoint).

**Request Body:**
```json
{
  "user_id": 123,
  "security_id": 1,
  "price": 175.0
}
```

**Response:**
```json
{
  "message": "Price for 1 updated to 175.0."
}
```

### 8.4 Error Handling

**Standard Error Response:**
```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**HTTP Status Codes:**
- 200: Success
- 201: Created
- 202: Accepted
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 422: Validation Error
- 500: Internal Server Error

---

## 9. Database Design

### 9.1 Database Schema

#### 9.1.1 Tax Lots Table

```sql
CREATE TABLE tax_lots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    security_id INTEGER NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    open_date DATETIME NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    close_date DATETIME,
    open_qty DECIMAL(19,4) NOT NULL,
    close_qty DECIMAL(19,4) NOT NULL DEFAULT 0,
    remaining_qty DECIMAL(19,4) NOT NULL,
    open_price DECIMAL(19,4) NOT NULL,
    close_price DECIMAL(19,4),
    charges DECIMAL(19,4) NOT NULL DEFAULT 0,
    realized_pnl DECIMAL(19,4) NOT NULL DEFAULT 0,
    stcg DECIMAL(19,4) NOT NULL DEFAULT 0,
    ltcg DECIMAL(19,4) NOT NULL DEFAULT 0,
    status VARCHAR(10) NOT NULL DEFAULT 'OPEN',
    
    INDEX idx_user_id (user_id),
    INDEX idx_security_id (security_id),
    INDEX idx_user_security (user_id, security_id),
    INDEX idx_open_date (open_date),
    INDEX idx_status (status)
);
```

#### 9.1.2 Portfolio Summary Table (Deprecated)

```sql
CREATE TABLE portfolio_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    security_id INTEGER NOT NULL,
    quantity DECIMAL(19,4) NOT NULL DEFAULT 0,
    avg_cost_basis DECIMAL(19,4) NOT NULL DEFAULT 0,
    current_price DECIMAL(19,4) NOT NULL DEFAULT 0,
    unrealized_pnl DECIMAL(19,4) NOT NULL DEFAULT 0,
    realized_pnl_ytd DECIMAL(19,4) NOT NULL DEFAULT 0,
    stcg_ytd DECIMAL(19,4) NOT NULL DEFAULT 0,
    ltcg_ytd DECIMAL(19,4) NOT NULL DEFAULT 0,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_user_security (user_id, security_id),
    INDEX idx_user_id (user_id),
    INDEX idx_security_id (security_id)
);
```

#### 9.1.3 Prices Table

```sql
CREATE TABLE prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    security_id INTEGER NOT NULL,
    price DECIMAL(19,4) NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50),
    
    INDEX idx_security_id (security_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_security_timestamp (security_id, timestamp)
);
```

### 9.2 Indexing Strategy

**Primary Indexes:**
- Primary keys on all tables
- Foreign key indexes for joins
- Composite indexes for common queries

**Query Optimization:**
- User-based queries: `idx_user_id`
- Security-based queries: `idx_security_id`
- Combined queries: `idx_user_security`
- Time-based queries: `idx_open_date`, `idx_timestamp`

### 9.3 Data Integrity

**Constraints:**
- NOT NULL constraints on required fields
- CHECK constraints for valid ranges
- UNIQUE constraints where appropriate
- FOREIGN KEY constraints (when implemented)

**Validation Rules:**
- Quantities must be non-negative
- Prices must be positive
- Dates must be valid
- Status values must be from enum

---

## 10. Security Requirements

### 10.1 Authentication and Authorization

**Current State:**
- No authentication implemented
- All endpoints are publicly accessible
- User ID passed as parameter

**Future Requirements:**
- JWT-based authentication
- Role-based access control
- User session management
- API key authentication for external services

### 10.2 Data Protection

**Input Validation:**
- Pydantic model validation
- Type checking and conversion
- Range validation for numeric fields
- Format validation for dates and strings

**SQL Injection Prevention:**
- Parameterized queries
- SQLAlchemy ORM usage
- Input sanitization

**XSS Protection:**
- Output encoding
- Content-Type headers
- CORS configuration

### 10.3 Audit and Logging

**Audit Trail:**
- Log all trade activities
- Track user actions
- Record system events
- Maintain audit logs

**Logging Requirements:**
- Structured logging format
- Log levels (DEBUG, INFO, WARN, ERROR)
- Request/response logging
- Error tracking and monitoring

---

## 11. Performance Requirements

### 11.1 Response Time Requirements

**API Endpoints:**
- Portfolio snapshots: < 500ms
- Trade processing: < 100ms
- Price updates: < 50ms
- Tax lot queries: < 200ms

**Database Operations:**
- Simple queries: < 10ms
- Complex aggregations: < 100ms
- Bulk operations: < 1000ms

### 11.2 Throughput Requirements

**Concurrent Users:**
- Support 1000+ concurrent users
- Handle 100+ requests per second
- Process 10,000+ price updates per minute

**Data Processing:**
- Process 100+ trades per second
- Handle 1M+ tax lot records
- Support 10K+ securities

### 11.3 Scalability Requirements

**Horizontal Scaling:**
- Stateless application design
- Database connection pooling
- Load balancer compatibility
- Container orchestration support

**Vertical Scaling:**
- Multi-core CPU utilization
- Memory optimization
- Database query optimization
- Caching strategies

---

## 12. Deployment Requirements

### 12.1 Environment Requirements

**Development Environment:**
- Python 3.10+
- SQLite database
- Local development server
- Poetry for dependency management

**Production Environment:**
- Linux/Windows servers
- PostgreSQL database
- Docker containers
- Load balancers
- Monitoring tools

### 12.2 Configuration Management

**Environment Variables:**
- Database connection strings
- Secret keys and tokens
- API configuration
- Feature flags

**Configuration Files:**
- Docker configuration
- Database migration scripts
- Logging configuration
- Monitoring setup

### 12.3 Deployment Process

**Development Deployment:**
1. Clone repository
2. Install dependencies
3. Configure environment
4. Run database migrations
5. Start application server

**Production Deployment:**
1. Build Docker image
2. Deploy to container registry
3. Configure production environment
4. Run database migrations
5. Deploy with orchestration tool
6. Verify deployment

### 12.4 Monitoring and Maintenance

**Health Checks:**
- Application health endpoint
- Database connectivity checks
- External service monitoring
- Performance metrics

**Maintenance Tasks:**
- Database backups
- Log rotation
- Security updates
- Performance optimization

---

## Conclusion

This Software Requirements Specification provides a comprehensive overview of the Position Tracker API system, including its functional requirements, technical specifications, and implementation details. The system is designed to provide robust portfolio management capabilities with a focus on accuracy, performance, and scalability.

The modular architecture allows for future enhancements and integrations, while the current implementation provides a solid foundation for portfolio tracking and tax management functionality.

---

**Document Control:**
- Version: 1.0
- Last Updated: January 2024
- Next Review: March 2024
- Approval: Development Team Lead
