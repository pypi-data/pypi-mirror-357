# Rust Modules

Este diretório contém os módulos Rust organizados para operações de data mining.

## Estrutura

```
rust_modules/
├── Cargo.toml                    # Configuração do projeto Rust
├── src/                          # Código fonte Rust
│   ├── lib.rs                   # Módulo principal
│   └── validation/              # Módulo de validação
│       ├── mod.rs              # Módulo de validação principal
│       └── cpf_cnpj.rs         # Validação de CPF/CNPJ
└── python_bindings/             # Bindings Python
    └── rust_modules/
        ├── __init__.py         # Módulo principal Python
        ├── __init__.pyi        # Definições de tipos
        ├── py.typed            # Marcador de suporte a tipos
        └── validation.py       # Módulo de validação Python
```

## Funcionalidades

### Validação de Documentos

- **CPF**: Validação completa com formatação
- **CNPJ**: Validação completa com formatação
- **Documento genérico**: Detecta automaticamente o tipo

## Uso

### Importação simples

```python
from rust_modules import validate_cpf, validate_cnpj, validate_document

# Validação simples
is_valid = validate_cpf("11144477735")
is_valid = validate_cnpj("11222333000181")

# Validação com detalhes
result = validate_document("11144477735")
# {'valid': True, 'type': 'CPF', 'formatted': '111.444.777-35'}
```

### Importação por módulos

```python
from rust_modules import validation
from rust_modules.validation import cpf_cnpj

# Usando submódulos
result = validation.validate_document("11144477735")
result = cpf_cnpj.validate_document("11144477735")
```

## Compilação

Para compilar os módulos:

```bash
uv run maturin develop
```

## Testes

Para executar os testes:

```bash
uv run python test_rust_modules_new.py
```
