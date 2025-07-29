# Django Auto Filters

Enhanced Django Admin filters with autocomplete support and OR condition combinations.

## Features

- Autocomplete-based filters for ForeignKey and ManyToMany fields
- Multiple selection with OR condition combinations
- User-friendly interface for large dataset exploration
- Flexible extension options for custom filter logic
- Performance optimized with AJAX calls and query caching
- Native ModelAdmin integration
- Minimal dependencies

## Requirements

- Python 3.8+
- Django 4.2 - 5.2

## Installation

```bash
pip install django-autofilters
```

## Quick Start

1. Add `auto_filters` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'auto_filters',
    ...
]
```

2. Use the filters in your ModelAdmin:

```python
from auto_filters.filters import AutocompleteFilter

class YourModelAdmin(admin.ModelAdmin):
    list_filter = (
        ('foreign_key_field', AutocompleteFilter),
    )
```

## Development Setup

This project uses Poetry for dependency management. To set up your development environment:

1. Clone the repository:
```bash
git clone https://github.com/youngkwang-yang/django-autofilters.git
cd django-autofilters
```

2. Install Poetry (if you haven't already):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies:
```bash
poetry install
```

4. Run the example project:
```bash
cd example
poetry run python manage.py migrate
poetry run python manage.py createsuperuser
poetry run python manage.py runserver
```

5. Visit http://127.0.0.1:8000/admin/ to see the filters in action.

## Running Tests

```bash
poetry run pytest
```

## Code Quality

We use several tools to maintain code quality:

```bash
# Format code
poetry run black .
poetry run isort .

# Check types
poetry run mypy .

# Run linter
poetry run flake8 .
```

## Documentation

[Documentation Link - Coming Soon]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 