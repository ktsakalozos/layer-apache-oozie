from charms.reactive import when, when_not, when_none
from charms.reactive import set_state, remove_state
from charmhelpers.core import hookenv
from charms.layer.oozie import Oozie
from charms.layer.hadoop_client import get_dist_config


@when_not('hadoop.ready')
def report_blocked():
    hookenv.status_set('blocked', 'Waiting for relation to Hadoop Plugin')


@when('hadoop.ready')
@when_not('oozie.installed')
def install_oozie(hadoop):
    hookenv.status_set('maintenance', 'Installing Apache Oozie')

    oozie = Oozie(get_dist_config())
    if oozie.verify_resources():
        oozie.install()
        set_state('oozie.installed')


@when('oozie.installed', 'hadoop.ready')
@when_not('oozie.started')
def start_oozie(hadoop):
    oozie = Oozie(get_dist_config())
    oozie.open_ports()
    oozie.start()
    set_state('oozie.started')
    hookenv.status_set('active', 'Ready')


@when('oozie.started')
@when_not('hadoop.ready')
def hadoop_disconnected():
    oozie = Oozie(get_dist_config())
    oozie.close_ports()
    oozie.stop()
    remove_state('oozie.started')
