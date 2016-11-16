# -*- coding: utf-8 -*-

'''
Copyright 2016 Cisco Systems 
All Rights Reserved
@author: javaos74@gmail.com, hyungsok@cisco.com
'''

import atexit

from pyVmomi import vim, vmodl
from pyVim import connect
from pyVim.connect import Disconnect

from tools import cli
import ssl


def get_objects(content, vimtype):
    """
     Get the vsphere object associated with a given text name
    """
    objs = []
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for c in container.view:
        objs.append( c)
    return objs


def remove_vswitch( hostNetSys, vss_name, host_name):
    print ("try to remove vSwitch-%s on %s" %(vss_name, host_name))
    hostNetSys.RemoveVirtualSwitch( vswitchName=vss_name)

def create_vswitch(host_network_system, vss_name, host_name, num_ports=16, nic_name=None):
    print ("Successfully created vSwitch: %s on %s" %(vss_name, host_name))
    vss_spec = vim.host.VirtualSwitch.Specification()
    vss_spec.numPorts = num_ports
    #vss_spec.bridge = vim.host.VirtualSwitch.SimpleBridge(nicDevice='pnic_key')
    #vss_spec.bridge = vim.host.VirtualSwitch.BondBridge(nicDevice=[nic_name])

    host_network_system.AddVirtualSwitch(vswitchName=vss_name, spec=vss_spec)

    print ("Successfully created vSwitch: %s on %s" %(vss_name, host_name))


def get_args():
    parser = cli.build_arg_parser()

    parser.add_argument('-v', '--vswitch',
                        type=str, action='store', help='standard vSwitch name for creation', required=True)
    args = parser.parse_args()

    return cli.prompt_for_password(args)

def main():

    args = get_args()
    try:
        service_instance = None
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23) 
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        try:
            service_instance = connect.SmartConnect(host=args.host,
                                                    user=args.user,
                                                    pwd=args.password,
                                                    port=int(args.port),
                                                    sslContext=context)
        except IOError as e:
            pass
        if not service_instance:
            print("Could not connect to the specified host using specified "
                  "username and password")
            raise SystemExit(-1)

        # Ensure that we cleanly disconnect in case our code dies
        atexit.register(connect.Disconnect, service_instance)

        content = service_instance.RetrieveContent()
        session_manager = content.sessionManager

        print("vssname=%s" %(args.vswitch))
        hosts = get_objects(content, [vim.HostSystem])
        for host in hosts:
            #create_vswitch( cfgm.networkSystem, args.vswitch, host.name)
            remove_vswitch( host.configManager.networkSystem, args.vswitch, host.name)
    except Exception as e:
    	print("Exception !!!!!" + e.message)
        pass


if __name__ == '__main__':
    main()