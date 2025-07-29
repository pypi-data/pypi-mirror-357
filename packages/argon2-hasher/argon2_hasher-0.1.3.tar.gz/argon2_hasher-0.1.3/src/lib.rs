use pyo3::prelude::*;
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::types::PyModule;

use argon2::{
    password_hash::{PasswordHash, PasswordHasher, PasswordVerifier, SaltString},
    Algorithm, Argon2, Params, Version,
};

use rand::rngs::OsRng;
use once_cell::sync::Lazy;
use num_cpus;

/// -------- 1 ▸ a single, tuned, SIMD-enabled Argon2 instance -------------
static ARGON2: Lazy<Argon2<'static>> = Lazy::new(|| {
    // ❶ choose cost parameters roughly equivalent to bcrypt cost-12
    //     memory  =  8 MiB
    //     iters   =  2
    //     lanes   =  #cpu cores  (parallel hash → ≈ linear speed-up)
    //     tag_len =  default (32 bytes)
    let params = Params::new(8 * 1024, 2, num_cpus::get() as u32, None)
        .expect("invalid Argon2 parameters");

    Argon2::new(Algorithm::Argon2id, Version::V0x13, params)
});

/// Python-visible class ----------------------------------------------------
#[pyclass]
pub struct Argon2Hasher;

#[pymethods]
impl Argon2Hasher {
    /// Hash a password.
    ///
    /// `salt` is optional.  When `None`, 16 random bytes are generated.
    #[staticmethod]
    #[pyo3(signature = (plain, salt=None))]
    pub fn hash(plain: &str, salt: Option<&str>) -> PyResult<String> {
        // -------- 2 ▸ pick or generate a salt ----------------------------
        let salt = match salt {
            Some(s) => SaltString::from_b64(s)
                .map_err(|e| PyValueError::new_err(e.to_string()))?,
            None => {
                let mut rng = OsRng;
                SaltString::generate(&mut rng)       // 16 random bytes
            }
        };

        // -------- 3 ▸ hash with the static Argon2 instance ---------------
        ARGON2
            .hash_password(plain.as_bytes(), &salt)
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))
            .map(|hp| hp.to_string())
    }

    /// Verify a plaintext against a PHC-formatted hash.
    #[staticmethod]
    pub fn verify(hashed: &str, plain: &str) -> PyResult<bool> {
        let parsed = PasswordHash::new(hashed)
            .map_err(|e| PyValueError::new_err(e.to_string()))?;

        Ok(ARGON2
            .verify_password(plain.as_bytes(), &parsed)
            .is_ok())
    }
}

/// Module init:  `import argon2_hasher`
#[pymodule]
fn argon2_hasher(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Argon2Hasher>()?;
    Ok(())
}

