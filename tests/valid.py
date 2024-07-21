import json
import sys

REQUIRED_BOOLEAN_FIELDS = [
    "Power.USB_Power",
    "Power.Battery_Compatible",
    "Control.crmx",
    "Control.RDM",
    "Control.Ethernet",
    "Control.5_Pin_DMX",
    "Control.3_Pin_DMX",
]


def validate_data(data):
    errors = []
    warnings = []

    for field in REQUIRED_BOOLEAN_FIELDS:
        keys = field.split(".")
        nested_data = data
        for key in keys:
            if key in nested_data:
                nested_data = nested_data[key]
            else:
                errors.append(f"Missing required boolean field: {field}")
                break
        else:
            if not isinstance(nested_data, bool):
                errors.append(f"Invalid type for field {field}. Expected boolean.")

    optional_string_fields = [
        key for key, value in data.items() if isinstance(value, str)
    ]
    for field in optional_string_fields:
        if not data[field]:
            warnings.append(f"Empty string field: {field}")

    return errors, warnings


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_data.py <data_file.json>")
        sys.exit(1)

    data_file = sys.argv[1]
    with open(data_file) as f:
        data = json.load(f)

    validation_errors, validation_warnings = validate_data(data)

    if validation_errors:
        print("Validation Errors Found:")
        for error in validation_errors:
            print(f" - {error}")
        sys.exit(1)

    if validation_warnings:
        print("Validation Warnings Found:")
        for warning in validation_warnings:
            print(f" - {warning}")

    print("All validations passed!")
    sys.exit(0)
