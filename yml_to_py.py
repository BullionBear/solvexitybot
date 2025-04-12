# yml_to_py.py

import yaml
import argparse
import pprint
from pathlib import Path

def convert_yml_to_py(input_path: str, output_path: str, variable_name: str = "CONFIG"):
    with open(input_path, "r") as f:
        data = yaml.safe_load(f)

    # Pretty-print Python dictionary to string
    py_content = f"# Auto-generated from {Path(input_path).name}\n\n"
    py_content += f"{variable_name} = "
    py_content += pprint.pformat(data, width=100)
    py_content += "\n"

    with open(output_path, "w") as f:
        f.write(py_content)

    print(f"✅ Generated {output_path} from {input_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert YAML to Python file with variable assignment.")
    parser.add_argument("input", help="Path to input YAML file (e.g. config.yml)")
    parser.add_argument("output", help="Path to output Python file (e.g. const.py)")
    parser.add_argument("--var", default="CONFIG", help="Top-level variable name (default: CONFIG)")

    args = parser.parse_args()
    convert_yml_to_py(args.input, args.output, args.var)
