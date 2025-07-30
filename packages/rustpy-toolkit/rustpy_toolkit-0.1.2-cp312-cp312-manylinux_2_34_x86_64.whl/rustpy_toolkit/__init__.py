from . import validation

# Import polars expressions if polars is available
try:
    import polars as pl

    from . import polars_expressions

    # Automatically register the document namespace
    polars_expressions.register_document_namespace()
    __all__ = ["validation", "polars_expressions"]
except ImportError:
    # Polars not available, only expose regular validation
    __all__ = ["validation"]

__version__ = "0.1.2"
