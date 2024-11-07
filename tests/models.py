from django.db import models

from prefixed_identity_field import PrefixedIdentityField


# Sample model to test PrefixedIdentityField integration with Django ORM.
class SampleModel(models.Model):
	id = PrefixedIdentityField(prefix="test")
	name = models.CharField(max_length=255)

	class Meta:
		app_label = "tests"  # Ensure Django knows this is a test model
