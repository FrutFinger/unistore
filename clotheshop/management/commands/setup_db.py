from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
import time

class Command(BaseCommand):
    help = 'Setup database with retries'

    def handle(self, *args, **options):
        self.stdout.write('Starting database setup...')
        
        # Попытки подключения к базе данных
        max_retries = 5
        for attempt in range(max_retries):
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                self.stdout.write(self.style.SUCCESS('Database connection successful'))
                break
            except Exception as e:
                self.stdout.write(f'Database connection attempt {attempt + 1} failed: {e}')
                if attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    self.stdout.write(self.style.ERROR('Failed to connect to database'))
                    return
        
        # Применяем миграции
        try:
            self.stdout.write('Applying migrations...')
            call_command('migrate', verbosity=2)
            self.stdout.write(self.style.SUCCESS('Migrations applied successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Migration failed: {e}'))
        
        # Собираем статические файлы
        try:
            self.stdout.write('Collecting static files...')
            call_command('collectstatic', '--noinput')
            self.stdout.write(self.style.SUCCESS('Static files collected successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Static collection failed: {e}')) 