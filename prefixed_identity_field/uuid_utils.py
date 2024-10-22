from datetime import datetime
from uuid import UUID

from base58 import b58decode, b58encode
from django.core.exceptions import ValidationError
from uuid6 import UUID as UUIDv7

SEPARATOR = "_"


def decode_uuid_from_prefixed_value(
	value: str | UUID, separator: str = SEPARATOR
) -> UUIDv7:
	if isinstance(value, UUIDv7):
		return value
	elif isinstance(value, UUID):
		return UUIDv7(bytes=value.bytes)

	value = value.rpartition(separator)[-1]
	decoded_value = b58decode(value)
	if len(decoded_value) != 16:
		raise ValidationError(
			f"ID {value!r} does not decode to a valid UUID",
			code="invalid",
			params={"value": value},
		)

	try:
		return UUIDv7(bytes=decoded_value)
	except ValueError:
		raise ValidationError(
			f"Invalid base58 value: {value!r}",
			code="invalid",
			params={"value": value},
		)


def encode_uuid_to_prefixed_value(value: UUID | str, prefix: str) -> str:
	if isinstance(value, str):
		value = UUIDv7(value)
	return prefix + b58encode(value.bytes).decode()


def extract_datetime_from_id(value: str | UUID) -> datetime:
	nanoseconds = decode_uuid_from_prefixed_value(value).time
	return datetime.fromtimestamp(nanoseconds / 1000)
