from typing import Dict, Sequence

import pandas as pd

HARNESS_FIELDS = [
    "BillingAccountId",
    "BillingAccountName",
    "BillingPeriodEnd",
    "BillingPeriodStart",
    "ChargeCategory",
    "ChargePeriodStart",
    "ChargePeriodEnd",
    "ConsumedQuantity",
    "EffectiveCost",
    "ProviderName",
    "ResourceId",
    "RegionName",
    "ServiceName",
    "SubAccountId",
    "SkuId",
    "SubAccountName",
    "Tags",
]

file_limit = 20000000


class Focus:
    """
    Load in a cloud provider focus billing export
    Apply modifications to the data as needed for processing
    Render a CSV that fits Harness' standards for external data ingestion
    """

    def __init__(
        self,
        provider: str,
        filename: str,
        mapping: Dict[str, str] = {},
        separator: str = ",",
        skip_rows: int | Sequence[int] = None,
        cost_multiplier: float = 1.0,
        converters: Dict[str, callable] = {},
        validate: bool = True,
    ):
        self.provider = provider
        self.cost_multiplier = cost_multiplier
        self.converters = converters
        self.harness_focus_content: pd.DataFrame = None

        # sanitize mappings
        mapping = mapping if mapping else {}
        self.mapping = {**{x: x for x in HARNESS_FIELDS}, **mapping}

        # restrict fields to ones supported by ccm
        # allow disabling verification for instances when ccm moves faster than the code
        if validate:
            for field in mapping:
                if field not in HARNESS_FIELDS:
                    print(
                        f"WARNING: Field {field} is not a recognized harness focus field. Will be ignored"
                    )
                    del self.mapping[field]

        baseline_converters = {
            # apply given cost multiplier
            self.mapping["EffectiveCost"]: lambda x: pd.to_numeric(x) * cost_multiplier,
            # make sure provider is set
            self.mapping["ProviderName"]: lambda x: self.provider if not x else x,
        }

        self.billing_content = pd.read_csv(
            filename,
            sep=separator,
            engine="python",
            skiprows=skip_rows,
            # any converters specified by the user will override built-in ones
            converters={**baseline_converters, **converters},
        )

    def render(self) -> pd.DataFrame:
        """
        Create the Harness-aligned FOCUS CSV
        """

        self.harness_focus_content = pd.DataFrame()
        for focus_field, source_field in self.mapping.items():
            if source_field in self.billing_content.columns:
                self.harness_focus_content[focus_field] = self.billing_content[
                    source_field
                ]
            else:
                # Default value for missing columns
                self.harness_focus_content[focus_field] = source_field

        return self.harness_focus_content

    def render_file(self, filename: str):
        """
        Save the Harness-CSV to a file
        """

        if self.harness_focus_content is None:
            self.render().to_csv(filename, index=False)
        else:
            self.harness_focus_content.to_csv(filename, index=False)
