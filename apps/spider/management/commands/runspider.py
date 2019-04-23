from django.core.management.base import BaseCommand, CommandError

import backend.scheduler


class Command(BaseCommand):
    help = 'Run backend spider.'

    def handle(self, *args, **options):
        try:
            backend.scheduler.run()
        except Exception as e:
            raise CommandError(f'Unhandled error occurred when running backend spider {e}')
