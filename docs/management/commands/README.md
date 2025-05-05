# Management Commands

This directory contains custom Django management commands for various administrative tasks.

## Available Commands

### Database Management
- `create_terms.py`: Creates initial terms in the database
- `backup_database.py`: Creates database backups
- `cleanup_old_data.py`: Removes old and unused data

### User Management
- `create_superuser.py`: Creates a superuser with specified credentials
- `reset_user_password.py`: Resets a user's password
- `deactivate_user.py`: Deactivates a user account
- `export_users.py`: Exports user data to CSV

### Content Management
- `import_programs.py`: Imports program data from CSV
- `export_programs.py`: Exports program data to CSV
- `cleanup_media.py`: Removes unused media files
- `generate_sitemap.py`: Generates sitemap.xml

### System Maintenance
- `check_system_health.py`: Checks system health and performance
- `clear_cache.py`: Clears system cache
- `rotate_logs.py`: Rotates and compresses log files
- `update_search_index.py`: Updates search index

## Usage

To use these commands, run them using the `python manage.py` command:

```bash
# Create terms
python manage.py create_terms

# Create superuser
python manage.py create_superuser

# Check system health
python manage.py check_system_health
```

## Adding New Commands

To add a new management command:

1. Create a new Python file in this directory
2. Create a class that inherits from `BaseCommand`
3. Implement the `handle` method
4. Add proper documentation and error handling

Example:

```python
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Description of what the command does'

    def add_arguments(self, parser):
        parser.add_argument('--option', type=str, help='Option description')

    def handle(self, *args, **options):
        # Command logic here
        self.stdout.write(self.style.SUCCESS('Successfully executed command'))
```

## Best Practices

1. Always include proper documentation
2. Add appropriate error handling
3. Use logging for important operations
4. Include progress indicators for long-running tasks
5. Add command-line arguments for flexibility
6. Include dry-run options where appropriate
7. Add proper validation for inputs
8. Use transactions for database operations
9. Include proper exit codes
10. Add proper logging and notifications

## Security Considerations

1. Never include sensitive data in command output
2. Validate all inputs
3. Use proper permissions
4. Log all sensitive operations
5. Use environment variables for sensitive data
6. Implement proper access controls
7. Use secure file operations
8. Implement proper error handling
9. Use proper database transactions
10. Follow security best practices 