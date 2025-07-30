use pyo3::prelude::*;
use rustalib_core::macd::{MACD};
use rustalib_core::Indicator;

#[pyclass(name = "MACD")]
pub struct PyMACD {
    inner: MACD,
}

#[pymethods]
impl PyMACD {
    #[new]
    pub fn new(fast_period: usize, slow_period: usize, signal_period: usize) -> Self {
        PyMACD {
            inner: MACD::new(fast_period, slow_period, signal_period),
        }
    }

    /// Procesa el próximo precio y devuelve un dict con los valores de MACD
    pub fn next(&mut self, value: f64) -> PyResult<Option<PyMACDOutput>> {
        let result = self.inner.next(value);
        match result {
            Some(output) => Ok(Some(PyMACDOutput {
                macd: output.macd,
                signal: output.signal,
                histogram: output.histogram,
            })),
            None => Ok(None),
        }
    }

    /// Calcula el indicador para toda la serie de datos y devuelve lista de dicts o None
    pub fn calculate_all(&mut self, data: Vec<f64>) -> PyResult<Vec<Option<PyMACDOutput>>> {
        let results = self.inner.calculate_all(&data);
        let py_results = results.into_iter().map(|opt| {
            opt.map(|output| PyMACDOutput {
                macd: output.macd,
                signal: output.signal,
                histogram: output.histogram,
            })
        }).collect();
        Ok(py_results)
    }

    /// Devuelve el último valor calculado
    pub fn value(&self) -> Option<PyMACDOutput> {
        self.inner.value().map(|output| PyMACDOutput {
            macd: output.macd,
            signal: output.signal,
            histogram: output.histogram,
        })
    }

    /// Devuelve todos los valores calculados
    pub fn values(&self) -> Vec<Option<PyMACDOutput>> {
        self.inner.values().iter().map(|opt| {
            opt.as_ref().map(|output| PyMACDOutput {
                macd: output.macd,
                signal: output.signal,
                histogram: output.histogram,
            })
        }).collect()
    }
}

#[pyclass]
#[derive(Clone)]
pub struct PyMACDOutput {
    #[pyo3(get)]
    pub macd: f64,
    #[pyo3(get)]
    pub signal: f64,
    #[pyo3(get)]
    pub histogram: f64,
}

impl std::fmt::Debug for PyMACDOutput {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("MACDOutput")
            .field("macd", &self.macd)
            .field("signal", &self.signal)
            .field("histogram", &self.histogram)
            .finish()
    }
}

impl std::fmt::Display for PyMACDOutput {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "MACDOutput(macd: {:.6}, signal: {:.6}, histogram: {:.6})",
            self.macd, self.signal, self.histogram
        )
    }
}
