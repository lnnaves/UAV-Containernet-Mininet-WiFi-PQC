from mininet.log import info, setLogLevel
from containernet import net
from containernet.net import Containernet
from mn_wifi.cli import CLI
from mn_wifi.link import wmediumd, adhoc
from mn_wifi.telemetry import telemetry
from mn_wifi.wmediumdConnector import interference
from containernet.node import DockerSta

import os
import subprocess

setLogLevel('info')

try:

    def topology(): 

        "Create images" 
        #dimage_drone = "ardupilot-drone"
        #dimage_gcs = "mavproxy-gcs"
        dimage_os = "ml-dsa"

        os.system("mkdir -p /tmp/shared_keys")

        net = Containernet(link=wmediumd, wmediumd_mode=interference, noise_th=-91, fading_cof=3)

        info("*** Adding docker containers\n")
        dr1 = net.addStation('dr1', mac='00:00:00:00:00:01',cls=DockerSta, ip='10.0.0.1/8',
                             dimage=dimage_os, position='10,20,0', privileged=True, volumes=["/tmp/shared_keys:/app/shared"])

        dr2 = net.addStation('dr2', mac='00:00:00:00:00:02',cls=DockerSta, ip='10.0.0.2/8',
                             dimage=dimage_os, position='30,40,0', privileged=True, volumes=["/tmp/shared_keys:/app/shared"])

        dr3 = net.addStation('dr3', mac='00:00:00:00:00:03',cls=DockerSta, ip='10.0.0.3/8',
                             dimage=dimage_os, position='27,33,0', privileged=True, volumes=["/tmp/shared_keys:/app/shared"])

        dr4 = net.addStation('dr4', mac='00:00:00:00:00:04',cls=DockerSta, ip='10.0.0.4/8',
                             dimage=dimage_os, position='20,30,0', privileged=True, volumes=["/tmp/shared_keys:/app/shared"])
        
        gcs0 = net.addStation('gcs0', mac='00:00:00:00:00:05',cls=DockerSta, ip='10.0.0.5/8',
                             dimage=dimage_os, position='10,10,0', privileged=True, volumes=["/tmp/shared_keys:/app/shared"])

        net.setPropagationModel(model="logDistance", exp=4.5)

        info("*** Configuring nodes\n")
        net.configureNodes() 

        net.addLink(dr1, cls=adhoc, intf='dr1-wlan0', 
                    ssid='adhocNet', proto='batman_adv', mode='g', channel=5, ht_cap='HT40+')
        net.addLink(dr2, cls=adhoc, intf='dr2-wlan0',
                     ssid='adhocNet', proto='batman_adv', mode='g', channel=5, ht_cap='HT40+')
        net.addLink(dr3, cls=adhoc, intf='dr3-wlan0',
                     ssid='adhocNet', proto='batman_adv', mode='g', channel=5, ht_cap='HT40+')
        net.addLink(dr4, cls=adhoc, intf='dr4-wlan0', 
                    ssid='adhocNet', proto='batman_adv', mode='g', channel=5, ht_cap='HT40+')
        net.addLink(gcs0, cls=adhoc, intf='gcs0-wlan0', 
                    ssid='adhocNet', proto='batman_adv', mode='g', channel=5, ht_cap='HT40+')

        net.start()
    
        info('*** Configurando interfaces BATMAN, IP e MTU\n')
    
        nodes = [
            (gcs0, 'gcs0-wlan0', '5'),
            (dr1, 'dr1-wlan0', '1'),
            (dr2, 'dr2-wlan0', '2'),
            (dr3, 'dr3-wlan0', '3'),
            (dr4, 'dr4-wlan0', '4')
        ]
    
        for node, iface, last_octet in nodes:

            node.cmd(f'ifconfig {iface} mtu 5000')
    
            node.cmd(f'ifconfig bat0 192.168.123.{last_octet} netmask 255.255.255.0 broadcast 192.168.123.255')
    
            node.cmd('ifconfig bat0 mtu 5000')
    
    
        info("*** Starting network\n")
        net.build()

        nodes = net.stations
        telemetry(nodes=nodes, single=True, data_type='position')

    # execucao do ML-DSA     
        gcs0.cmd('python3 gcs_control.py &')
        dr1.cmd('python3 drone_control.py &')
        dr2.cmd('python3 drone_control.py &')
        dr3.cmd('python3 drone_control.py &')
        dr4.cmd('python3 drone_control.py &')

        info("*** Running CLI\n")
        CLI(net) 

        info("*** Stopping network\n")
        net.stop()

finally:
    print("\nLimpando ambientes do Mininet...")
    subprocess.run(['sudo', 'mn', '-c'])

if __name__ == '__main__':
    topology() 