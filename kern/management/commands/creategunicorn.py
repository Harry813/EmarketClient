import os

from django.core.management.base import BaseCommand, CommandError

gunicorn_template = """[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory={path}
ExecStart={path}/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/run/gunicorn.sock EmarketClient.wsgi:application

[Install]
WantedBy=multi-user.target"""


class Command(BaseCommand):
    help = '创建Gunicorn配置文件'

    def add_arguments (self, parser):
        parser.add_argument('-D', '--disable', action='store_true', help='禁用开机启动')

    def handle (self, *args, **options):
        if not os.path.exists('/etc/systemd/system'):
            raise CommandError('目标目录不存在，请先安装Gunicorn')

        path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.stdout.write(self.style.WARNING('当前路径为：' + path))
        i1 = input('是否继续？(y/n/new path，默认为y)：')
        if i1 == 'y' or i1 == '':
            pass
        elif i1 == 'n':
            self.stdout.write(self.style.ERROR('已取消'))
            return
        else:
            path = i1
            self.stdout.write(self.style.WARNING('当前路径为：' + path))
            self.stdout.write(self.style.WARNING('请确保Gunicorn设置与Django设置一致，否则可能导致无法访问'))

        with open('/etc/systemd/system/gunicorn.service', 'w') as f:
            f.write(gunicorn_template.format(path=path))
        self.stdout.write(self.style.SUCCESS('创建成功'))

        os.system('systemctl daemon-reload')
        self.stdout.write(self.style.SUCCESS('重载成功'))

        if options['disable']:
            os.system('systemctl disable gunicorn')
            self.stdout.write(self.style.SUCCESS('已取消开机启动'))
        else:
            os.system('systemctl enable gunicorn')
            self.stdout.write(self.style.SUCCESS('已设置开机启动'))

        os.system('systemctl start gunicorn')
        self.stdout.write(self.style.SUCCESS('启动成功'))
