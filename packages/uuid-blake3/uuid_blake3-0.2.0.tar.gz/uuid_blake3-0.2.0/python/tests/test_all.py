import pytest
import uuid_blake3
import uuid


def test_uuid():

    name = "example_a"
    namespace = "namespace_a"
    other_name = "example_b"
    other_namespace = "namespace_b"

    uuid_1 = uuid_blake3.uuid(namespace, name)
    uuid_2 = uuid_blake3.uuid(namespace, name)

    assert isinstance(uuid_1, uuid.UUID)
    assert uuid_1 == uuid.UUID("b6839270-3331-531b-99b5-e67404c687cb")  # Example UUID for testing
    assert uuid_1 == uuid_2, "UUIDs should be equal for the same name and namespace"

    uuid_3 = uuid_blake3.uuid(other_namespace, name)
    assert uuid_1 != uuid_3, "UUIDs should be different for different namespaces"

    uuid_4 = uuid_blake3.uuid(namespace, other_name)
    assert uuid_1 != uuid_4, "UUIDs should be different for different names"

    uuid_5 = uuid_blake3.uuid(other_namespace, other_name)
    assert uuid_3 != uuid_5, "UUIDs should be different for different names"

    assert uuid_1.variant == 'specified in RFC 4122'
    assert uuid_1.version == 5


def test_uuid_with_metadata():
    name = "example_a"
    namespace = "namespace_a"

    # Test with string metadata
    metadata1 = {"key1": "value1", "key2": "value2"}
    uuid_1 = uuid_blake3.uuid_with_metadata(namespace, name, metadata1)
    uuid_2 = uuid_blake3.uuid_with_metadata(namespace, name, metadata1)

    assert isinstance(uuid_1, uuid.UUID)
    assert uuid_1 == uuid_2, "UUIDs should be equal for the same name, namespace, and metadata"

    # Test with different metadata values
    metadata2 = {"key1": "different_value", "key2": "value2"}
    uuid_3 = uuid_blake3.uuid_with_metadata(namespace, name, metadata2)
    assert uuid_1 != uuid_3, "UUIDs should be different for different metadata values"

    # Test with same metadata but different order
    metadata1_reordered = {"key2": "value2", "key1": "value1"}
    uuid_3_reordered = uuid_blake3.uuid_with_metadata(namespace, name, metadata1_reordered)
    assert uuid_1 == uuid_3_reordered, "UUID should be equal for same metadata in different order"

    # Test with different metadata keys
    metadata3 = {"different_key": "value1", "key2": "value2"}
    uuid_4 = uuid_blake3.uuid_with_metadata(namespace, name, metadata3)
    assert uuid_1 != uuid_4, "UUIDs should be different for different metadata keys"

    # Test with various data types in metadata
    metadata_mixed = {
        "string": "test_string",
        "integer": 42,
        "float": 3.14159,
        "boolean": True,
        "bytes": b"test_bytes"
    }
    uuid_5 = uuid_blake3.uuid_with_metadata(namespace, name, metadata_mixed)
    uuid_6 = uuid_blake3.uuid_with_metadata(namespace, name, metadata_mixed)
    assert uuid_5 == uuid_6, "UUIDs should be equal for the same mixed metadata"

    # Test with empty metadata
    metadata_empty = {}
    uuid_7 = uuid_blake3.uuid_with_metadata(namespace, name, metadata_empty)
    assert isinstance(uuid_7, uuid.UUID)
    assert uuid_7 != uuid_1, "UUID with empty metadata should be different from UUID with metadata"

    # Test that different namespace affects result
    uuid_8 = uuid_blake3.uuid_with_metadata("different_namespace", name, metadata1)
    assert uuid_1 != uuid_8, "UUIDs should be different for different namespaces"

    # Test that different name affects result
    uuid_9 = uuid_blake3.uuid_with_metadata(namespace, "different_name", metadata1)
    assert uuid_1 != uuid_9, "UUIDs should be different for different names"

    # Check UUID properties
    assert uuid_1.variant == 'specified in RFC 4122'
    assert uuid_1.version == 5


def test_uuid_with_metadata_error_cases():
    """Test error handling in uuid_with_metadata function"""
    name = "example_a"
    namespace = "namespace_a"

    # Test with None as metadata (should raise TypeError)
    with pytest.raises(TypeError):
        uuid_blake3.uuid_with_metadata(namespace, name, None)

    # Test with non-dict metadata (should raise TypeError)
    with pytest.raises(TypeError):
        uuid_blake3.uuid_with_metadata(namespace, name, "not_a_dict")

    with pytest.raises(TypeError):
        uuid_blake3.uuid_with_metadata(namespace, name, 123)

    with pytest.raises(TypeError):
        uuid_blake3.uuid_with_metadata(namespace, name, [1, 2, 3])

    # Test with complex non-serializable objects as values
    class CustomObject:
        def __init__(self, value):
            self.value = value

        def __str__(self):
            return f"CustomObject({self.value})"

    # This should work because we fall back to str() representation
    custom_obj = CustomObject("test_value")
    metadata_with_custom = {"custom": custom_obj}
    uuid_custom = uuid_blake3.uuid_with_metadata(namespace, name, metadata_with_custom)
    assert isinstance(uuid_custom, uuid.UUID)

    # Test with nested dictionaries (should use str() representation)
    nested_dict = {"level1": {"level2": "nested_value"}}
    metadata_nested = {"nested": nested_dict}
    uuid_nested = uuid_blake3.uuid_with_metadata(namespace, name, metadata_nested)
    assert isinstance(uuid_nested, uuid.UUID)

    # Test with list values (should use str() representation)
    metadata_with_list = {"list_key": [1, 2, 3, "four"]}
    uuid_with_list = uuid_blake3.uuid_with_metadata(namespace, name, metadata_with_list)
    assert isinstance(uuid_with_list, uuid.UUID)

    # Test with None values (should use str() representation)
    metadata_with_none = {"none_key": None}
    uuid_with_none = uuid_blake3.uuid_with_metadata(namespace, name, metadata_with_none)
    assert isinstance(uuid_with_none, uuid.UUID)

    # Test that different complex objects produce different UUIDs
    custom_obj2 = CustomObject("different_value")
    metadata_with_custom2 = {"custom": custom_obj2}
    uuid_custom2 = uuid_blake3.uuid_with_metadata(namespace, name, metadata_with_custom2)
    assert uuid_custom != uuid_custom2, "Different custom objects should produce different UUIDs"

    # Test consistency with complex objects
    uuid_custom_repeat = uuid_blake3.uuid_with_metadata(namespace, name, metadata_with_custom)
    assert uuid_custom == uuid_custom_repeat, "Same custom object should produce same UUID"

def test_type_conflicts():
    namespace = "namespace_a"
    name = "example_a"

    # Test that None value and "None" string produce different UUIDs
    metadata_with_none_value = {"test_key": None}
    metadata_with_none_string = {"test_key": "None"}
    uuid_none_value = uuid_blake3.uuid_with_metadata(namespace, name, metadata_with_none_value)
    uuid_none_string = uuid_blake3.uuid_with_metadata(namespace, name, metadata_with_none_string)
    assert uuid_none_value != uuid_none_string, "None value and 'None' string should produce different UUIDs"

    # Test that empty string and None produce different UUIDs
    metadata_with_empty_string = {"test_key": ""}
    uuid_empty_string = uuid_blake3.uuid_with_metadata(namespace, name, metadata_with_empty_string)
    assert uuid_none_value != uuid_empty_string, "None value and empty string should produce different UUIDs"

    # Test that 0 and False produce different UUIDs
    metadata_with_zero = {"test_key_a": 0}
    metadata_with_false = {"test_key_a": False}
    uuid_zero = uuid_blake3.uuid_with_metadata(namespace, name, metadata_with_zero)
    uuid_false = uuid_blake3.uuid_with_metadata(namespace, name, metadata_with_false)
    assert uuid_zero != uuid_false, "0 and False should produce different UUIDs"

