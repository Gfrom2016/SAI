# Copyright (c) 2021 Microsoft Open Technologies, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
#    THIS CODE IS PROVIDED ON AN *AS IS* BASIS, WITHOUT WARRANTIES OR
#    CONDITIONS OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT
#    LIMITATION ANY IMPLIED WARRANTIES OR CONDITIONS OF TITLE, FITNESS
#    FOR A PARTICULAR PURPOSE, MERCHANTABILITY OR NON-INFRINGEMENT.
#
#    See the Apache Version 2.0 License for specific language governing
#    permissions and limitations under the License.
#
#    Microsoft would like to thank the following companies for their review and
#    assistance with these files: Intel Corporation, Mellanox Technologies Ltd,
#    Dell Products, L.P., Facebook, Inc., Marvell International Ltd.
#
#

from sai_test_base import T0TestBase
from sai_thrift.sai_headers import *
from ptf import config
from ptf.testutils import *
from ptf.thriftutils import *
from sai_utils import *

class Vlan_Domain_Forwarding_Test(T0TestBase):
    """
    Verify the basic VLAN forwarding.
    In L2, if segement with VLAN tag and sends to a VLAN port, 
    segment should be forwarded inside a VLAN domain.
    """

    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self, is_reset_default_vlan=False)

    def runTest(self):
        """
        Test VLAN forwarding
        """
        try:
            print("VLAN forwarding test.")
            for index in range(2, 9):
                print("Forwarding in VLAN {} from {} to port: {}".format(
                    10,
                    self.dev_port_list[1], 
                    self.dev_port_list[index]))
                pkt = simple_udp_packet(eth_dst=self.local_server_mac_list[index],
                                        eth_src=self.local_server_mac_list[1],
                                        vlan_vid=10,
                                        ip_id=101,
                                        ip_ttl=64)
                    
                send_packet(self, self.dev_port_list[1], pkt)
                verify_packet(self, pkt, self.dev_port_list[index])
            for index in range(10, 17):
                print("Forwarding in VLAN {} from {} to port: {}".format(
                    20,
                    self.dev_port_list[9], 
                    self.dev_port_list[index]))
                pkt = simple_udp_packet(eth_dst=self.local_server_mac_list[index],
                                        eth_src=self.local_server_mac_list[9],
                                        vlan_vid=20,
                                        ip_id=101,
                                        ip_ttl=64)
                    
                send_packet(self, self.dev_port_list[9], pkt)
                verify_packet(self, pkt, self.dev_port_list[index])
        finally:
            pass

    def tearDown(self):
        """
        Test the basic tearDown process
        """
        sai_thrift_flush_fdb_entries(
            self.client, entry_type=SAI_FDB_FLUSH_ENTRY_TYPE_ALL)


class L3IPv4LpmTest(T0TestBase):
    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self, is_reset_default_vlan=False)

    def runTest(self):
        print
        print("Sending packet port 1 -> port 2 (192.168.0.1 -> 10.10.10.1 [id = 101])")
        port1 = self.port_list[20]
        port2 = self.port_list[21]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        router_mac='00:77:66:55:44:00'

        vr_id = sai_thrift_create_virtual_router(self.client)

        #we can set the src mac here
        #rif_id1 = sai_thrift_create_router_interface(self.client, virtual_router_id=vr_id, type=SAI_ROUTER_INTERFACE_TYPE_PORT, port_id=port1, src_mac_address="00:44:33:22:11:00")
        rif_id1 = sai_thrift_create_router_interface(self.client, virtual_router_id=vr_id, type=SAI_ROUTER_INTERFACE_TYPE_PORT, port_id=port1)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        rif_id2 = sai_thrift_create_router_interface(self.client, virtual_router_id=vr_id, type=SAI_ROUTER_INTERFACE_TYPE_PORT, port_id=port2)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        ip_addr1 = '10.10.10.0'
        ip_mask1 = '255.255.255.0'
        dmac1 = '00:11:22:33:44:55'
        nhop_ip1 = '20.20.20.1'
        nhop_ip1_subnet = '20.20.20.0'
        ip_mask2 = '255.255.255.0'

        nbr_entry_v4 = sai_thrift_neighbor_entry_t(rif_id=rif_id1,ip_address=sai_ipaddress(nhop_ip1))
        sai_thrift_create_neighbor_entry(self.client, nbr_entry_v4, dst_mac_address=dmac1)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        nhop1 = sai_thrift_create_next_hop(self.client, ip=sai_ipaddress(nhop_ip1), router_interface_id=rif_id1, type=SAI_NEXT_HOP_TYPE_IP)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        route1 = sai_thrift_route_entry_t(vr_id=vr_id, destination=sai_ipprefix(ip_addr1+'/24'))
        sai_thrift_create_route_entry(self.client, route1, next_hop_id=nhop1)

        #Below route is useless
        #route2 = sai_thrift_route_entry_t(vr_id=vr_id, destination=sai_ipprefix(nhop_ip1_subnet+'/24'))
        #sai_thrift_create_route_entry(self.client, route2, next_hop_id=rif_id1)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=router_mac,eth_src='00:22:22:22:22:22',ip_dst='10.10.10.1',ip_src='192.168.0.1',ip_id=105,ip_ttl=64)
        exp_pkt = simple_tcp_packet(eth_dst='00:11:22:33:44:55',eth_src=router_mac,ip_dst='10.10.10.1',ip_src='192.168.0.1',ip_id=105,ip_ttl=63)
        send_packet(self, 21, pkt)
        verify_packets(self, exp_pkt, [20])


class L3LagTest(T0TestBase):
    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self, is_reset_default_vlan=False)

    def runTest(self):
        ip_addr1 = '10.10.10.0'
        router_mac='00:77:66:55:44:00'

        port2 = self.port_list[21]
        

        vr_id = sai_thrift_create_virtual_router(self.client)
        lag1 = sai_thrift_create_lag(self.client)
        lag1_member17 = sai_thrift_create_lag_member(
            self.client, lag_id=lag1, port_id=self.port_list[17])
        lag1_member18 = sai_thrift_create_lag_member(
            self.client, lag_id=lag1, port_id=self.port_list[18])
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

        rif_id1 = sai_thrift_create_router_interface(self.client, virtual_router_id=vr_id, type=SAI_ROUTER_INTERFACE_TYPE_PORT, port_id=lag1)

        rif_id2 = sai_thrift_create_router_interface(self.client, virtual_router_id=vr_id, type=SAI_ROUTER_INTERFACE_TYPE_PORT, port_id=port2)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

        nbr_entry_v4 = sai_thrift_neighbor_entry_t(rif_id=rif_id1,ip_address=sai_ipaddress(ip_addr1))
        sai_thrift_create_neighbor_entry(self.client, nbr_entry_v4, dst_mac_address="00:44:33:22:11:00")

        nhop1 = sai_thrift_create_next_hop(self.client, ip=sai_ipaddress(ip_addr1), router_interface_id=rif_id1, type=SAI_NEXT_HOP_TYPE_IP)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        
        route1 = sai_thrift_route_entry_t(vr_id=vr_id, destination=sai_ipprefix(ip_addr1+'/24'))
        sai_thrift_create_route_entry(self.client, route1, next_hop_id=nhop1)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

        pkt1 = simple_tcp_packet(eth_dst=router_mac,eth_src='00:22:22:22:22:22',ip_dst='10.10.10.1',ip_src='192.168.0.2',ip_id=105,ip_ttl=64)
        pkt2 = simple_tcp_packet(eth_dst=router_mac,eth_src='00:22:22:22:22:22',ip_dst='10.10.10.1',ip_src='192.168.0.1',ip_id=105,ip_ttl=64)
        exp_pkt = simple_tcp_packet(eth_dst="00:44:33:22:11:00",eth_src=router_mac,ip_dst='10.10.10.1',ip_src='192.168.0.1',ip_id=105,ip_ttl=63)
        # tcpdump -i eth17 -nv tcp
        send_packet(self, 21, pkt1)
        verify_packet_any_port(self, exp_pkt, [17,18])
        send_packet(self, 21, pkt2)
        verify_packet_any_port(self, exp_pkt, [17,18])
        
