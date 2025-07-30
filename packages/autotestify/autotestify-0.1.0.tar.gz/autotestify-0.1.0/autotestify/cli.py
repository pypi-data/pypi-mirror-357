import argparse
from autotestify.generator import generate_tests

def main():
    parser = argparse.ArgumentParser(description="Auto-generate tests for Python code.")
    parser.add_argument("filepath", help="Path to the Python file")
    args = parser.parse_args()

    test_code = generate_tests(args.filepath)
    test_file = f"test_{args.filepath.split('/')[-1]}"
    with open(test_file, "w") as f:
        f.write(test_code)
    print(f"✅ Created {test_file}")
