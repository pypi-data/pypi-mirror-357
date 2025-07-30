#!/usr/bin/env python3
"""
Test script for rustpy-toolkit CPF/CNPJ validation with Polars expressions.

This script demonstrates both regular validation functions and Polars expression plugins.
"""

import rustpy_toolkit


def test_regular_validation():
    """Test regular validation functions."""
    print("=== Testing Regular Validation Functions ===")

    # Test documents
    test_docs = [
        "11144477735",  # Valid CPF
        "12345678901",  # Invalid CPF
        "11222333000181",  # Valid CNPJ
        "12345678000190",  # Invalid CNPJ
        "123",  # Invalid length
    ]

    for doc in test_docs:
        result = rustpy_toolkit.validation.cpf_cnpj.validate_document(doc)
        print(f"Document: {doc}")
        print(f"  Valid: {result['valid']}")
        print(f"  Type: {result['type']}")
        print(f"  Formatted: {result['formatted']}")
        print()


def test_polars_expressions():
    """Test Polars expression plugins."""
    try:
        import polars as pl
        from rustpy_toolkit import polars_expressions

        print("=== Testing Polars Expression Plugins ===")

        # Create test DataFrame
        df = pl.DataFrame(
            {
                "documents": [
                    "11144477735",  # Valid CPF
                    "111.444.777-35",  # Valid CPF with formatting
                    "12345678901",  # Invalid CPF
                    "11222333000181",  # Valid CNPJ
                    "11.222.333/0001-81",  # Valid CNPJ with formatting
                    "12345678000190",  # Invalid CNPJ
                    "123",  # Invalid length
                    "",  # Empty string
                ]
            }
        )

        print("Original DataFrame:")
        print(df)
        print()

        # Test validation functions
        result_df = df.with_columns(
            [
                polars_expressions.validate_document("documents").alias("is_valid"),
                polars_expressions.validate_cpf("documents").alias("is_valid_cpf"),
                polars_expressions.validate_cnpj("documents").alias("is_valid_cnpj"),
                polars_expressions.format_document("documents").alias("formatted"),
                polars_expressions.document_type("documents").alias("doc_type"),
            ]
        )

        print("DataFrame with validation results:")
        print(result_df)
        print()

        # Test namespace syntax
        namespace_df = df.with_columns(
            [
                pl.col("documents").document.validate().alias("valid_namespace"),
                pl.col("documents").document.format().alias("formatted_namespace"),
                pl.col("documents").document.type().alias("type_namespace"),
            ]
        )

        print("DataFrame with namespace syntax:")
        print(namespace_df)
        print()

        # Performance comparison example
        print("=== Performance Test ===")

        # Create larger dataset for performance testing
        large_df = pl.DataFrame({"documents": ["11144477735", "11222333000181", "12345678901"] * 10000})

        print(f"Testing with {len(large_df)} rows...")

        # Time the Polars expression
        import time

        start_time = time.time()
        result = large_df.with_columns(polars_expressions.validate_document("documents").alias("is_valid"))
        polars_time = time.time() - start_time

        print(f"Polars expression time: {polars_time:.4f} seconds")
        print(f"Processed {len(large_df)} documents")
        print(f"Rate: {len(large_df) / polars_time:.0f} documents/second")

    except ImportError:
        print("Polars not available. Install with: pip install polars")
    except Exception as e:
        print(f"Error testing Polars expressions: {e}")


def main():
    """Main test function."""
    print("Testing rustpy-toolkit CPF/CNPJ validation\n")

    # Test regular validation
    test_regular_validation()

    # Test Polars expressions
    test_polars_expressions()


if __name__ == "__main__":
    main()
