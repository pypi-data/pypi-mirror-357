use std::borrow::Cow;

use polars::prelude::*;
use pyo3::prelude::*;
use pyo3_polars::derive::polars_expr;
use serde::Deserialize;

/// Validates Brazilian CPF or CNPJ
///
/// Args:
///     document (str): The document to be validated (CPF or CNPJ)
///
/// Returns:
///     dict: A dictionary with the keys:
///         - "valid": bool - Whether the document is valid
///         - "type": str - Document type ("CPF", "CNPJ" or "UNKNOWN")
///         - "formatted": str - Formatted document (if valid)
#[pyfunction]
pub fn validate_document(document: &str) -> PyResult<PyObject>
{
    Python::with_gil(|py| {
        // Remove non-numeric characters
        let clean_doc: String = document.chars().filter(|c| c.is_ascii_digit()).collect();

        let result = match clean_doc.len()
        {
            11 => validate_cpf_internal(&clean_doc),
            14 => validate_cnpj_internal(&clean_doc),
            _ => ValidationResult {
                valid: false,
                doc_type: "UNKNOWN".to_string(),
                formatted: document.to_string(),
            },
        };

        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("valid", result.valid)?;
        dict.set_item("type", result.doc_type)?;
        dict.set_item("formatted", result.formatted)?;

        Ok(dict.into())
    })
}

#[pyfunction]
pub fn validate_cpf(cpf: &str) -> PyResult<bool>
{
    let clean_cpf: String = cpf.chars().filter(|c| c.is_ascii_digit()).collect();
    if clean_cpf.len() != 11
    {
        return Ok(false);
    }
    Ok(validate_cpf_internal(&clean_cpf).valid)
}

#[pyfunction]
pub fn validate_cnpj(cnpj: &str) -> PyResult<bool>
{
    let clean_cnpj: String = cnpj.chars().filter(|c| c.is_ascii_digit()).collect();
    if clean_cnpj.len() != 14
    {
        return Ok(false);
    }
    Ok(validate_cnpj_internal(&clean_cnpj).valid)
}

// Polars expression plugins

#[derive(Deserialize)]
pub struct ValidationKwargs
{
    format_output: bool,
}

/// Polars expression to validate CPF or CNPJ documents
#[polars_expr(output_type=Boolean)]
fn pl_validate_document(inputs: &[Series]) -> PolarsResult<Series>
{
    let ca = inputs[0].str()?;
    let out: BooleanChunked = ca.try_apply_nonnull_values_generic(|value| -> PolarsResult<bool> {
        let clean_doc: String = value.chars().filter(|c| c.is_ascii_digit()).collect();
        Ok(match clean_doc.len()
        {
            11 => validate_cpf_internal(&clean_doc).valid,
            14 => validate_cnpj_internal(&clean_doc).valid,
            _ => false,
        })
    })?;
    Ok(out.into_series())
}

/// Polars expression to validate CPF documents specifically
#[polars_expr(output_type=Boolean)]
fn pl_validate_cpf(inputs: &[Series]) -> PolarsResult<Series>
{
    let ca = inputs[0].str()?;
    let out: BooleanChunked = ca.try_apply_nonnull_values_generic(|value| -> PolarsResult<bool> {
        let clean_cpf: String = value.chars().filter(|c| c.is_ascii_digit()).collect();
        Ok(
            if clean_cpf.len() != 11
            {
                false
            }
            else
            {
                validate_cpf_internal(&clean_cpf).valid
            },
        )
    })?;
    Ok(out.into_series())
}

/// Polars expression to validate CNPJ documents specifically
#[polars_expr(output_type=Boolean)]
fn pl_validate_cnpj(inputs: &[Series]) -> PolarsResult<Series>
{
    let ca = inputs[0].str()?;
    let out: BooleanChunked = ca.try_apply_nonnull_values_generic(|value| -> PolarsResult<bool> {
        let clean_cnpj: String = value.chars().filter(|c| c.is_ascii_digit()).collect();
        Ok(
            if clean_cnpj.len() != 14
            {
                false
            }
            else
            {
                validate_cnpj_internal(&clean_cnpj).valid
            },
        )
    })?;
    Ok(out.into_series())
}

/// Polars expression to format valid CPF or CNPJ documents
#[polars_expr(output_type=String)]
fn pl_format_document(inputs: &[Series]) -> PolarsResult<Series>
{
    let ca = inputs[0].str()?;
    let out: StringChunked = ca.apply_into_string_amortized(|value, output| {
        let clean_doc: String = value.chars().filter(|c| c.is_ascii_digit()).collect();
        let result = match clean_doc.len()
        {
            11 => validate_cpf_internal(&clean_doc),
            14 => validate_cnpj_internal(&clean_doc),
            _ => ValidationResult {
                valid: false,
                doc_type: "UNKNOWN".to_string(),
                formatted: value.to_string(),
            },
        };

        let formatted = if result.valid { result.formatted } else { value.to_string() };
        output.push_str(&formatted);
    });
    Ok(out.into_series())
}

/// Polars expression to get document type (CPF, CNPJ, or UNKNOWN)
#[polars_expr(output_type=String)]
fn pl_document_type(inputs: &[Series]) -> PolarsResult<Series>
{
    let ca = inputs[0].str()?;
    let out: StringChunked = ca.try_apply_nonnull_values_generic(|value| -> PolarsResult<String> {
        let clean_doc: String = value.chars().filter(|c| c.is_ascii_digit()).collect();
        Ok(match clean_doc.len()
        {
            11 => "CPF".to_string(),
            14 => "CNPJ".to_string(),
            _ => "UNKNOWN".to_string(),
        })
    })?;
    Ok(out.into_series())
}

struct ValidationResult
{
    valid: bool,
    doc_type: String,
    formatted: String,
}

fn validate_cpf_internal(cpf: &str) -> ValidationResult
{
    if cpf.len() != 11
    {
        return ValidationResult {
            valid: false,
            doc_type: "CPF".to_string(),
            formatted: cpf.to_string(),
        };
    }

    // Checks if all digits are the same
    if cpf.chars().all(|c| c == cpf.chars().next().unwrap())
    {
        return ValidationResult {
            valid: false,
            doc_type: "CPF".to_string(),
            formatted: cpf.to_string(),
        };
    }

    let digits: Vec<u32> = cpf.chars().map(|c| c.to_digit(10).unwrap()).collect();

    // Calculates first check digit
    let mut sum = 0;
    for i in 0..9
    {
        sum += digits[i] * (10 - i as u32);
    }
    let remainder = sum % 11;
    let first_digit = if remainder < 2 { 0 } else { 11 - remainder };

    // Calculates second check digit
    sum = 0;
    for i in 0..10
    {
        sum += digits[i] * (11 - i as u32);
    }
    let remainder = sum % 11;
    let second_digit = if remainder < 2 { 0 } else { 11 - remainder };

    let is_valid = digits[9] == first_digit && digits[10] == second_digit;

    ValidationResult {
        valid: is_valid,
        doc_type: "CPF".to_string(),
        formatted: if is_valid
        {
            format!("{}.{}.{}-{}", &cpf[0..3], &cpf[3..6], &cpf[6..9], &cpf[9..11])
        }
        else
        {
            cpf.to_string()
        },
    }
}

fn validate_cnpj_internal(cnpj: &str) -> ValidationResult
{
    if cnpj.len() != 14
    {
        return ValidationResult {
            valid: false,
            doc_type: "CNPJ".to_string(),
            formatted: cnpj.to_string(),
        };
    }

    let digits: Vec<u32> = cnpj.chars().map(|c| c.to_digit(10).unwrap()).collect();

    // Calculates first check digit
    let weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
    let mut sum = 0;
    for i in 0..12
    {
        sum += digits[i] * weights1[i];
    }
    let remainder = sum % 11;
    let first_digit = if remainder < 2 { 0 } else { 11 - remainder };

    // Calculates second check digit
    let weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
    sum = 0;
    for i in 0..13
    {
        sum += digits[i] * weights2[i];
    }
    let remainder = sum % 11;
    let second_digit = if remainder < 2 { 0 } else { 11 - remainder };

    let is_valid = digits[12] == first_digit && digits[13] == second_digit;

    ValidationResult {
        valid: is_valid,
        doc_type: "CNPJ".to_string(),
        formatted: if is_valid
        {
            format!(
                "{}.{}.{}/{}-{}",
                &cnpj[0..2],
                &cnpj[2..5],
                &cnpj[5..8],
                &cnpj[8..12],
                &cnpj[12..14]
            )
        }
        else
        {
            cnpj.to_string()
        },
    }
}

pub fn register_module(m: &Bound<'_, PyModule>) -> PyResult<()>
{
    m.add_function(wrap_pyfunction!(validate_document, m)?)?;
    m.add_function(wrap_pyfunction!(validate_cpf, m)?)?;
    m.add_function(wrap_pyfunction!(validate_cnpj, m)?)?;
    Ok(())
}
