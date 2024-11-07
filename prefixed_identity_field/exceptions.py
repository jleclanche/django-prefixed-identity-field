from django.core.exceptions import ValidationError


class InvalidPrefixedUUID(ValidationError):
	pass
