import json
import os
from copy import deepcopy

import pandas as pd
import re


INPUT_FILE = "Data/TC Data Check.xlsx"


# --------------------------------------------------
# Helpers
# --------------------------------------------------

# def normalize_columns(df):
#     """
#     Make column names case-insensitive
#     and ignore spaces and dots. Will try more aggressive normalization below.
#     """

#     df.columns = [
#         str(col)
#         .strip()
#         .lower()
#         .replace(" ", "")
#         .replace(".", "")
#         for col in df.columns
#     ]

#     return df

def normalize_columns(df):

    df.columns = [
        re.sub(
            r"[^a-z0-9]",
            "",
            str(col).lower()
        )
        for col in df.columns
    ]

    return df


def validate_columns(df):

    required_columns = [
        "identifier",
        "answertype",
        "answerschema",
        "options"
    ]

    missing = [
        col
        for col in required_columns
        if col not in df.columns
    ]

    if missing:

        raise Exception(
            "Missing required columns:\n"
            + "\n".join(missing)
        )


def normalize_answer_type(
    schema_type,
    property_schema
):
    """
    Convert schema type into
    checker answerType.
    """

    if schema_type in (
        "string",
        "number",
        "integer"
    ):

        return (
            "text",
            ""
        )

    if schema_type == "boolean":

        return (
            "options",
            json.dumps(
                ["true", "false"]
            )
        )

    if schema_type == "array":

        items = property_schema.get(
            "items",
            {}
        )

        enum_values = items.get(
            "enum"
        )

        if enum_values:

            return (
                "options",
                json.dumps(
                    enum_values,
                    ensure_ascii=False
                )
            )

        return (
            "text",
            ""
        )

    return (
        None,
        None
    )


def get_properties(answer_schema):

    if pd.isna(answer_schema):
        return {}

    try:

        schema = json.loads(
            str(answer_schema)
        )

        # return schema.get(
        #     "properties",
        #     {}
        # )
    
        # Structure A

        if "properties" in schema:

            return schema["properties"]

        # Structure B
        # Object List

        if (
            "items" in schema
            and isinstance(
                schema["items"],
                dict
            )
        ):

            items = schema["items"]

            if "properties" in items:

                return items["properties"]

        return {}

    except Exception:

        return {}


def get_top_level_schema_type(answer_schema):

    if pd.isna(answer_schema):
        return None

    try:
        schema = json.loads(str(answer_schema))
        return schema.get("type")

    except Exception:
        return None


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print(
        f"Reading:\n{INPUT_FILE}"
    )

    df = pd.read_excel(
        INPUT_FILE
    )

    df = normalize_columns(df)

    print("\nNormalized columns:")
    print(df.columns.tolist())

    validate_columns(df)

    new_rows = []

    object_count = 0
    warning_count = 0
    added_rows = 0

    for _, row in df.iterrows():

        answer_type = str(
            row.get(
                "answertype",
                ""
            )
        ).strip()

        identifier = row.get(
            "identifier",
            ""
        )

        original_options = row.get(
            "options",
            ""
        )

        # ----------------------------------
        # OBJECT / OBJECT LIST
        # ----------------------------------

        if answer_type.lower() in (
            "object",
            "object list"
        ):

            object_count += 1

            properties = get_properties(
                row.get(
                    "answerschema",
                    ""
                )
            )

            schema_type = get_top_level_schema_type(
                row.get(
                    "answerschema",
                    ""
                )
            )

            if not properties:

                if schema_type == "array":

                    new_row = deepcopy(
                        row.to_dict()
                    )

                    new_row["item"] = ""

                    new_row["source_answertype"] = answer_type

                    new_row["identifier_options"] = original_options

                    new_row["schema_details"] = ""

                    new_row["answertype"] = "text"

                    new_row["allows_multiple_values"] = "Yes"

                    new_row["options"] = ""

                    new_rows.append(
                        new_row
                    )

                    continue

                print(
                    f"\nWARNING"
                    f"\nIdentifier: "
                    f"{identifier}"
                    f"\nNo properties found."
                )

                warning_count += 1
                continue

            for (
                item_name,
                property_schema
            ) in properties.items():

                schema_type = (
                    property_schema
                    .get(
                        "type"
                    )
                )

                mapped_type, options = (
                    normalize_answer_type(
                        schema_type,
                        property_schema
                    )
                )

                if mapped_type is None:

                    print(
                        f"\nWARNING"
                        f"\nIdentifier: "
                        f"{identifier}"
                        f"\nItem: "
                        f"{item_name}"
                        f"\nUnsupported type: "
                        f"{schema_type}"
                    )

                    warning_count += 1

                    mapped_type = "text"
                    options = ""

                new_row = deepcopy(
                    row.to_dict()
                )

                new_row[
                    "item"
                ] = item_name

                new_row[
                    "source_answertype"
                ] = answer_type

                new_row[
                    "identifier_options"
                ] = original_options

                new_row["allows_multiple_values"] = (
                    "Yes"
                    if answer_type.lower() == "object list"
                    else ""
                )

                new_row[
                    "answertype"
                ] = mapped_type

                new_row[
                    "options"
                ] = options

                new_rows.append(
                    new_row
                )

                added_rows += 1

        # ----------------------------------
        # NORMAL ROWS
        # ----------------------------------

        else:

            new_row = deepcopy(
                row.to_dict()
            )

            new_row[
                "item"
            ] = ""

            new_row[
                "source_answertype"
            ] = answer_type

            new_row[
                "identifier_options"
            ] = original_options

            new_row["schema_details"] = ""

            schema_type = get_top_level_schema_type(
                row.get(
                    "answerschema",
                    ""
                )
            )

            if schema_type == "array":

                new_row["allows_multiple_values"] = "Yes"

            else:

                new_row["allows_multiple_values"] = ""

            new_row[
                "allows_multiple_values"
            ] = ""

            if answer_type.lower() == "boolean":

                new_row[
                    "answertype"
                ] = "options"

                new_row[
                    "options"
                ] = json.dumps(
                    [
                        "true",
                        "false"
                    ]
                )

            elif answer_type.lower() in (
                "option",
                "options"
            ):

                new_row[
                    "options"
                ] = original_options

            else:

                new_row[
                    "options"
                ] = ""

            new_rows.append(
                new_row
            )

    output_df = pd.DataFrame(
        new_rows
    )

    output_file = (
        os.path.splitext(
            INPUT_FILE
        )[0]
        + "_Expanded.xlsx"
    )

    desired_order = []

    for col in output_df.columns:

        if col not in (
            "allows_multiple_values",
            "options"
        ):
            desired_order.append(col)

    desired_order.extend(
        [
            "allows_multiple_values",
            "options"
        ]
    )

    output_df = output_df[
        desired_order
    ]

    output_df.to_excel(
        output_file,
        index=False
    )

    print("\n")
    print("=" * 60)

    print(
        f"Rows read: "
        f"{len(df)}"
    )

    print(
        f"Objects expanded: "
        f"{object_count}"
    )

    print(
        f"Additional rows created: "
        f"{added_rows}"
    )

    print(
        f"Warnings: "
        f"{warning_count}"
    )

    print(
        f"\nOutput:\n"
        f"{output_file}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()