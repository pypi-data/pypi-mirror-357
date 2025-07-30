use pyo3::prelude::*;
use rustalib_core::{sma::SMA, Indicator};

/// Clase Python que implementa el indicador Simple Moving Average (SMA).
#[pyclass(name = "SMA")]
pub struct PySMA {
    inner: SMA,
}

#[pymethods]
impl PySMA {
    
    /// Crea un nuevo indicador SMA con el periodo especificado.
    #[new]
    fn new(period: usize) -> Self {
        PySMA {
            inner: SMA::new(period),
        }
    }

    /// Añade un nuevo valor y calcula el SMA incremental.
    fn next(&mut self, value: f64) -> Option<f64> {
        self.inner.next(value)
    }

    /// Calcula el SMA para toda una serie de datos históricos.
    fn calculate_all(&mut self, data: Vec<f64>) -> Vec<Option<f64>> {
        self.inner.calculate_all(&data)
    }

    /// Obtiene el último valor calculado del SMA.
    fn value(&self) -> Option<f64> {
        self.inner.value()
    }

    /// Obtiene todos los valores calculados después de una ejecución.
    fn values(&self) -> Vec<Option<f64>> {
        self.inner.values().to_vec()
    }

    /// Representación en string del objeto para debugging.
    fn __repr__(&self) -> String {
        format!("SMA()")
    }

    /// Representación en string del objeto.
    fn __str__(&self) -> String {
        self.__repr__()
    }
}