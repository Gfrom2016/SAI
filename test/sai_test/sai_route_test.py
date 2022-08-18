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
from sai_utils import *

from data_module.device import Device, DeviceType

class RouteRifTest(T0TestBase):
    """
    Verify route with RIF directly (next hop is RIF)
    """

    def setUp(self):
        """
        Test the basic setup process.
        """
        super().setUp()

    def runTest(self):
        """
        1. Make sure common config for route dest IP within 192.168.12.0/24 through RIF(Nhop is Rif) to LAG2 created
        2. Send packets for DIP:192.168.12.1~8 SIP 192.168.0.1 DMAC: SWITCH_MAC on port5
        3. Verify packet received with SMAC: SWITCH_MAC SIP: 192.168.0.1 DIP:192.168.12.1~8 on one of LAG2 member
        """
        print("RouteRifTest")
        self.port5_rif = sai_thrift_create_router_interface(self.client,
                                                            virtual_router_id=self.dut.default_vrf,
                                                            type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                                                            port_id=self.dut.port_list[5])
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

        try:
            for i in range(0, 8):
                pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                        ip_dst=self.servers[12][i].ipv4,
                                        ip_id=105,
                                        ip_ttl=64)
                exp_pkt = simple_tcp_packet(eth_src=ROUTER_MAC,
                                            eth_dst=self.t1_list[2][100].mac,
                                            ip_dst=self.servers[12][i].ipv4,
                                            ip_id=105,
                                            ip_ttl=63)
                send_packet(self, 5, pkt)
                verify_packet_any_port(self, exp_pkt, self.dut.lag2.member_port_indexs)
                print("received packet with dst_ip:{} on one of lag2 member".format(self.servers[12][i].ipv4))
        finally:
            sai_thrift_remove_router_interface(self.client, self.port5_rif)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
    
    def tearDown(self):
        super().tearDown()


class LagMultipleRouteTest(T0TestBase):
    """
    Verify multi-route to the same nhop.
    """

    def setUp(self):
        """
        Test the basic setup process.
        """
        super().setUp()
    
    def runTest(self):
        """
        1. Make sure common config created for IP within in 192.168.21.0/24, through next-hop: IP 10.1.1.100 LAG1
        2. Send packet with SIP:192.168.0.1 DIP:192.168.21.1 DMAC:SWITCH_MAC on port5
        3. Verify packet received with SMAC: SWITCH_MAC SIP 192.168.0.1 DIP:192.168.21.1 on one of LAG1 member
        4. Send packet with SIP:192.168.0.1 DIP:192.168.11.1 DMAC:SWITCH_MAC on port5
        5. Verify packet received with SMAC: SWITCH_MAC SIP:192.168.0.1 DIP:192.168.11.1 on one of LAG1 member
        """
        print("LagMultipleRouteTest")
        self.port5_rif = sai_thrift_create_router_interface(self.client,
                                                            virtual_router_id=self.dut.default_vrf,
                                                            type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                                                            port_id=self.dut.port_list[5])
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        
        self.servers[21] = [Device(DeviceType.server, index, 21) for index in range(0, self.num_device_each_group)]
        self.servers[21][0].ip_prefix = '24'
        self.servers[21][0].ip_prefix_v6 = '112'
        self.new_route4, self.new_route6 = self.route_configer.create_route_path_by_nexthop(
            dest_device=new_dst, 
            nexthopv4=self.dut.lag1.nexthopv4, 
            nexthopv6=self.dut.lag1.nexthopv6)
        
        pkt1 = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                 ip_dst=self.servers[21][1].ipv4,
                                 ip_id=105,
                                 ip_ttl=64)
        exp_pkt1 = simple_tcp_packet(eth_src=ROUTER_MAC,
                                     eth_dst=self.t1_list[1][100].mac,
                                     ip_dst=self.servers[21][1].ipv4,
                                     ip_id=105,
                                     ip_ttl=63)

        pkt2 = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                 ip_dst=self.servers[11][1].ipv4,
                                 ip_id=105,
                                 ip_ttl=64)
        exp_pkt2 = simple_tcp_packet(eth_src=ROUTER_MAC,
                                     eth_dst=self.t1_list[1][100].mac,
                                     ip_dst=self.servers[11][1].ipv4,
                                     ip_id=105,
                                     ip_ttl=63)          

        try:
            send_packet(self, 5, pkt1)
            verify_packet_any_port(self, exp_pkt1, self.dut.lag1.member_port_indexs)
            print("receive packet with dst_ip:{} from one of lag1 member".format(self.servers[21][1].ipv4))

            send_packet(self, 5, pkt2)
            verify_packet_any_port(self, exp_pkt2, self.dut.lag1.member_port_indexs)
            print("receive packet with dst_ip:{} from one of lag1 member".format(self.servers[11][1].ipv4))
        finally:
            sai_thrift_remove_router_interface(self.client, self.port5_rif)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
            self.dut.routev4_list.remove(self.new_route4)
            self.dut.routev6_list.remove(self.new_route6)
            sai_thrift_remove_route_entry(self.client, self.new_route4)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
            sai_thrift_remove_route_entry(self.client, self.new_route6)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
            #TODO: delete servers[21]?

    def tearDown(self):
        super().tearDown()


class DropRouteTest(T0TestBase):
    """
    Verify drop the packet when SAI_PACKET_ACTION_DROP
    """

    def setUp(self):
        """
        Test the basic setup process.
        """
        super().setUp()
    
    def runTest(self):
        """
        1. Create new route. Dest_IP:10.1.1.10 with SAI_PACKET_ACTION_DROP, through an already existing next-hop: IP 10.1.1.100 LAG1
        2. Send packet with SIP:192.168.0.1 DIP:10.1.1.10 DMAC:SWITCH_MAC on port5
        3. Verify no packet on any of the LAG1 members
        4. Check the packet drop counter
        """
        print("DropRouteTest...")
        self.port5_rif = sai_thrift_create_router_interface(self.client,
                                                            virtual_router_id=self.dut.default_vrf,
                                                            type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                                                            port_id=self.dut.port_list[5])
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

        self.t1_list[1][10].ip_prefix = '24'
        self.t1_list[1][10].ip_prefix_v6 = '112'
        self.new_route4, self.new_route6 = self.route_configer.create_route_path_by_nexthop(
            dest_device=self.t1_list[1][10],
            nexthopv4=self.dut.lag1.nexthopv4,
            nexthopv6=self.dut.lag1.nexthopv6)
        sai_thrift_set_route_entry_attribute(self.client, self.new_route4, packet_action=SAI_PACKET_ACTION_DROP)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        print("create new route with SAI_PACKET_ACTION_DROP")
        
        pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                ip_dst=self.t1_list[1][10].ipv4,
                                ip_id=105,
                                ip_ttl=64)
        try:
            send_packet(self, 5, pkt)
            verify_no_other_packets(self)
            print("no other packets")
            #TODO check packet drop counter
        finally:
            sai_thrift_remove_router_interface(self.client, self.port5_rif)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
            self.dut.routev4_list.remove(self.new_route4)
            self.dut.routev6_list.remove(self.new_route6)
            sai_thrift_remove_route_entry(self.client, self.new_route4)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
            sai_thrift_remove_route_entry(self.client, self.new_route6)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

    def tearDown(self):
        super().tearDown()


class RouteUpdateTest(T0TestBase):
    """
    Verify route action gets updated when set attribute from SAI_PACKET_ACTION_DROP to SAI_PACKET_ACTION_FORWARD
    """

    def setUp(self):
        """
        Test the basic setup process.
        """
        super().setUp()
    
    def runTest(self):
        """
        1. Set Existing Route on DIP:192.168.11.0/24 with packet action as SAI_PACKET_ACTION_DROP
        2. Send packet with SIP:192.168.0.1 DIP:192.168.11.1 DMAC:SWITCH_MAC on port5
        3. Verify no packet on any of the LAG1 members
        4. Set Route packet action as SAI_PACKET_ACTION_FORWARD
        5. Send packet with SIP:192.168.0.1 DIP:192.168.11.1 DMAC: SWITCH_MAC on port5
        6. Verify packet received with SMAC: SWITCH_MAC SIP 192.168.0.1 DIP:192.168.11.1 on one of LAG1 member
        """
        print("RouteUpdateTest...")
        self.port5_rif = sai_thrift_create_router_interface(self.client,
                                                            virtual_router_id=self.dut.default_vrf,
                                                            type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                                                            port_id=self.dut.port_list[5])
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        
        pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                ip_dst=self.servers[11][1].ipv4,
                                ip_id=105,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(eth_src=ROUTER_MAC,
                                    eth_dst=self.t1_list[1][100].mac,
                                    ip_dst=self.servers[11][1].ipv4,
                                    ip_id=105,
                                    ip_ttl=63)
        try:
            sai_thrift_set_route_entry_attribute(self.client, self.servers[11][0].routev4, packet_action=SAI_PACKET_ACTION_DROP)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
            print("set route on 192.168.11.0/24 with action SAI_PACKET_ACTION_DROP")

            send_packet(self, 5, pkt)
            verify_no_other_packets(self)
            print("no packets received after set packet action to DROP")

            sai_thrift_set_route_entry_attribute(self.client, self.servers[11][0].routev4, packet_action=SAI_PACKET_ACTION_FORWARD)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
            print("Update route action to forward")

            send_packet(self, 5, pkt)
            verify_packet_any_port(self, exp_pkt, self.dut.lag1.member_port_indexs)
            print("packet received on one of lag1 member after set packet action to FORWARD")
        finally:
            sai_thrift_remove_router_interface(self.client, self.port5_rif)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

    def tearDown(self):
        super().tearDown()


class RouteLPMRouteNexthopTest(T0TestBase):
    """
    Verify lpm route path (with next-hop), route path will be alter to the more accurate one
    """

    def setUp(self):
        """
        Test the basic setup process.
        """
        super().setUp()

        self.dst_ip = '192.168.1.200'
        self.dmac1 = '00:11:22:33:44:55'
        self.dmac2 = '00:11:22:33:44:66'

        self.port5_rif = sai_thrift_create_router_interface(self.client,
                                                            virtual_router_id=self.dut.default_vrf,
                                                            type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                                                            port_id=self.dut.port_list[5])
        self.port2_rif = sai_thrift_create_router_interface(self.client,
                                                            virtual_router_id=self.dut.default_vrf,
                                                            type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                                                            port_id=self.dut.port_list[2])
        self.port1_rif = sai_thrift_create_router_interface(self.client,
                                                            virtual_router_id=self.dut.default_vrf,
                                                            type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                                                            port_id=self.dut.port_list[1])
    
    def runTest(self):
        """
        1. Make sure the route for DIP:192.168.1.0/24 is already configured (the route through the next hop)
        2. Add a neighbor with IP:192.168.1.200 on Port2 with DMAC1
        3. Send packet with DMAC: SWITCH_MAC and DIP:192.168.1.200 on port5
        4. Received packet with the DMAC1, SMAC: SWITCH_MAC and DIP:192.168.1.200 on port2
        5. Add a new route for DIP:192.168.1.200/32 with a next-hop on port1
        6. Add a neighbor with IP:192.168.1.200 on Port1 with DMAC2
        7. Send packet with DMAC: SWITCH_MAC and DIP:192.168.1.200 on port5
        8. Received packet with the DMAC2, SMAC: SWITCH_MAC and DIP:192.168.1.200 on port1
        """
        print("RouteLPMRouteNexthopTest")
        # Add a neighbor with IP:192.168.1.200 on Port2 with DMAC1
        self.port2_nbr_entry = sai_thrift_neighbor_entry_t(rif_id=self.port2_rif,
                                                           ip_address=sai_ipaddress(self.dst_ip))
        status = sai_thrift_create_neighbor_entry(self.client,
                                                  entry=self.port2_nbr_entry,
                                                  dst_mac_address=self.dmac1)
        self.assertEqual(status, SAI_STATUS_SUCCESS)
        print("Add a neighbor with IP:192.168.1.200 on Port2 with DMAC1")

        pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                ip_dst=self.dst_ip,
                                ip_id=105,
                                ip_ttl=64)
        exp_pkt1 = simple_tcp_packet(eth_src=ROUTER_MAC,
                                     eth_dst=self.dmac1,
                                     ip_dst=self.dst_ip,
                                     ip_id=105,
                                     ip_ttl=63)
        exp_pkt2 = simple_tcp_packet(eth_src=ROUTER_MAC,
                                     eth_dst=self.dmac2,
                                     ip_dst=self.dst_ip,
                                     ip_id=105,
                                     ip_ttl=63)

        try:
            send_packet(self, 5, pkt)
            verify_packet(self, exp_pkt1, 2)
            print("packet with dst_ip:{} sent from port5, received from port2".format(self.dst_ip))

            # Add a neighbor with IP:192.168.1.200 on Port1 with DMAC2
            self.port1_nbr_entry = sai_thrift_neighbor_entry_t(rif_id=self.port1_rif,
                                                               ip_address=sai_ipaddress(self.dst_ip))
            status = sai_thrift_create_neighbor_entry(self.client,
                                                      entry=self.port1_nbr_entry,
                                                      dst_mac_address=self.dmac2)
            print("Add a neighbor with IP:192.168.1.200 on Port1 with DMAC2")

            # Add a new route for DIP:192.168.1.200/32 with a next-hop on port1
            self.port1_nhop = sai_thrift_create_neighbor_entry(self.client,
                                                               ip=sai_ipaddress(self.dst_ip),
                                                               router_interface_id=self.port1_rif,
                                                               type=SAI_NEXT_HOP_TYPE_IP)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
            self.port1_route = sai_thrift_route_entry_t(vr_id=self.default_vrf,
                                                        destination=sai_ipprefix(self.dst_ip+'/32'))
            status = sai_thrift_create_route_entry(self.client, self.port1_route, next_hop_id=self.port1_nhop)
            self.assertEqual(status, SAI_STATUS_SUCCESS)
            print("add a new route DIP:192.168.1.200/32 with next-hop on port1")

            send_packet(self, 5, pkt)
            verify_packet(self, exp_pkt2, 1)
            print("after add new neighbor for port1, packet with dst_ip:{} sent from port5, received from port1".format(dst_ip))
        finally:
            pass

    def tearDown(self):
        sai_thrift_remove_route_entry(self.client, self.port1_route)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        sai_thrift_remove_next_hop(self.client, self.port1_nhop)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        sai_thrift_remove_neighbor_entry(self.client, self.port1_nbr_entry)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        sai_thrift_remove_neighbor_entry(self.client, self.port2_nbr_entry)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        sai_thrift_remove_router_interface(self.client, self.port2_rif_id)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        sai_thrift_remove_router_interface(self.client, self.port5_rif_id)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        sai_thrift_remove_router_interface(self.client, self.port1_rif_id)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        super().tearDown()


class RouteLPMRouteRifTest(T0TestBase):
    """
    Verify lpm route path (with rif as next hop), route path will be alter to the more accurate one
    """

    def setUp(self):
        """
        Test the basic setup process.
        """
        super().setUp()

        self.dst_ip = '192.168.1.200'
        self.dmac1 = '00:11:22:33:44:55'
        self.dmac2 = '00:11:22:33:44:66'

        self.port5_rif = sai_thrift_create_router_interface(self.client,
                                                            virtual_router_id=self.dut.default_vrf,
                                                            type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                                                            port_id=self.dut.port_list[5])
        self.port2_rif = sai_thrift_create_router_interface(self.client,
                                                            virtual_router_id=self.dut.default_vrf,
                                                            type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                                                            port_id=self.dut.port_list[2])
        self.port1_rif = sai_thrift_create_router_interface(self.client,
                                                            virtual_router_id=self.dut.default_vrf,
                                                            type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                                                            port_id=self.dut.port_list[1])
    
    def runTest(self):
        """
        1. Make sure the route for DIP:192.168.1.0/24 is already configured (the route through next hop)
        2. Add a neighbor with IP:192.168.1.200 on Port2 with DMAC1
        3. Send packet with DMAC: SWITCH_MAC and DIP: IP:192.168.1.200 on port5
        4. Received packet with the DMAC1, SMAC: SWITCH_MAC and DIP: IP:192.168.1.200 on port2
        5. Add a new route for DIP: IP:192.168.1.200/32 and bind to port1 rif directly
        6. Add a neighbor with IP:192.168.1.200 on Port1 with DMAC2
        7. Send packet with DMAC: SWITCH_MAC and DIP: IP:192.168.1.200 on port5
        8. Received packet with the DMAC2, SMAC: SWITCH_MAC and DIP: IP:192.168.1.200 on port1
        """
        print("RouteLPMRouteRifTest")
        # Add a neighbor with IP:192.168.1.200 on Port2 with DMAC1
        self.port2_nbr_entry = sai_thrift_neighbor_entry_t(rif_id=self.port2_rif,
                                                           ip_address=sai_ipaddress(self.dst_ip))
        status = sai_thrift_create_neighbor_entry(self.client,
                                                  entry=self.port2_nbr_entry,
                                                  dst_mac_address=self.dmac1)
        self.assertEqual(status, SAI_STATUS_SUCCESS)
        print("Add a neighbor with IP:192.168.1.200 on Port2 with DMAC1")

        pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                ip_dst=self.dst_ip,
                                ip_id=105,
                                ip_ttl=64)
        exp_pkt1 = simple_tcp_packet(eth_src=ROUTER_MAC,
                                     eth_dst=self.dmac1,
                                     ip_dst=self.dst_ip,
                                     ip_id=105,
                                     ip_ttl=63)
        exp_pkt2 = simple_tcp_packet(eth_src=ROUTER_MAC,
                                     eth_dst=self.dmac2,
                                     ip_dst=self.dst_ip,
                                     ip_id=105,
                                     ip_ttl=63)

        try:
            send_packet(self, 5, pkt)
            verify_packet(self, exp_pkt1, 2)
            print("packet with dst_ip:{} sent from port5, received from port2".format(self.dst_ip))

            # Add a neighbor with IP:192.168.1.200 on Port1 with DMAC2
            self.port1_nbr_entry = sai_thrift_neighbor_entry_t(rif_id=self.port1_rif,
                                                               ip_address=sai_ipaddress(self.dst_ip))
            status = sai_thrift_create_neighbor_entry(self.client,
                                                      entry=self.port1_nbr_entry,
                                                      dst_mac_address=self.dmac2)
            print("Add a neighbor with IP:192.168.1.200 on Port1 with DMAC2")

            # Add a new route for DIP: IP:192.168.1.200/32 and bind to port1 rif directly
            self.port1_route = sai_thrift_route_entry_t(vr_id=self.default_vrf,
                                                        destination=sai_ipprefix(self.dst_ip+'/32'))
            status = sai_thrift_create_route_entry(self.client, self.port1_route, next_hop_id=self.port1_rif)
            self.assertEqual(status, SAI_STATUS_SUCCESS)
            print("add a new route DIP:192.168.1.200/32 and bind to port1 rif directly")

            send_packet(self, 5, pkt)
            verify_packet(self, exp_pkt2, 1)
            print("after add new neighbor for port1, packet with dst_ip:{} sent from port5, received from port1".format(dst_ip))
        finally:
            pass

    def tearDown(self):
        sai_thrift_remove_route_entry(self.client, self.port1_route)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        sai_thrift_remove_neighbor_entry(self.client, self.port1_nbr_entry)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        sai_thrift_remove_neighbor_entry(self.client, self.port2_nbr_entry)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        sai_thrift_remove_router_interface(self.client, self.port2_rif_id)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        sai_thrift_remove_router_interface(self.client, self.port5_rif_id)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        sai_thrift_remove_router_interface(self.client, self.port1_rif_id)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        super().tearDown()