use ::uuid::Uuid;
use pyo3::{prelude::*, types::PyDict};

// Blake3 key used for hashing.
// UUID: 6ba7b842-9dad-11d1-80b4-00c04fd430c8 as 32-byte key (repeated)
// Inspired by the UUID namespaces values, in case you wonder. But with 42 instead of 10, 11, 12, and 14 at the
// fourth byte (yes 13 is somehow skipped in the RFC 9562).
// As Blake3 requires a 32-byte key, the second half is the same, but inversed.
const BLAKE3_KEY: [u8; 32] = [
    // UUID: 6ba7b842-9dad-11d1-80b4-00c04fd430c8
    0x6b, 0xa7, 0xb8, 0x42, 0x9d, 0xad, 0x11, 0xd1, 0x80, 0xb4, 0x00, 0xc0, 0x4f, 0xd4, 0x30, 0xc8,
    // Same UUID but inversed
    !0x6b, !0xa7, !0xb8, !0x42, !0x9d, !0xad, !0x11, !0xd1, !0x80, !0xb4, !0x00, !0xc0, !0x4f,
    !0xd4, !0x30, !0xc8,
];

/// Computes a hashed UUID.
#[pyfunction]
fn uuid(namespace: &str, name: &str) -> Uuid {
    let buffer_size = namespace.len() + name.len() + 1;
    let mut buffer = Vec::with_capacity(buffer_size);
    buffer.extend_from_slice(namespace.as_bytes());
    buffer.push(30u8); // Record separator (RS) - ASCII 30 (0x1E)
    buffer.extend_from_slice(name.as_bytes());

    let mut hash_output = [0u8; 16];
    let mut hasher = blake3::Hasher::new_keyed(&BLAKE3_KEY);
    hasher.update(&buffer);
    hasher.finalize_xof().fill(&mut hash_output);

    ::uuid::Builder::from_bytes(hash_output)
        .with_variant(::uuid::Variant::RFC4122)
        // Please note that SHA1 is *not* the same as BLAKE3,
        // But it's still a hash, and that what matters here.
        // Custom (8) doesn't imply it's a hash, and it doesn't
        // even have to be unique.
        .with_version(::uuid::Version::Sha1)
        .into_uuid()
}

/// Computes a hashed UUID with metadata.
#[pyfunction]
fn uuid_with_metadata(namespace: &str, name: &str, metadata: Bound<'_, PyDict>) -> PyResult<Uuid> {
    let buffer_size = namespace.len() + name.len() + 1;
    let mut buffer = Vec::with_capacity(buffer_size);
    buffer.extend_from_slice(namespace.as_bytes());
    buffer.push(30u8); // Record separator (RS) - ASCII 30 (0x1E)
    buffer.extend_from_slice(name.as_bytes());

    let mut hash_name_output = [0u8; 4];
    let mut hasher_name = blake3::Hasher::new_keyed(&BLAKE3_KEY);
    hasher_name.update(&buffer);
    hasher_name.finalize_xof().fill(&mut hash_name_output);

    let mut hash_everything_output = [0u8; 12];
    let mut hasher_everything = blake3::Hasher::new_keyed(&BLAKE3_KEY);
    hasher_everything.update(&buffer);

    // Collect metadata items for sorting
    let mut items_with_keys: Vec<_> = Vec::new();
    for (key, value) in metadata.iter() {
        let key_str = key
            .str()
            .map_err(|_| {
                PyErr::new::<pyo3::exceptions::PyTypeError, _>("Failed to convert key to string")
            })?
            .extract::<String>()
            .map_err(|_| {
                PyErr::new::<pyo3::exceptions::PyTypeError, _>("Failed to extract key as string")
            })?;
        items_with_keys.push((key_str, key, value));
    }

    // Sort by key in lexical order
    items_with_keys.sort_by(|a, b| a.0.cmp(&b.0));

    // Iterate through the metadata dictionary in sorted order
    for (key_str, _key, value) in items_with_keys {
        // reset buffer
        buffer.clear();

        // Add a separator before each metadata entry
        buffer.push(30u8); // Record separator (RS) - ASCII 30 (0x1E)

        // Add the key as bytes
        buffer.extend_from_slice(key_str.as_bytes());

        buffer.push(31u8); // Unit separator (US) - ASCII 31 (0x1F)

        // Check Python object type first, then extract
        if value.is_none() {
            buffer.push(0u8); // None type
        } else if value.is_instance_of::<pyo3::types::PyBool>() {
            // Check bool BEFORE int because bool is a subtype of int in Python
            let bool_val = value.extract::<bool>().map_err(|_| {
                PyErr::new::<pyo3::exceptions::PyTypeError, _>("Failed to extract boolean value")
            })?;
            buffer.push(1u8); // Boolean type
            buffer.push(if bool_val { 1u8 } else { 0u8 });
        } else if value.is_instance_of::<pyo3::types::PyBytes>() {
            let bytes = value.extract::<Vec<u8>>().map_err(|_| {
                PyErr::new::<pyo3::exceptions::PyTypeError, _>("Failed to extract bytes")
            })?;
            buffer.push(2u8); // Bytes type
            buffer.extend_from_slice(&bytes);
        } else if value.is_instance_of::<pyo3::types::PyString>() {
            let string_val = value.extract::<String>().map_err(|_| {
                PyErr::new::<pyo3::exceptions::PyTypeError, _>("Failed to extract string")
            })?;
            buffer.push(3u8); // String type
            buffer.extend_from_slice(string_val.as_bytes());
        } else if value.is_instance_of::<pyo3::types::PyInt>() {
            let int_val = value.extract::<i64>().map_err(|_| {
                PyErr::new::<pyo3::exceptions::PyTypeError, _>("Failed to extract integer")
            })?;
            buffer.push(4u8); // Integer type
            buffer.extend_from_slice(&int_val.to_le_bytes());
        } else if value.is_instance_of::<pyo3::types::PyFloat>() {
            let float_val = value.extract::<f64>().map_err(|_| {
                PyErr::new::<pyo3::exceptions::PyTypeError, _>("Failed to extract float")
            })?;
            buffer.push(5u8); // Float type
            buffer.extend_from_slice(&float_val.to_le_bytes());
        } else {
            // For any other type, use Python's str() representation
            let str_repr = value.str().map_err(|_| {
                PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                    "Failed to get string representation of value",
                )
            })?;
            let str_val = str_repr.extract::<String>().map_err(|_| {
                PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                    "Failed to extract string representation",
                )
            })?;
            buffer.push(6u8); // Custom type
            buffer.extend_from_slice(str_val.as_bytes());
        }

        hasher_everything.update(&buffer);
    }

    hasher_everything
        .finalize_xof()
        .fill(&mut hash_everything_output);

    let mut uuid_bytes = [0u8; 16];
    uuid_bytes[..4].copy_from_slice(&hash_name_output);
    uuid_bytes[4..].copy_from_slice(&hash_everything_output);

    Ok(::uuid::Builder::from_bytes(uuid_bytes)
        .with_variant(::uuid::Variant::RFC4122)
        .with_version(::uuid::Version::Sha1)
        .into_uuid())
}

/// A Python module implemented in Rust.
#[pymodule]
fn uuid_blake3(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(crate::uuid, m)?)?;
    m.add_function(wrap_pyfunction!(crate::uuid_with_metadata, m)?)?;
    Ok(())
}
