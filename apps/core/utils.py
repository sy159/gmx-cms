from __future__ import unicode_literals

import os
import platform
from collections import OrderedDict
from collections import namedtuple

from django.urls import reverse


def disk_partitions(all=False):
    """Return all mountd partitions as a nameduple.
    If all == False return phyisical partitions only.
    """
    try:
        phydevs = []
        f = open("/proc/filesystems", "r")
        for line in f:
            if not line.startswith("nodev"):
                phydevs.append(line.strip())

        retlist = []
        f = open('/etc/mtab', "r")
        for line in f:
            if not all and line.startswith('none'):
                continue
            fields = line.split()
            device = fields[0]
            mountpoint = fields[1]
            fstype = fields[2]
            if not all and fstype not in phydevs:
                continue
            if device == 'none':
                device = ''
            retlist.append([device, mountpoint])
        return retlist
    except Exception:
        return None


# 统计某磁盘使用情况的函数
def disk_usage(path):
    try:
        st = os.statvfs(path)
        total = (st.f_blocks * st.f_frsize)
        used = (st.f_blocks - st.f_bfree) * st.f_frsize
        try:
            percent = ret = (float(used) / total) * 100
        except ZeroDivisionError:
            percent = 0
        return [total / 1024 / 1204, round(percent, 1)]
    except Exception:
        return None


def sys_information():
    try:
        # 系统信息
        the_os = platform.uname()

        # CPU信息
        the_cpu = []
        with open('/proc/cpuinfo') as f:
            for line in f:
                if line.strip():
                    if line.rstrip('\n').startswith('model name'):
                        the_cpu.append(line.rstrip('\n').split(':')[1])

        # 内存状态
        meminfo = OrderedDict()
        with open('/proc/meminfo') as f:
            for line in f:
                meminfo[line.split(':')[0]] = line.split(':')[1].strip()
        try:
            total_mem = str(int(float(meminfo['MemTotal'].split(" ")[0]) / 1024)) + " MB"
            free_mem = str(int(float(meminfo['MemFree'].split(" ")[0]) / 1024)) + " MB"
        except Exception:
            total_mem = meminfo['MemTotal']
            free_mem = meminfo['MemFree']

        # 网络状态
        network = []
        with open('/proc/net/dev') as f:
            net_dump = f.readlines()
        device_data = {}
        data = namedtuple('data', ['rx', 'tx'])
        for line in net_dump[2:]:
            line = line.split(':')
            if line[0].strip() != 'lo':
                device_data[line[0].strip()] = data(float(line[1].split()[0]) / (1024.0 * 1024.0),
                                                    float(line[1].split()[8]) / (1024.0 * 1024.0))
        for dev in device_data.keys():
            network.append('{0}: {1} MB {2} MB'.format(dev, device_data[dev].rx, device_data[dev].tx))
        network = "<br>".join(network)

        # 块设备
        space = []
        for disk in disk_partitions():
            space.append('{0}, 总共 {1} MB, 剩余 {2}%'.format(disk[0], disk_usage(disk[1])[0], disk_usage(disk[1])[1]))
        space = "<br>".join(space)

        nginx = "-"

        return {"os": the_os[0] + "-" + the_os[2],
                "cpu": the_cpu[0],
                "total_mem": total_mem,
                "free_mem": free_mem,
                "network": network,
                "space": space,
                "nginx": nginx}
    except Exception:
        return {"os": "-",
                "cpu": "-",
                "total_mem": "-",
                "free_mem": "-",
                "network": "-",
                "space": "-",
                "nginx": "-"}


def admin_url(model, url, object_id=None):
    """
    Returns the URL for the given model and admin url name.
    """
    opts = model._meta
    url = "admin:%s_%s_%s" % (opts.app_label, opts.object_name.lower(), url)
    args = ()
    if object_id is not None:
        args = (object_id,)
    return reverse(url, args=args)
