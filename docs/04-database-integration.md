# Python Database Integration

## Purpose

This document describes how the Python application connects to the PostgreSQL
database used by E-commerce Price Tracker.

## Dependencies

- Psycopg 3
- python-dotenv


## Configuration

Database credentials are loaded from environment variables stored in 
the local '.env' file.

Required variables:

```text
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
```


## Modules

## config.py

Loads and validates environment variables.

## connection.py

Creates PostgreSQL connections and provides a managed connection context.

## health_check.py

Validates:

- PostgreSQL connectivity.
- Database name.
- Database user.
- Required MVP tables.

# Current status

Python can connect to PostgreSQL and query the initial project schema.

# Next step

Create repository modules for products, listings, pipeline executions and price observations.


