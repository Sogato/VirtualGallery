from dotenv import load_dotenv
load_dotenv()
import os
import sys

# Если DJANGO_SETTINGS_MODULE не задан извне — используем dev
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'virtual_gallery.settings.dev'
)

def main():
    """Run administrative tasks."""
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
