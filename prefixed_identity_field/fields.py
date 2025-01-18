from uuid import UUID

from django.db.models import UUIDField
from uuid6 import uuid7

from .uuid_utils import (
	SEPARATOR,
	decode_uuid_from_prefixed_value,
	encode_uuid_to_prefixed_value,
)


class PrefixedIdentityField(UUIDField):
	def __init__(self, prefix: str, separator: str = SEPARATOR, *args, **kwargs):
		if not prefix.endswith(separator):
			prefix += separator
		self.prefix = prefix
		self.separator = separator
		kwargs.setdefault("default", uuid7)
		kwargs.setdefault("primary_key", True)
		kwargs.setdefault("editable", False)
		super().__init__(*args, **kwargs)

	def deconstruct(self):
		name, path, args, kwargs = super().deconstruct()
		del kwargs["default"]
		kwargs["prefix"] = self.prefix
		return name, path, args, kwargs

	def to_python(self, value):
		if isinstance(value, str) and self.separator in value:
			return value
		if value is None:
			return value
		return encode_uuid_to_prefixed_value(value, prefix=self.prefix)

	def get_prep_value(self, value):
		if isinstance(value, str) and self.separator in value:
			return decode_uuid_from_prefixed_value(value, separator=self.separator)
		return super().get_prep_value(value)

	def get_db_prep_value(self, value, connection, prepared):
		if isinstance(value, str) and self.separator in value:
			return decode_uuid_from_prefixed_value(value, separator=self.separator)
		return super().get_db_prep_value(value, connection, prepared=prepared)

	def from_db_value(
		self, value: UUID | str | None, expression, connection
	) -> str | None:
		if value is None:
			return value

		return encode_uuid_to_prefixed_value(value, prefix=self.prefix)

	def get_default(self) -> str:
		default_uuid = super().get_default()
		return encode_uuid_to_prefixed_value(default_uuid, prefix=self.prefix)
