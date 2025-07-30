"""
Polars expression plugins for CPF/CNPJ validation.

This module provides Polars expression functions that can be used within
Polars DataFrames for efficient CPF and CNPJ validation operations.
"""

from pathlib import Path
from typing import TYPE_CHECKING

import polars as pl
from polars._typing import IntoExpr
from polars.plugins import register_plugin_function

if TYPE_CHECKING:
    pass

# Path to the compiled plugin
PLUGIN_PATH = Path(__file__).parent


def validate_document(expr: IntoExpr) -> pl.Expr:
    """
    Validate Brazilian CPF or CNPJ documents using Polars expressions.

    This function creates a Polars expression that validates CPF (11 digits)
    or CNPJ (14 digits) documents, returning True for valid documents and
    False for invalid ones.

    Args:
        expr: Column expression containing the documents to validate

    Returns:
        Polars expression that returns boolean validation results

    Example:
        >>> import polars as pl
        >>> from rustpy_toolkit.polars_expressions import validate_document
        >>> df = pl.DataFrame({"documents": ["12345678901", "12.345.678/0001-90"]})
        >>> df.with_columns(valid=validate_document("documents"))
    """
    return register_plugin_function(
        plugin_path=PLUGIN_PATH,
        function_name="pl_validate_document",
        args=expr,
        is_elementwise=True,
    )


def validate_cpf(expr: IntoExpr) -> pl.Expr:
    """
    Validate Brazilian CPF documents using Polars expressions.

    This function creates a Polars expression that specifically validates
    CPF documents (11 digits), returning True for valid CPFs and False
    for invalid ones.

    Args:
        expr: Column expression containing the CPF documents to validate

    Returns:
        Polars expression that returns boolean validation results

    Example:
        >>> import polars as pl
        >>> from rustpy_toolkit.polars_expressions import validate_cpf
        >>> df = pl.DataFrame({"cpfs": ["12345678901", "111.111.111-11"]})
        >>> df.with_columns(valid_cpf=validate_cpf("cpfs"))
    """
    return register_plugin_function(
        plugin_path=PLUGIN_PATH,
        function_name="pl_validate_cpf",
        args=expr,
        is_elementwise=True,
    )


def validate_cnpj(expr: IntoExpr) -> pl.Expr:
    """
    Validate Brazilian CNPJ documents using Polars expressions.

    This function creates a Polars expression that specifically validates
    CNPJ documents (14 digits), returning True for valid CNPJs and False
    for invalid ones.

    Args:
        expr: Column expression containing the CNPJ documents to validate

    Returns:
        Polars expression that returns boolean validation results

    Example:
        >>> import polars as pl
        >>> from rustpy_toolkit.polars_expressions import validate_cnpj
        >>> df = pl.DataFrame({"cnpjs": ["12345678000190", "11.111.111/0001-11"]})
        >>> df.with_columns(valid_cnpj=validate_cnpj("cnpjs"))
    """
    return register_plugin_function(
        plugin_path=PLUGIN_PATH,
        function_name="pl_validate_cnpj",
        args=expr,
        is_elementwise=True,
    )


def format_document(expr: IntoExpr) -> pl.Expr:
    """
    Format valid Brazilian CPF or CNPJ documents using Polars expressions.

    This function creates a Polars expression that formats valid CPF/CNPJ
    documents with the standard Brazilian formatting (masks). Invalid
    documents are returned unchanged.

    Args:
        expr: Column expression containing the documents to format

    Returns:
        Polars expression that returns formatted documents

    Example:
        >>> import polars as pl
        >>> from rustpy_toolkit.polars_expressions import format_document
        >>> df = pl.DataFrame({"documents": ["12345678901", "12345678000190"]})
        >>> df.with_columns(formatted=format_document("documents"))
    """
    return register_plugin_function(
        plugin_path=PLUGIN_PATH,
        function_name="pl_format_document",
        args=expr,
        is_elementwise=True,
    )


def document_type(expr: IntoExpr) -> pl.Expr:
    """
    Get the document type (CPF, CNPJ, or UNKNOWN) using Polars expressions.

    This function creates a Polars expression that identifies the type of
    Brazilian document based on the number of digits: 11 digits = CPF,
    14 digits = CNPJ, other = UNKNOWN.

    Args:
        expr: Column expression containing the documents to classify

    Returns:
        Polars expression that returns document type strings

    Example:
        >>> import polars as pl
        >>> from rustpy_toolkit.polars_expressions import document_type
        >>> df = pl.DataFrame({"documents": ["12345678901", "12345678000190", "123"]})
        >>> df.with_columns(doc_type=document_type("documents"))
    """
    return register_plugin_function(
        plugin_path=PLUGIN_PATH,
        function_name="pl_document_type",
        args=expr,
        is_elementwise=True,
    )


class DocumentValidationExpr:
    """
    Custom namespace for document validation expressions.

    This class provides a namespace that can be registered with Polars
    to enable syntax like: pl.col("documents").document.validate()
    """

    def __init__(self, expr: pl.Expr):
        self._expr = expr

    def validate(self) -> pl.Expr:
        """Validate CPF or CNPJ documents."""
        return validate_document(self._expr)

    def validate_cpf(self) -> pl.Expr:
        """Validate CPF documents specifically."""
        return validate_cpf(self._expr)

    def validate_cnpj(self) -> pl.Expr:
        """Validate CNPJ documents specifically."""
        return validate_cnpj(self._expr)

    def format(self) -> pl.Expr:
        """Format valid documents with Brazilian standard formatting."""
        return format_document(self._expr)

    def type(self) -> pl.Expr:
        """Get document type (CPF, CNPJ, or UNKNOWN)."""
        return document_type(self._expr)


def register_document_namespace():
    """
    Register the document validation namespace with Polars.

    After calling this function, you can use expressions like:
    pl.col("documents").document.validate()
    """
    try:
        pl.api.register_expr_namespace("document")(DocumentValidationExpr)
    except Exception:
        # Namespace might already be registered
        pass
