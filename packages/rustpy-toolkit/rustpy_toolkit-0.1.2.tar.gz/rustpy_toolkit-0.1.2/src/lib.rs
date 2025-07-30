use pyo3::prelude::*;

// Modules organized by functionality
mod validation;

#[pymodule]
#[pyo3(name = "rustpy_toolkit")]
fn rustpy_toolkit(m: &Bound<'_, PyModule>) -> PyResult<()>
{
    // Validation submodule
    let validation_module = PyModule::new(m.py(), "validation")?;
    validation::register_module(&validation_module)?;
    m.add_submodule(&validation_module)?;

    // Convenience functions in the main module
    // CPF/CNPJ validation
    m.add_function(wrap_pyfunction!(validation::cpf_cnpj::validate_document, m)?)?;
    m.add_function(wrap_pyfunction!(validation::cpf_cnpj::validate_cpf, m)?)?;
    m.add_function(wrap_pyfunction!(validation::cpf_cnpj::validate_cnpj, m)?)?;

    Ok(())
}
