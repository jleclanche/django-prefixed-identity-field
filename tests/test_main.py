from datetime import datetime

import pytest
from base58 import b58encode
from uuid6 import uuid7

from prefixed_identity_field.exceptions import InvalidPrefixedUUID
from prefixed_identity_field.uuid_utils import (
	decode_uuid_from_prefixed_value,
	encode_uuid_to_prefixed_value,
	extract_datetime_from_id,
)

from .models import SampleModel


def test_encode_uuid_to_prefixed_value():
	uuid_obj = uuid7()
	encoded_value = encode_uuid_to_prefixed_value(uuid_obj, prefix="test_")
	assert encoded_value.startswith("test_")
	assert isinstance(encoded_value, str)


def test_decode_uuid_from_prefixed_value():
	uuid_obj = uuid7()
	encoded_value = "test_" + b58encode(uuid_obj.bytes).decode()
	decoded_uuid = decode_uuid_from_prefixed_value(encoded_value)
	assert decoded_uuid == uuid_obj


def test_decode_uuid_from_prefixed_value_invalid_length():
	with pytest.raises(InvalidPrefixedUUID):
		decode_uuid_from_prefixed_value("test_X")


def test_decode_uuid_from_prefixed_value_invalid_value():
	with pytest.raises(InvalidPrefixedUUID):
		decode_uuid_from_prefixed_value("test_invalid_base58!")


def test_extract_datetime_from_id():
	uuid_obj = uuid7()
	encoded_value = encode_uuid_to_prefixed_value(uuid_obj, prefix="test_")
	extracted_datetime = extract_datetime_from_id(encoded_value)
	assert isinstance(extracted_datetime, datetime)
	assert extracted_datetime.timestamp() == uuid_obj.time / 1000


@pytest.mark.django_db(transaction=True)
def test_default_value_and_prefix():
	# Create an instance without specifying an ID, allowing PrefixedIdentityField to generate it.
	instance = SampleModel(name="Test Instance")
	instance.save()

	instance_id = str(instance.id)

	# Assert the generated ID has the correct prefix
	assert instance_id.startswith("test_"), instance_id
	assert (
		len(instance_id.split("_")[-1]) > 0
	)  # Ensures there's an encoded UUID after the prefix


@pytest.mark.django_db
def test_prefixed_uuid_encoding_and_decoding():
	# Generate a known UUID and encode it with a prefix
	uuid_obj = uuid7()
	encoded_value = encode_uuid_to_prefixed_value(uuid_obj, prefix="test_")

	# Save a model instance with the prefixed UUID value
	instance = SampleModel(id=encoded_value, name="Instance with Custom ID")
	instance.save()

	# Fetch the instance back and verify the ID has the correct prefix and matches the original UUID
	retrieved_instance = SampleModel.objects.get(pk=instance.pk)
	assert retrieved_instance.id == encoded_value  # Confirm it matches what we set
	assert retrieved_instance.id.startswith("test_")


@pytest.mark.django_db
def test_invalid_prefixed_uuid():
	# Attempt to save an instance with an invalid prefixed value and expect failure
	with pytest.raises(InvalidPrefixedUUID):
		SampleModel(id="invalid_prefix_uuid", name="Invalid UUID Instance").save()


@pytest.mark.django_db
def test_round_trip_db_storage():
	# Generate a UUID and manually encode it
	uuid_obj = uuid7()
	prefixed_id = encode_uuid_to_prefixed_value(uuid_obj, prefix="test_")

	# Create and save the instance with the encoded UUID
	instance = SampleModel(id=prefixed_id, name="Round Trip Test Instance")
	instance.save()

	# Fetch the instance from the database to verify decoding
	retrieved_instance = SampleModel.objects.get(pk=instance.pk)
	assert retrieved_instance.id == prefixed_id  # Check it matches exactly

	# Ensure the database retrieves a valid UUID after decoding
	assert isinstance(retrieved_instance.id.split("_")[-1], str)
	assert len(retrieved_instance.id.split("_")[-1]) > 0  # Verify encoded part exists


@pytest.mark.django_db
def test_auto_generated_id_persistence():
	# Create and save an instance without specifying an ID
	instance = SampleModel(name="Auto-generated ID Instance")
	instance.save()

	# Retrieve the instance and verify the auto-generated ID has been saved with the prefix
	retrieved_instance = SampleModel.objects.get(pk=instance.pk)
	assert retrieved_instance.id.startswith("test_")
	assert (
		len(retrieved_instance.id.split("_")[-1]) > 0
	)  # UUID part exists after the prefix
