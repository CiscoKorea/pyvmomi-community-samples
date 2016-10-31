from __future__ import print_function
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import atexit
import sys
import ssl


pnicmap = {}
def GetUplink( uplinks):
    vals = []
    for nic in uplinks:
    	vals.append(  pnicmap.get( nic))
    return "["+",".join(vals)+"]"

def GetPortgroup( portgroups):
    vals = []
    for pg in portgroups:
        vals.append( pnicmap.get(pg))
    return "[" +",".join(vals) + "]"

def GetNetwork( network):
    global pnicmap
    for nic in network.pnic:
        print("pnic key: %s name: %s " %(nic.key, nic.device))
        pnicmap[ nic.key] = nic.device
    for pg in network.portgroup:
    	pnicmap[ pg.key] = pg.spec.name +":"+str(pg.spec.vlanId)
    for nic in network.vnic:
        print("vnic name: %s connected portgroup: %s" %(nic.device, nic.portgroup))
    for sw in network.vswitch:
#    	print("vSwitch name: %s, numPort: %d pnics: %s" %(sw.name, sw.numPorts, sw.pnic))
    	print("vSwicth name: %s uplink: %s portgroup: %s" %(sw.name, GetUplink(sw.pnic), GetPortgroup(sw.portgroup)))
 
def GetHost( hosts):
    for host in hosts:
        print("Host Name=%s" %(host.name))
        GetNetwork( host.config.network)

def GetCluster( folder):
    for entity in folder.childEntity:
       print("Cluster name = %s" %(entity.name))
       GetHost( entity.host)

def GetDatacenters(content):
    print("Getting all Datacenter...")
    dc_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.Datacenter], True)
    obj = [ dc for dc in dc_view.view]
    for dc in obj:
       print("Datacenter %s" %(dc.name))
       GetCluster( dc.hostFolder) 
    dc_view.Destroy()
    return obj


def GetArgs():
    if len(sys.argv) != 4:
        host = raw_input("vCenter IP: ")
        user = raw_input("Username: ")
        password = raw_input("Password: ")
    else:
        host, user, password = sys.argv[1:]
    return host, user, password

def main():
    global content, hosts, hostPgDict
    host, user, password = GetArgs()
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.verify_mode = ssl.CERT_NONE
    serviceInstance = SmartConnect(host=host,
                                   user=user,
                                   pwd=password,
                                   port=443,
                                   sslContext=context)
    atexit.register(Disconnect, serviceInstance)
    content = serviceInstance.RetrieveContent()
    dcs = GetDatacenters(content)

# Main section
if __name__ == "__main__":
    sys.exit(main())