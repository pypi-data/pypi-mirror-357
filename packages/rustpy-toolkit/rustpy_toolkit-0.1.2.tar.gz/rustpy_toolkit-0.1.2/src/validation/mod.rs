use pyo3::prelude::*;

pub mod cpf_cnpj;

pub fn register_module(m: &Bound<'_, PyModule>) -> PyResult<()>
{
    // CPF/CNPJ submodule
    let cpf_cnpj_module = PyModule::new(m.py(), "cpf_cnpj")?;
    cpf_cnpj::register_module(&cpf_cnpj_module)?;
    m.add_submodule(&cpf_cnpj_module)?;

    // Convenience functions in the validation module
    m.add_function(wrap_pyfunction!(cpf_cnpj::validate_document, m)?)?;
    m.add_function(wrap_pyfunction!(cpf_cnpj::validate_cpf, m)?)?;
    m.add_function(wrap_pyfunction!(cpf_cnpj::validate_cnpj, m)?)?;

    Ok(())
}
