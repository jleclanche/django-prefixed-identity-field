import os

DATABASES = {
	"default": {
		"ENGINE": "django.db.backends.postgresql",
		"HOST": os.environ.get("PGHOST", "localhost"),
		"PORT": os.environ.get("PGPORT", "5432"),
		"PASSWORD": os.environ.get("PGPASSWORD", ""),
		"NAME": os.environ.get("PGDATABASE", "tests"),
		"USER": os.environ.get("PGUSER", "postgres"),
		"DATABASE": os.environ.get("PGDATABASE", "tests"),
	}
}

INSTALLED_APPS = ["tests"]
