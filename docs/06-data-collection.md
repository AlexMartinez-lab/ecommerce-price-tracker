# Data Collection

## Purpose

The data collection layer extracts product information from external
sources and returns normalized data without accessing PostgreSQL directly.

## Architecture

```text

Source
  |
  v
Collector Adapter
  |
  v
HTML Parsing
  |
  v
Data Validation
  |
  v
CollectedProductData

```

## Initial controlled source

The first collector uses a local HTML fixture.

This controlled source makes it possible to validate:

- HTML parsin.
- CSS selectors.
- Required fields.
- Price normalization.
- Availability extraction.
- Error handling.
- Automated tests.

The controlled collector does not require internet access and does not
depend on third-party website stability.

## Collector interface

Every product collector must implement:

collect() -> CollectedProductData

## Current extracted fields

- External listing ID.
- Listing title.
- Brand.
- Model.
- Current price.
- Original price.
- Currency.
- Shipping cost.
- Availability.
- Stock status.
- Image URL.
- Raw price text.

## Error handling

Current collection exceptions include:

- CollectionError.
- SourceReadError.
- ElementNotFoundError.
- InvalidPriceError.


## Price normalization

Extracted monetary values are converted to Python Decimal objects.

The parser currently supports common formats such as:

 $21,499-00
 21499.00
 21.299,50
 MXN 21,499


## Validation commands

Manual collector validation:

python -m scripts.test_local_collector

Automated tests:

python -m unittest discover -s tests -v

## Current limitation

The current adapter reads only a controlled local HTML fixture.

It does not perform HTTP request or collect data from a real e-commerce platform.


## Next step

Create a collection service that converts CollectedProductData into a 
PriceObservation and persists it through the repository layer.
