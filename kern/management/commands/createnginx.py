import os

import dotenv
from django.core.management.base import BaseCommand, CommandError

nginx_tempalte = '''server {{
    server_name {url};
    location = /favicon.ico {{ access_log off; log_not_found off; }}
    location /static/ {{
        root {path};
    }}

    location /media/ {{
        root {path};
    }}

    location / {{
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }}
}}'''


class Command(BaseCommand):
    help = '创建Nginx配置文件'

    def handle (self, *args, **options):
        if not os.path.exists('/etc/nginx/sites-available'):
            raise CommandError('目标目录不存在，请先安装Nginx')

        env_path = '.env'
        if not os.path.exists(env_path):
            raise CommandError('不存在.env文件，请运行python manage.py createenv创建')

        dotenv.load_dotenv(env_path)
        url = os.getenv('URL')
        self.stdout.write(self.style.WARNING('当前URL为：' + url))
        i1 = input('是否继续？(y/n/new url)，默认为y：')
        if i1 == 'y' or i1 == '':
            pass
        elif i1 == 'n':
            self.stdout.write(self.style.ERROR('已取消'))
            return
        else:
            url = i1
            self.stdout.write(self.style.WARNING('当前URL为：' + url))
            self.stdout.write(
                self.style.WARNING('请确保Nginx设置与Django设置以及.env文件中的URL一致，否则可能导致无法访问\n'))

        path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.stdout.write(self.style.WARNING('当前路径为：' + path))
        i2 = input('是否继续？(y/n/new path)，默认为y：')
        if i2 == 'y' or i2 == '':
            pass
        elif i2 == 'n':
            self.stdout.write(self.style.ERROR('已取消'))
            return
        else:
            path = i2
            self.stdout.write(self.style.WARNING('当前路径为：' + path))
            self.stdout.write(self.style.WARNING('请确保Nginx设置与Django设置以及.env文件中的URL一致'))
            self.stdout.write(self.style.WARNING('否则可能导致无法访问'))

        self.stdout.write(self.style.WARNING('开始创建Nginx配置文件'))
        nginx_config = nginx_tempalte.format(url=url, path=path)
        with open('/etc/nginx/sites-available/emarket-client', 'w') as f:
            f.write(nginx_config)
        self.stdout.write(self.style.SUCCESS('Nginx配置文件创建成功'))
        self.stdout.write(self.style.WARNING('开始创建软链接'))
        os.system('ln -s /etc/nginx/sites-available/emarket-client /etc/nginx/sites-enabled')
        self.stdout.write(self.style.SUCCESS('软链接创建成功'))
        os.system('systemctl restart nginx')
        if os.path.exists('/etc/nginx/sites-enabled/emarket-client'):
            self.stdout.write(self.style.SUCCESS('创建成功'))
        else:
            raise CommandError('创建失败')
