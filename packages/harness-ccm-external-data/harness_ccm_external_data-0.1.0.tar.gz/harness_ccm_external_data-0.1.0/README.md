# harness-ccm-external-data

tools to help manage ingesting external data in harness ccm

the project is split into several parts:
- converting external data formats to a compatible format for harness (focus)
- uploading the converted data to the harness platform

## loading data

when loading in a billing export we can apply a few modifications of the data to prepare it for ingestion into harness.

first, we convert any non-focus fields to their focus equivalent. this is done by providing a map of focus fields to their corresponding non-focus fields.

```python
mapping = {
    "BillingAccountId": "Organization ID",
    "BillingAccountName": "Organization Name",
    ...
}
```

next we create a `Focus` object, specifying the platform, local billing export file, field mappings (if needed) and any data modifications needed:

```python
from harness_ccm_external_data import Focus

my_data = Focus(
    "MyTestPlatform",
    "my_billing_export.csv",
    mappings={
        "BillingAccountId": "Organization ID",
        "BillingAccountName": "Organization Name",
        ...
    }
    # skip the first n rows of the billing data
    skip_rows=100,
    # you can also specify specific rows to skip
    # skip_rows=[0, 2, 4, 6, 8],
    # apply a multiplier to the cost (account for discounts not shown in the export?)
    cost_multiplier=0.95
    # if the csv is in a non-standard format
    separator=";"
    # apply a function to any column value
    converters={
        "ChargeCategory": lambda x: lower(x)
    }
)
```

now we can render the data to the harness platform format:

```
my_data.render_file("harness_focus_my_billing_export.csv")
```

## development

pull the example focus csv: `curl -LO https://raw.githubusercontent.com/FinOps-Open-Cost-and-Usage-Spec/FOCUS-Sample-Data/refs/heads/main/FOCUS-1.0/focus_sample.csv`

install [poetry](https://python-poetry.org/docs/#installation)

testing: `make test`
