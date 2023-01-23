import os

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = '创建必要环境变量，可以通过交互式命令行创建，也可以通过参数创建'
    requires_migrations_checks = False
    requires_system_checks = []

    def check_migrations (self, *args, **kwargs):
        pass

    def check (self, *args, **kwargs):
        pass

    def add_arguments (self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制创建.env文件',
        )
        parser.add_argument('-B', '--brand', type=str, help='品牌名称')
        parser.add_argument('-A', '--api_key', type=str, help='API密钥，若没有请咨询上级管理员')
        parser.add_argument('-U', '--url', type=str, help='网站地址，不包含http://或https://')
        parser.add_argument('-I', '--ip', type=str, help='网站IPv4地址')
        parser.add_argument('-D', '--dbip', type=str, help='数据库IPv4地址，默认为127.0.0.1')
        parser.add_argument('-T', '--dbport', type=str, help='数据库端口，默认为3306')
        parser.add_argument('--dbusername', type=str, help='数据库用户名称，默认为EmarketClient')
        parser.add_argument('-P', '--pswd', type=str, help='数据库密码')

    def handle (self, *args, **options):
        env_path = '.env'
        if os.path.exists(env_path) and not options['force']:
            raise CommandError('已存在.env文件，若要强制创建，请使用--force参数')

        brand = options['brand']
        if not brand:
            brand = input('请输入品牌名称：')

        api_key = options['api_key']
        if not api_key:
            api_key = input('请输入API密钥：')
        # 检查API密钥格式
        p = api_key.split('.')
        if len(p[0]) != 8 or len(p[1]) != 32:
            raise CommandError('API密钥格式错误')

        url = options['url']
        if not url:
            url = input('请输入网站地址，http(s)://')

        ip = options['ip']
        if not ip:
            ip = input('请输入网站IPv4地址：')
        p = ip.split('.')
        if len(p) != 4:
            raise CommandError('IPv4地址格式错误')
        for i in p:
            if not i.isdigit() or int(i) > 255:
                raise CommandError('IPv4地址格式错误')

        dbip = options['dbip']
        if not dbip:
            dbip = input('请输入数据库IPv4地址，默认为127.0.0.1：')
            if dbip == '':
                dbip = '127.0.0.1'

        p = dbip.split('.')
        if len(p) != 4:
            raise CommandError('数据库IPv4地址格式错误')
        for i in p:
            if not i.isdigit() or int(i) > 255:
                raise CommandError('数据库IPv4地址格式错误')

        try:
            dbport = options.get('dbport')
            if dbport:
                dbport = int(dbport)
            else:
                dbport = 3306
        except ValueError or TypeError:
            raise CommandError('数据库端口格式错误')
        dbname = options.get('dbname', 'EmarketClient')

        pswd = options['pswd']
        if not pswd:
            pswd = input('请输入数据库密码：')

        import MySQLdb

        try:
            MySQLdb.connect(host=dbip, port=dbport, user=dbname, passwd=pswd)
        except MySQLdb.Error as e:
            raise CommandError('数据库连接失败，错误信息：{}'.format(e))

        with open(env_path, 'w') as f:
            f.write('BRAND=' + brand + '\n')
            f.write('API_KEY=' + api_key + '\n')
            f.write('URL=' + url + '\n')
            f.write('IPv4=' + ip + '\n')
            f.write('DB_HOST=' + dbip + '\n')
            f.write('DB_PASSWORD=' + pswd + '\n')

            dbname = options.get('dbname', None)
            if dbname:
                f.write('DB_USER=' + dbname + '\n')

            dbport = options.get('dbport', None)
            if dbport:
                f.write('DB_PORT=' + dbport + '\n')

        if os.path.exists(env_path):
            self.stdout.write(self.style.SUCCESS('创建成功'))
        else:
            raise CommandError('创建失败')
