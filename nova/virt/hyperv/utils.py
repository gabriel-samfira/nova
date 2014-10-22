import os

from eventlet.green import subprocess
from nova.i18n import _
from eventlet import greenthread

from nova import exception
from nova.network import model as network_model
from nova.openstack.common import log as logging


LOG = logging.getLogger(__name__)


def execute(cmd, addl_env=None):
    LOG.debug(_("Running command: %s"), cmd)
    env = os.environ.copy()
    if addl_env:
        env.update(addl_env)
        subprocess.Popen(args, shell=shell, stdin=stdin, stdout=stdout,
                            stderr=stderr,
                            # preexec_fn=_subprocess_setup,
                            # close_fds=True,
                            env=env)

    obj = subprocess.Popen(cmd, shell=False,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            env=env)
    try:
        _stdout, _stderr = obj.communicate()
        obj.stdin.close()
        m = _("\nCommand: %(cmd)s\nExit code: %(code)s\nStdout: %(stdout)r\n"
              "Stderr: %(stderr)r") % {'cmd': cmd, 'code': obj.returncode,
                                       'stdout': _stdout, 'stderr': _stderr}

        if obj.returncode:
            LOG.error(m)

        if obj.returncode:
            raise RuntimeError(m)
    finally:
        # NOTE(termie): this appears to be necessary to let the subprocess
        #               call clean something up in between calls, without
        #               it two execute calls in a row hangs the second one
        greenthread.sleep(1)

    return (_stdout, _stderr)


def _ovs_vsctl(args):
    full_args = ['ovs-vsctl', '--timeout=20'] + args
    try:
        return execute(full_args)
    except Exception as e:
        LOG.error(_("Unable to execute %(cmd)s. Exception: %(exception)s"),
                  {'cmd': full_args, 'exception': e})
        raise exception.AgentError(method=full_args)


def create_ovs_vif_port(bridge, dev, iface_id, mac, instance_id):
    _ovs_vsctl(['--', '--if-exists', 'del-port', dev, '--',
                'add-port', bridge, dev,
                '--', 'set', 'Interface', dev,
                'external-ids:iface-id=%s' % iface_id,
                'external-ids:iface-status=active',
                'external-ids:attached-mac=%s' % mac,
                'external-ids:vm-uuid=%s' % instance_id])

def delete_ovs_vif_port(bridge, dev):
    _ovs_vsctl(['--', '--if-exists', 'del-port', bridge, dev])


def get_veth_name(iface_id):
    return ("qvo%s" % iface_id)[:network_model.NIC_NAME_LEN]