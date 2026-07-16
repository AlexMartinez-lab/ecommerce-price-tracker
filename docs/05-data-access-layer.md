# Data Acces Layer

## Purpose

The data Acces Layer separates PostgreSQL queries from scraper, pipeline and applications logic.

Future components must access persistent data trough repository classes insted of writing SQL directly

## Models

The current domain models are:

- Product
- Store
- ProductListing
- PipelineRun
- PriceObservation

The current repositories are:

- ProductRepository
- StoreRepository
- ListingRepository
- PipelineRepository
- PriceHistoryRepository

## Supported operations


### Products

- Create
- Retrieve by ID
- List
- Search by name
- Updatable
- Disable

### Stores

- Create
- Retrieve by ID
- Retrieve by domain
- List
- Disable

### Listings

- Create
- Retrieve by ID
- Retrieve by external ID
- List active listings
- Update last-seen timestamp
- Disable


### Pipeline runs

- Start an execution
- Finish an execution
- Retrieve an execution
- List recent executions

### Price history

- Create immutable observations
- Retrive listing history
- Retrive latest observation

## Validation

Manual integration test:


python -m scripts.test_data_access_layer


Automated integration test:

python -m unittest discover -s tests -v

## Current limitation

Each repository method currently manages its own database transaction.

A future service layer may coordinate shared transactions for operations
that involve multiple repositories.

## Next step

Create the first data collection service and implement a controlled
scraper adapter for one supported source. 
