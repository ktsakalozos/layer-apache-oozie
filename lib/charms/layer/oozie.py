import os
import shutil
import jujuresources
from charmhelpers.core import hookenv
from charmhelpers.core import host
from charmhelpers.core import unitdata
from jujubigdata import utils


class Oozie(object):

    def __init__(self, dist_config):
        self.dist_config = dist_config
        self.resources = {
            'oozie': 'oozie-%s' % utils.cpu_arch(),
        }
        self.verify_resources = utils.verify_resources(*self.resources.values())

    def install(self, force=False):
        jujuresources.install(self.resources['oozie'],
                              destination=self.dist_config.path('oozie'),
                              skip_top_level=True)
        self.dist_config.add_users()
        self.dist_config.add_dirs()
        self.dist_config.add_packages()

        # ExtJS v2.2 should go under self.dist_config.path('ext22')
        jujuresources.fetch('ext22')
        src = jujuresources.resource_path('ext22')
        dest = self.dist_config.path('ext22')
        shutil.copy(src, dest)

        # self.dist_config.path('ext22') should also contain all files under
        # self.dist_config.path('oozie') / 'libtools'
        src = self.dist_config.path('oozie') / 'libtools'
        src_files = os.listdir(src)
        for file_name in src_files:
            full_file_name = os.path.join(src, file_name)
            if (os.path.isfile(full_file_name)):
                shutil.copy(full_file_name, dest)

        self.setup_oozie_config()
        self.configure_oozie_hdfs()
        self.set_oozie_env()
        self.build_oozie_sharelib()
        self.build_oozie_war_file()
        self.build_oozie_db()
        # self.configure_oozie()

    def setup_oozie_config(self):
        # copy default config into alternate dir
        conf_dir = self.dist_config.path('oozie') / 'conf'
        self.dist_config.path('oozie_conf').rmtree_p()
        conf_dir.copytree(self.dist_config.path('oozie_conf'))
        oozie_conf = self.dist_config.path('oozie_conf') / "oozie-site.xml"
        with utils.xmlpropmap_edit_in_place(oozie_conf) as e:
            e['oozie.service.ProxyUserService.proxyuser.hue.hosts'] = '*'
            e['oozie.service.ProxyUserService.proxyuser.hue.groups'] = '*'

    def configure_oozie_hdfs(self):
        #config = hookenv.config()
        e = utils.read_etc_env()
        utils.run_as('hdfs', 'hdfs', 'dfs', '-mkdir', '-p', '/user/oozie', env=e)
        utils.run_as('hdfs', 'hdfs', 'dfs', '-chown', '-R', 'oozie:hadoop', '/user/oozie', env=e)

    def build_oozie_sharelib(self):
        core_conf = self.dist_config.path('hadoop_conf') / "core-site.xml"
        with utils.xmlpropmap_edit_in_place(core_conf) as e:
            namenodeURL = e['fs.defaultFS']
        slib = '/usr/lib/oozie/'
        utils.run_as('oozie', 'oozie-setup.sh', 'sharelib', 'create', '-fs', namenodeURL, '-locallib', slib)

    def build_oozie_war_file(self):
        utils.run_as('oozie', 'oozie-setup.sh', 'prepare-war')

    def build_oozie_db(self):
        sqlpath = self.dist_config.path('oozie') / 'oozie.sql'
        utils.run_as('oozie', 'ooziedb.sh', 'create', '-sqlfile', sqlpath, '-run')

    def set_oozie_env(self):
        oozie_bin = self.dist_config.path('oozie') / 'bin'
        with utils.environment_edit_in_place('/etc/environment') as env:
            if oozie_bin not in env['PATH']:
                env['PATH'] = ':'.join([env['PATH'], oozie_bin])
            env['OOZIE_HOME'] = self.dist_config.path('oozie') / 'libexec'
            env['OOZIE_CONFIG'] = self.dist_config.path('oozie_conf')
            env['OOZIE_DATA'] = self.dist_config.path('oozie_data')
            env['OOZIE_LOG'] = self.dist_config.path('oozie_log')
            env['CATALINA_BASE'] = self.dist_config.path('oozie') / 'oozie-server'
            env['CATALINA_TMPDIR'] = '/tmp'
            env['CATALINA_PID'] = '/tmp/oozie.pid'

    def open_ports(self):
        for port in self.dist_config.exposed_ports('oozie'):
            hookenv.open_port(port)

    def close_ports(self):
        for port in self.dist_config.exposed_ports('oozie'):
            hookenv.close_port(port)

    def start(self):
        hookenv.log("Starting Oozie")
        utils.run_as('oozie', 'oozied.sh', 'start')

    def stop(self):
        hookenv.log("Stopping Oozie")
        utils.run_as('oozie', 'oozied.sh', 'stop')

    def cleanup(self):
        self.dist_config.remove_users()
        self.dist_config.path('oozie').rmtree_p()
        self.dist_config.path('oozie_conf').rmtree_p()
