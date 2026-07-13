## Database Design

# Purpose

This document defines the initial relational database design for the E-commerce Price Tracker project.

The database is designed to support multiple products, stores, sellers and product listing form the beginning,
even thought the first MVP will track only one product from one store.

The objetive is to create a normalized and extensible data model than can store historical price observation
without requiring a major redesign when new data sources ara added.

 

# Desing Goals

The data design must:

- Store products independently from online stores.
- Support multiple stores.
- Support multiple sellers within the same marketplace.
- Associate equivalent listing with the same canonical product.
- Preserve historical price observations.
- Store currency and availability information.
- Avoid unnecessary duplication.
- Maintain data integrity trough keys and constraints.
- Support future price comparisons and alerts.

 

# Core Concepts

# Canonical Product

A canonical product represent the real-world item being tracked.

Example:

Samsung Galaxy S23+ 256 GB Phantom Black

The canonical product is independent from any store, seller or URL.

Several listings from different stores may refer to the same canonical product.

 

# Product Listing

A product listing represents a specific publication or offer from a particular store.

Examples:

Amazon Mexico listing for Samsung Galaxy S23+ 256 GB
Mercado Libre listing from Seller A
Mercado Libre listing from Seller B
Waltmart Mexico listing for the same product

Each listing may have:

- A different URL.
- A different seller.
- A different price.
- Different shipping conditions.
- Different stock availability.
- A different title or description.

 

# Price Observation

A price observation is a historical record captured at a especific moment.

Every scraper execution may create a new observation containing:

- Current price.
- Original price.
- Currency.
- Availability.
- Shipping cost.
- Capture timestamp.

Price observations should not overwrite previous values.

They form the historical dataset used by the analytics layer.

 

# Main Entities

The initial model contains the following entities:

1. categories
2. brands
3. products
4. stores
5. sellers
6. product_listings
7. price_history
8. pipeline_runs

Future versions may add:

9. users
10. price_alerts
11. product_matches
12. notifications

 

# Entity Relationship Overview

'''text
categories
    |
    | 1
    |
    | 
    | N
products -------  brands
    |   	
    | 1     	
    |
    | N
product_listing ------- stores
    |                      |
    |                      |
    |                   sellers
    |
    | 1
    | 
    | N
price_history

pipeline_runs
    |
    | 1
    |
    | N
price_history

'''
 


## Detailed Entities

# 1. categories

Stores product categories.

Examples:

- Smartphones
- Laptops
- Graphics Cards
- Home Appliances

Proposed fields:

'''text
Field		Type		Description
-------------------------------------------- 
id		BIGINT		Primary Key
name		VARCHAR(100)	Category name
slug		VARCHAR(120)	URL-friendly identifier
parent_id	BIGINT		Optional parent category
created_at	TIMESTAMPTZ	Creation timestamp
'''
Rules:

- name is requiered.
- slug must be unique.
- parent_id may reference another category.
- Hierarchical categories are optional during the MVP.

 

# 2. brands

Stores normalized product brands.

Examples:

- Samsung
- Apple
- Lenovo
- NVIDIA

Proposed fields:

'''text
Field		Type		Description
------------------------------------------------- 
id		BIGINT		Primary key
name		VARCHAR(100)	Brand name
created_at	TIMESTAMPTZ	Creation timestamp
'''

Rules:

- name is required.
- Brand names must be unique.
- Brand matching may initially be performed manually.



# 3. products

Stores canonical products independently from any store.

Proposed fields:

'''text
Field		Type		Description
------------------------------------------------ 
id		BIGINT		Primary key
name		VARCHAR(255)	Canonical product name
brand_id	BIGINT		Reference to brands
category_id	BIGINT		Reference to categories
model		VARCHAR(150)	Manufacturer model
sku		VARCHAR(100)	Optional internal or manufacturer SKU
description	TEXT		Optional normalized description
active		BOOLEAN		Indicates whether tracking is enabled
created_id	TIMESTAMPTZ	Creation timestamp
update_id	TIMESTAMPTZ	Last update timestamp
'''

Rules:

- name is required.
- A product may temporarily have no brand or category.
- active defaults to true.
- Products must not store store-specific URLs.
- Products must not store current prices.	

 

# 4. stores

Stores supported e-commerce platforms.

Examples:

- Amazon Mexico
- Mercado Libre Mexico
- Waltmart Mexico
- CyberPuerta

Proposed fields:

'''text
Field		Type		Description
------------------------------------------------------- 
id		BIGINT		Primary key
name		VARCHAR(120)	Store name
domain		VARCHAR(255)	Main store domain
country_code	CHAR(2)		ISO country code
active		BOOLEAN		Indicates whether collection is enable
created_id	TIMESTAMPTZ	Creation timestamp
'''

Rules:

- name is required.
- domain must be unique.
- country_code will initially use MX.
- active defaults to true.

 

# 5. sellers

Stores sellers operatin within markectplaces.

A store such as Mercado Libre or Amazon may contain multiple third-party sellers.

Proposed fields:

'''text
Field			Type		Description
------------------------------------------------------------- 
id			BIGINT		Primary key
store_id		BIGINT		Reference to stores
external_seller_id	VARCHAR(150)	Seller ID assigned by the store
name			VARCHAR(255)	Seller display name
official_store		BOOLEAN		Indicates official brand store
created_at		TIMESTAMPTZ	Creation timestamp
'''

Rules:

- A seller belongs to one store.
- The combination of store_id and external_seller_id be unique.
- Seller information may be null when the source does not expose it.
- official_store defaults to false.

 

# 6. product_listings

Stores the relationship between a canonical product and a specific online publication.

This is one of the most important tables in the model.

Propose fields:

'''text
Field			Type			Description
---------------------------------------------------------------------- 
id			BIGINT			Primary key
product_id		BIGINT			Reference to products
store_id		BIGINT			Reference to stores
seller_id		BIGINT			Optional reference to sellers
external_listing_id	VARCHAR(200)		Listing identifier from the source
title			TEXT			Listing title as displayed by the store
url			TEXT			Product listing URL
image_url		TEXT			Main product image
condition		VARCHAR(30)		New, used, refurbished or unkown
active			BOOLEAN			Indicates whether the listing is tracked
first_seen_at		TIMESTAMPTZ		First collection timestamp
last_seen_at 		TIMESTAMPTZ		Most recent successful observation
created_at		TIMESTAMPTZ		Record creation timestamp
updated_at		TIMESTAMPTZ		Last update timestamp
'''

Rules:

- Every listing belongs to one canonical product.
- Every listing belongs to one store.
- A listing may optionally belong to a seller.
- The listing URL must be store separatly from the canonical product.
- The combination of store and external listing identifier should be unique.
- A listing may become inactive without deleting its historical data.
- Listing titles are kept because they provide useful raw source context.

 

# 7. price_history

Stores immutable historical observations for every tracked listing.

Proposed fields:

'''text
Field			Type		Description
------------------------------------------------------------- 
id			BIGINT		Primary key
listing_id		BIGINT		Reference to product_listings
pipeline_run_id		BIGINT		Optional reference to pipeline_runs
current_price		NUMERIC(12,2)	Current observed price
original_price		NUMERIC(12,2)	Price before discount
shipping_cost		NUMERIC(12,2)	Observed shipping cost
currency		CHAR(3)		ISO currency code
available		BOOLEAN		Availability status
stock_status		VARCHAR(50)	Textual availability description
raw_price_text		VARCHAR(100)	Original extracted price text
observed_at		TIMESTAMPTZ	Observation timestamp
created_at		TIMESTAMPTZ	Database insertion timestamp
'''

Rules:

- Historical records must not be updated after instertion.
- current_price must be zero or greater.
- original_price, when present, must be zero or greater.
- shipping_cost, when present, must be zero or greater.
- Currency will initially default to MXN.
- observed_at represents when the information was collected.
- created_at represents when it was written to the database.
- Failed scraping attempts must not create invalid price observations.

 

# 8. pipeline_runs

Stores information about every ETL pipeline execution.

This table will help with monitoring, debugging and Linux automation.

Proposed fields:

'''text
Field			Type		Description
------------------------------------------------------------ 
id			BIGINT		Primary key
started_at		TIMESTAMPTZ	Pipeline start time
finished_at		TIMESTAMPTZ	Pipeline end time
status			VARCHAR(20)	Running, success, partial or failed
listing_processed	INTEGER		Number of processed listings
successful_records	INTEGER		Successful observations
failed_records 		INTEGER		Failed observations
error_message		TEXT		General error information
execution_source	VARCHAR(30)	Manual, cron, API or scheduler
created_at		TIMESTAMPTZ	Record creation timestamp
'''

Rules:

- A pipeline execution starts whit status running.
- The final status must be success, partial or failed.
- Counts must be zero or greater.
- Detailed logs remain in application log files.
- This table stores operational execution summaries.

 


## Relationship Summary

# Categories to products

One category may contain many products.

A product may belong to one category.

category 1 ---- N products

 

# Brands to products

One brand may have many products.

A product may belong to one brand.

brands 1 ---- N products

 

# Products to product_listings

One canonical product may have many listings.

Each listing refers to one canonical product.

products 1 ---- N product_listings

 

# Stores to product_listings

One store may contain many product listings.

Each listing belongs to one store.

stores 1 ---- N product_listings

 

# Stores to sellers

One store may contain many sellers.

Each seller belongs to one store.

store 1 ---- N sellers

 

# Sellers to product_listings

One seller may publish many listings.

A listing may optionally have one seller.

sellers 1 ---- N product_listings

 

# product_listings to price_history

One listing may have many price observations.

Each price observation belongs to one listing.

product_listings 1 ---- N price_history

 

# pipeline_runs to price_history

One pipeline execution may create many price observations.

A price record my optionally reference one pipeline execution.

pipeline_runs 1 ---- N price_history

 


## Product Matching Strategy	

Different stores may use different titles for the same product.

Example:

Samsung Galaxy S23 Plus 256GB Negro

Samsung S23+ 256 GB Phantom Black

Galaxy S23 Plus SM-S916U 256GB

All three listings may represent the same canonical product.

For the MVP, product matching will be performed manually.

The developer will:

1. Create one canonical product.
2. Register the listing.
3. Associate the listing with the correct product.

Automatic product matching is outside the MVP scope.

Future versions may use:

- Manufacturer model numbers.
- SKUs.
- UPC or EAN identifiers.
- Text normalization.
- Similarity algorithms.
- Machine learning.

 


## Historical Data Strategy

The system will use an append-only strategy for price observations.

Every successful collection creates a new row in price_history.

Example:

'''text
listing			Price		Observed At
------------------------------------------------------------- 
Product A-Amazon	12500.00	2026-07-10 10:00
Product A-Amazon	12300.00	2026-07-10 16:00
Product A-Amazon	11999.00	2026-07-11 10:00

'''

The system must not replace the previous price with the latest one.

This design enables:

- Price history charts.
- Minimum and maximum price calculations.
- Price change detection.
- Discount analysis.
- Store comparisons.
- Future alert evaluations.

 


# Duplicate Observation Policy

During early develpment, each successful execution may create a new observation 
even when price has not changes.

This provides a complete record of date collection and proves that the pipeline ran successfully.

A future optimization may avoid storing identical observations when:

- The price is unchanged.
- Availability is unchanged.
- Shipping cost is unchanged.
- The previous observation is recent.

That optimization is intentionally postponed until real data volume justifies it.

 


# Data Types and Precision

Prices will use:

NUMERIC(12,2)

Floating-point types must not be used for monetary values.

Timestamps will use:

TIMESTAMPTZ

Using time-zone-aware timestamps avoids ambiguity when the system is later deployed in another region or cloud enviorment.

Currencies will use ISO 4217 codes such as:

MXN
USD
CAD

Countries will use ISO 3166-1 alpha-2 codes such as:

MX
US
CA

 


# Deletion Strategy

Historical information should not be removed when a product or listing is no longer tracked

Insted, records will use an active field.

Example:

active = true

The pipeline continues monitoring the listing.

active = false

The pipeline stops monitoring the listing, but historical observactions remain available.

Hard deletion should be reserved for:

- Invalid test data.
- Accidental records.
- Development database resets.
- Legal or privacy requirements.




# Initial MVP Database Scope

Although the complete design includes several entities, the first implementation will focus on:

- Products
- Stores
- product_listings
- price_history
- pipeline_runs

The following entities may be added shortly afterward:

- brands
- categories
- sellers

This allows the MVP to remain manageable while preserving the ful architectural direction.

 

# Example MVP Data

# Product

Name:
Samsung Galaxy S23+ 256 GB

Brand:
Samsung

Model:
SM-S916

# Store

Name:
Mercado Libre Mexico

Domain:
mercadolibre.com.mx

Country:
MX

# Listing

Product:
Samsung Galaxy S23+ 256 GB

Store:
Mercado Libre Mexico

Title:
Samsung Galaxy S23 Plus 256GB

URL:
Product listing URL

Condition:
new

# Price Observation

Current price:
12599.00

Currency:
MXN

Available:
true

Observed at:
Collection timestamp

 


# Indexing Strategy

The firt version should include indexes for frequently queried relatioship and time-based serches.

Recommended indexes:

- product.name
- stores.domain
- product_listings.product_id
- product_listings.store_id
- product_listings.external_listings_id
- price_history.listing_id
- price_history.observed_at
- Composite index on price_history(listing_id, observed_at)

The composite index will be especially useful for retrieving the price history of one listing in chronologicao order.

Indexes should be added based on actual query patterns and measured performance.

--- 


# Integrity Rules

The database should enforce the following rules:

- A price observation cannot exist without a valid listing.
- A listing cannot exist without a valid product and store.
- Prices cannot be negative.
- Shipping cost cannot be negative.
- Store domains must be unique.
- Brand names should be unique.
- Category slugs should be unique.
- Listing identifiers should be uniquit within each store.
- Historical records should not be overwritten.
- Inactive products and listings must preserve their history.

 


# Security Considerations

Database credentials must not be committed to GitHub.

Credentials will be stored in:

.env

The repository will only contain:

.env.example

The application should use a dedicated PostgreSQL user instead of the default administrative account.

The application user should receive only the permissions required by the project.

 


# Future Entities

# price_alerts

Will store user-defined target prices and alert conditions.

Possible fields:

- product_list
- listing_id
- target_price
- active
- created_at
- triggered_at

 


# Users

Will be introduced only if authentication is implemented.

Possible fields:

- email
- password hash
- active
- created_at

Password must never be stored in plain text.

 


# product_matches

May store confidence scores and matching evidence between listings and canonical products.

This would support future automatic product matching.

 


# notifications

May record alert delivery attempts throught:

- email
- telegram
- push notifications

 

## Design Decisions

# Decision 1: Separate products form listings

Reason:

The same real-world product may appear in several stores or seller publications.

Storing URLs directly in the product table would make multi-store comparison difficult.




# Decision 2: Use an append-only price history

Reason:

The primary value of the project is historical analasis.

Updating a single current-price field would destroy previous information.

 


# Decision 3: Support sellers separately

Reason:

Marketplaces may contain multiple sellers offering the same product with different prices and conditions.

 


# Decision 4: Track pipeline executions

Reason:

Operational metadata helps diagnose failures, verify automated execution and demonstrate data pipeline monitoring skills.

 

# Decision 5: Use PostgreSQL

Reason:

PostgreSQL provides:

- Strong relational integrity.
- Advance SQL capabilities.
- Reliable transaction support.
- Time-zone-aware timestamps.
- Numeric precision for financial data.
- Good compatibility with python and data engineering tools.

 


## MVP Entity Relationship Diagram

'''text
|products        |
----------------- 
|id              |
|name            |
|model           |
|active          |
|created_at      |
|updated_at      |
---------------- 
       |
       | 1
       |
       | N
------------------- 
|product_listings |
------------------- 
|id               |
|product_id       |
|store_id         |
|title            |
|url              |
|condition        | 
|active           |
|first_seen_at    | 
|last_seen_at     |
------------------- 
       |
       | 1
       |
       | N
       |
------------------- 
|price_history	  |
------------------- 
|id               |
|listing_id       |
|pipeline_run_id  | 
|current_price    |
|original_price   |
|shipping_cost    |
|currency         | 
|available        |
|observed_at      |
------------------- 



------------------- 
|      Stores     |
------------------- 
|id               |
|name             |
|domain           |
|country_code     |
|active           |
------------------- 
         |
         | 1
         |
         | N
         |
	 --------------> product_listings


-------------------- 
| pipeline_runs    |
-------------------- 
|id                |
|started_at        |
|finished_at       |
|status            |
|processed         |
|successful        |
|failed            |
-------------------- 
         |
         | 1
         |
         | N
         -----------> price_history

'''


# Current Status

Current phase:

Database Design

Document version:

1.0

Last Updated:

July 2026

Implementation status:

The initial PostgreSQL schema has been implemented in database/schema.sql.

Next step:

Connect the Python application to PostgreSQL and create the first 
database access module.
