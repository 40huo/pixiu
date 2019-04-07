from django.core.management.base import BaseCommand, CommandError

import backend


class Command(BaseCommand):
    help = '启动爬虫后端'

    def handle(self, *args, **options):
        try:
            backend.run()
        except Exception as e:
            raise CommandError(f'启动爬虫后端出错 {e}')
