from typing import Any, Dict

def validate_document(document: str) -> Dict[str, Any]:
    """
    Valida CPF ou CNPJ brasileiros

    Args:
        document: O documento a ser validado (CPF ou CNPJ)

    Returns:
        Dict com as chaves:
        - "valid": bool - Se o documento é válido
        - "type": str - Tipo do documento ("CPF", "CNPJ" ou "UNKNOWN")
        - "formatted": str - Documento formatado (se válido)
    """
    ...

def validate_cpf(cpf: str) -> bool:
    """
    Valida CPF brasileiro

    Args:
        cpf: CPF a ser validado

    Returns:
        True se válido, False caso contrário
    """
    ...

def validate_cnpj(cnpj: str) -> bool:
    """
    Valida CNPJ brasileiro

    Args:
        cnpj: CNPJ a ser validado

    Returns:
        True se válido, False caso contrário
    """
    ...

__all__ = [
    "validate_document",
    "validate_cpf",
    "validate_cnpj",
]
