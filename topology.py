from mininet.log import info, setLogLevel
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
        dimage_drone = "ardupilot-drone"
        dimage_gcs = "mavproxy-gcs"

        net = Containernet(link=wmediumd, wmediumd_mode=interference, noise_th=-91, fading_cof=3)

        info("*** Adding docker containers\n")
        dr1 = net.addStation('dr1', mac='00:00:00:00:00:01',cls=DockerSta, ip='10.0.0.1/8',
                             dimage=dimage_drone, position='30,60,0')

        dr2 = net.addStation('dr2', mac='00:00:00:00:00:02',cls=DockerSta, ip='10.0.0.2/8',
                             dimage=dimage_drone, position='40,70,0')

        dr3 = net.addStation('dr3', mac='00:00:00:00:00:03',cls=DockerSta, ip='10.0.0.3/8',
                             dimage=dimage_drone, position='67,33,0')

        dr4 = net.addStation('dr4', mac='00:00:00:00:00:04',cls=DockerSta, ip='10.0.0.4/8',
                             dimage=dimage_drone, position='90,30,0')
        
        GCS = net.addStation('GCS', mac='00:00:00:00:00:05',cls=DockerSta, ip='10.0.0.5/8',
                             dimage=dimage_gcs, position='10,10,0')

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

        info("*** Starting network\n")
        net.build()

        nodes = net.stations
        telemetry(nodes=nodes, single=True, data_type='position')


        info("*** Running CLI\n")
        CLI(net) 

        info("*** Stopping network\n")
        net.stop()

finally:
    print("\nLimpando ambientes do Mininet...")
    subprocess.run(['sudo', 'mn', '-c'])

if __name__ == '__main__':
    topology() 