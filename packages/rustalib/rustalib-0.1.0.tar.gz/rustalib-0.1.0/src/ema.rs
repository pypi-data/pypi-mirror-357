use pyo3::prelude::*;
use rustalib_core::ema::EMA;
use rustalib_core::Indicator;

#[pyclass(name = "EMA")]
pub struct PyEMA {
    inner: EMA,
}

#[pymethods]
impl PyEMA {
    #[new]
    pub fn new(period: usize) -> Self {
        Self {
            inner: EMA::new(period),
        }
    }

    /// Process next price incrementally
    pub fn next(&mut self, value: f64) -> Option<f64> {
        self.inner.next(value)
    }

    /// Calculate EMA over entire historical data
    pub fn calculate_all(&mut self, data: Vec<f64>) -> Vec<Option<f64>> {
        self.inner.calculate_all(&data)
    }

    /// Get last calculated value
    pub fn value(&self) -> Option<f64> {
        self.inner.value()
    }

    /// Get all calculated values
    pub fn values(&self) -> Vec<Option<f64>> {
        self.inner.values().to_vec()
    }

    #[getter]
    pub fn period(&self) -> usize {
        self.inner.period()
    }

    fn __repr__(&self) -> String {
        format!("EMA(period={})", self.inner.period())
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }
}