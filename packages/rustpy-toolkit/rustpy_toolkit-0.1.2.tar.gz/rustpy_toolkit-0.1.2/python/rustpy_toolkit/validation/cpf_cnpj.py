try:
    from ..rustpy_toolkit import validation as _validation_rust

    # Re-exporta as funções do módulo Rust
    validate_document = _validation_rust.cpf_cnpj.validate_document
    validate_cpf = _validation_rust.cpf_cnpj.validate_cpf
    validate_cnpj = _validation_rust.cpf_cnpj.validate_cnpj
except ImportError:
    # Fallback: try direct import from the main module
    try:
        from .. import rust_modules as _rust_mod

        validate_document = _rust_mod.validate_document
        validate_cpf = _rust_mod.validate_cpf
        validate_cnpj = _rust_mod.validate_cnpj
    except ImportError:
        raise ImportError("Could not import Rust functions. Make sure the module is properly compiled.")

__all__ = [
    "validate_document",
    "validate_cpf",
    "validate_cnpj",
]
