# System Architecture

 

# Purpose

This document describes the overall architecture ot the E-commerce Price Tracker system.

Rather than being developed as a simple web scraper, the project is designed as a modula
Data Engineering platform where each component has a specific responsability.

The architecture follows the principle of separation of concerns, allowing every module to evolve independently.

 

# High-Level Architecture


		User

		 |
		 v

	Dashboard / REST API

		 |
		 v

	  Analytics Layer

	 	 |
		 v

             PostgreSQL

		 |
		 v	

            ETL Pipeline

		 |
 		 v

	   Data processing

		 |
		 v

	   Web Scrapers

		 |
		 v

	E-commerce Websites


# System Components

## 1. Data Sources

The system collects information from one or more e-commerce websites.

Examples:

- Amazon
- Mercado libre
- Waltmart
- CiberPuerta
- DDTech
- Costco

Initially only one source will be implemented.

 

## 2. Web Scraper

Responsabilities

- Connect to websites.
- Download product pages.
- Extract raw information.
- Handle connection errors.
- Return structured data.

Input

Product URL

Output

Raw product data

 

## 3. Data Processing

Responsabilities

- Validate extracted information.
- Normalize prices.
- Standardize text.
- Clean unnecessary characters.
- Prepare data for storage

Output

Validated product record

 

## 4. ETL Pipeline

Responsabilities

Retrieve product information.

Transform
 
Validate and normalize data.

Load

Insert processed information into PostgreSQL

The ETL pipeline represent the core of the application.

 

## 5. Database

Responsabilities

Store:

- Products
- Stores
- Historical prices
- Categories
- Future alerts

The database acts as the system's single source of truth.

 

## 6. Analytics Layer

Responsabilities

Generate information such as:

- Historical prices
- Average prices
- Lowest recorded price
- Highest recorded price
- Price variation

This layer prepares data for visualization.

 

## 7. Dashboard

Future version will provide:

- Price history
- Interactive charts
- Product comparison
- Store comparison
- Purchase alerts

 

# Data flow

The complete workflow is:

1. User register a product.
2. The scraper downloads the webpage.
3. Raw data is extracted.
4. Data is validated.
5. Prices are normalized.
6. Information is stored.
7. Historical records are update.
8. Analytics are calculated.
9. Results are displayed.

 

# Design Principles

The architecture follows the following principles:

- Modular design
- Separation of concerns
- Scalability
- Maintainability
- Reusability
- Simplicity
- Extensibility

 

# Future Evolution

The architecture has been designed to allow future integration of:

- Docker
- FastAPI
- Airflow
- Kafka
- Redis
- Cloud deployment
- Machine Learning

without major redesing.

 

# Current Status

Current Version

1.0

Current Phase

Architecture Design

Last Update

July 2026
