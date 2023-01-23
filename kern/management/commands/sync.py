import os

from django.core.management.base import BaseCommand, CommandError

from kern.models import Image
from kern.utils.sync import sync_images, sync_products


class Command(BaseCommand):
    help = '同步必要数据'

    def add_arguments (self, parser):
        parser.add_argument('--delete-images', action='store_true', help='删除所有Image')

    def handle (self, *args, **options):
        if not os.path.exists('media'):
            os.mkdir('media')
        if not os.path.exists('media/images'):
            os.mkdir('media/images')

        if options['delete_images']:
            try:
                self.stdout.write(self.style.WARNING('正在删除所有图像'))
                count, _ = Image.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(f'成功删除 {count} 个实例'))
            except Exception as e:
                self.stdout.write(self.style.WARNING('删除图片失败'))

        try:
            self.stdout.write(self.style.WARNING('开始同步图片'))
            sync_images()
            self.stdout.write(self.style.SUCCESS('图片同步成功'))

            self.stdout.write(self.style.WARNING('开始同步商品'))
            sync_products()
            self.stdout.write(self.style.SUCCESS('商品同步成功'))
        except Exception as e:
            raise CommandError(str(e))
