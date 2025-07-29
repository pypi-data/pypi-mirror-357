# CRC_API

A Python wrapper for the MatInf VRO API used in CRC 1625. It allows querying samples, associated objects, compositions, and properties.

## Installation

```bash
pip install CRC_API
```

### 1. Initialize the client
```python
### Full Summary Query Example
from crc_api import MatInfWebApiClient

crc_api = MatInfWebApiClient(
    service_url="https://your-api-endpoint",  # e.g., "https://matinf-api.crc1625.de"
    api_key="your-api-token"
)
```
### Full Summary Query Example
```python
summary = crc_api.get_summary(
    main_object="Sample",                        # Main object type to search
    start_date="2023-01-01",                         # Start of creation date range
    end_date="2025-01-01",                           # End of creation date range
    include_associated=True,                         # Include linked objects
    include_properties=True,                         # Include main object properties
    include_composition=True,                        # Include element composition
    include_linked_properties=True,                  # Include properties of associated objects
    user_associated_typenames=["EDX CSV", "Bandgap Sample Spectra"],  # Associated object types to include
    property_names=["Bandgap", "Resistance"],        # Properties to extract
    required_elements={"Pt": (10, 90), "Au": None},  # Filter for samples with elements in given range
    required_properties=["Bandgap"],                 # Filter for samples that include this property
    save_to_json=True,                               # Save summary to disk
    output_folder="summary_results"                  # Folder to save output
)

```
### Search and Download Data
```python
crc_api.search(
    main_object="Sample",
    associated_typenames=["EDX CSV", "HTTS Resistance CSV"],
    start_date="2022-01-01",
    end_date="2025-05-31",
    element_criteria={"Pt": (10, 90), "Pd": None},
    strict=True,
    save_location="output",
    download_folder="downloads",
    output_filename="filtered_results.csv"
)
```
### Filter by Elements
```python
df, sample_ids = client.filter_samples_by_elements(
    object_ids=[101, 102, 103],
    element_criteria={"Pt": (20, 80), "Ag": None}
)
```

### Filter Linked Composition by Sample ID

```python
filtered_df, object_map = client.filter_samples_by_elements_and_composition(
    sample_ids=[1234, 5678],
    object_link_mapping={
        1234: [2001, 2002],
        5678: [2003]
    },
    element_criteria={"Pd": (5, 60)}
)
```