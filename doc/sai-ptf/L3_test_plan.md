# SAI Route Test plan <!-- omit in toc --> 

- [Test Configuration](#test-configuration)
- [Test Execution](#test-execution)
  - [Test Group1: Route](#test-group1-route)
    - [Case1: test_multiple_route_v4](#case1-test_multiple_route_v4)
    - [Case2: test_drop_route_v4](#case2-test_drop_route_v4)
    - [Case3: test_route_update_v4](#case3-test_route_update_v4)
    - [Case4: test_route_rif_v4](#case4-test_route_rif_v4)
    - [Case5: test_svi_route_v4](#case5-test_svi_route_v4)
    - [Case6: test_svi_broadcast_v4](#case6-test_svi_broadcast_v4)
    - [Case8: test_multiple_route_v6](#case8-test_multiple_route_v6)
    - [Case9: test_drop_route_v6](#case9-test_drop_route_v6)
    - [Case10: test_route_update_v6](#case10-test_route_update_v6)
    - [Case11: test_route_rif_v6](#case11-test_route_rif_v6)
    - [Case12: test_svi_route_v6](#case12-test_svi_route_v6)
    - [Case13: test_svi_broadcast_v6](#case13-test_svi_broadcast_v6)
    - [Case14: test_trap_cpu](#case14-test_trap_cpu)
  - [Test Group2: Neighbor](#test-group2-neighbor)
    - [Case1: test_host_route_v4](#case1-test_host_route_v4)
    - [Case2: test_host_route_v4](#case2-test_host_route_v4)
    - [Case3: test_no_host_route_v4](#case3-test_no_host_route_v4)
    - [Case4: test_no_host_route_v4](#case4-test_no_host_route_v4)
    - [Case5: test_host_route_v6](#case5-test_host_route_v6)
    - [Case6: test_host_route_v6](#case6-test_host_route_v6)
    - [Case7: test_no_host_route_v6](#case7-test_no_host_route_v6)
    - [Case8: test_no_host_route_v6](#case8-test_no_host_route_v6)
  - [Test Group3: Next Hop group](#test-group3-next-hop-group)
    - [Case1: test_ecmp_lags](#case1-test_ecmp_lags)
    - [Case2: test_ingress_no_diff](#case2-test_ingress_no_diff)
    - [Case3: test_ecmp_lpm_lag](#case3-test_ecmp_lpm_lag)
    - [Case4: test_ecmp_lpm_lag_add](#case4-test_ecmp_lpm_lag_add)
    - [Case5: test_ecmp_lpm_lag_disable](#case5-test_ecmp_lpm_lag_disable)
    - [Case6: test_ecmp_lpm_lag_remove](#case6-test_ecmp_lpm_lag_remove)
    - [Case7: test_ecmp_lags_v6](#case7-test_ecmp_lags_v6)
    - [Case8: test_ingress_no_diff_v6](#case8-test_ingress_no_diff_v6)
    - [Case9: test_ecmp_lpm_lag_v6](#case9-test_ecmp_lpm_lag_v6)
    - [Case10: test_ecmp_lpm_lag_add_v6](#case10-test_ecmp_lpm_lag_add_v6)
    - [Case11: test_ecmp_lpm_lag_disable_v6](#case11-test_ecmp_lpm_lag_disable_v6)
    - [Case12: test_ecmp_lpm_lag_remove_v6](#case12-test_ecmp_lpm_lag_remove_v6)
    - [Case13: test_next_hop_group_and_ecmp_entry_api](#case13-test_next_hop_group_and_ecmp_entry_api)
  - [Test Group4: Route interface](#test-group4-route-interface)
    - [Case1: test_ingress_disable](#case1-test_ingress_disable)
# Test Configuration

For the test configuration, please refer to the file 
  - [Config_t0](./config_data/config_t0.md)
  
**Note. All the tests will be based on the configuration above, if any additional configuration is required, it will be specified in the Test case.**

# Test Execution

## Test Group1: Route
### Case1: test_multiple_route_v4
### Case2: test_drop_route_v4
### Case3: test_route_update_v4
### Case4: test_route_rif_v4
### Case5: test_svi_route_v4
### Case6: test_svi_broadcast_v4
### Case8: test_multiple_route_v6
### Case9: test_drop_route_v6
### Case10: test_route_update_v6
### Case11: test_route_rif_v6
### Case12: test_svi_route_v6
### Case13: test_svi_broadcast_v6
### Case14: test_trap_cpu

### Testing Objective <!-- omit in toc --> 
Verify the basic route functions:
- multi route to the same nhop
- drop route
- update route
- RIF route
- svi route
- svi broadcast
- trap CPU 
  
### Test steps <!-- omit in toc --> 
- test_multiple_route

1. create another new route to T1. ``Dest_IP 10.1.1.99``, through next hop: ``IP 10.1.1.101`` ``LAG1``
2. Send packet with ``SIP:192.168.0.1`` ``DIP:10.1.1.99`` ``DMAC:SWITCH_MAC`` on port5
3. verify packet received with ``SMAC:SWITCH_MAC`` ``SIP 192.168.0.1`` ``DIP:10.1.1.99`` on one of LAG1 member
4. Send packet with ``SIP:192.168.0.1`` ``DIP:10.1.1.101`` ``DMAC:SWITCH_MAC`` on port5
5. verify packet received with ``SMAC:SWITCH_MAC`` ``SIP 192.168.0.1`` ``DIP:10.1.1.101`` on one of LAG1 member

- test_drop_route

1. create another new route to T1. ``Dest_IP 10.1.1.99`` with ``SAI_PACKET_ACTION_DROP``, through next hop: ``IP 10.1.1.101`` ``LAG1``
2. Send packet with ``SIP:192.168.0.1`` ``DIP:10.1.1.99`` ``DMAC:SWITCH_MAC`` on port5
3. verify no packet on any of LAG1 member

- test_route_update

1. Set Route for  ``DIP 10.1.1.101`` to SAI_PACKET_ACTION_DROP
2. Send packet with ``SIP:192.168.0.1`` ``DIP:10.1.1.101`` ``DMAC:SWITCH_MAC`` on port5
3. verify no packet on any of LAG1 member
4. Set Route for  ``DIP 10.1.1.101`` to SAI_PACKET_ACTION_FORWARD
5. verify packet received with ``SMAC:SWITCH_MAC`` ``SIP 192.168.0.1`` ``DIP:10.1.1.101`` on one of LAG1 member

- test_route_rif

1. Create route interface for LAG1:``rifx``
2. Create neighbor for ``rifx`` with IP ``IP:10.1.1.99`` with a ``DMAC``:``nbx``
3. Create next hop for ``rifx`` with IP ``IP:10.1.1.99``:``nhopx``
4. Create route through new next hop for ``DIP:10.1.1.99``
5. Send packet for ``DIP:10.1.1.99`` on port5
6. verify packet received with ``SMAC:SWITCH_MAC`` ``SIP 192.168.0.1`` ``DIP:10.1.1.99`` on one of LAG1 member

- test_svi_route

1. rounte interface already existing in config for VLAN20 SVI:``rifx``
2. Neighbors already existing in config for ``rifx`` with IP ``IP:192.168.2.9``-``IP:192.168.2.11`` with a ``Port_DMAC1``-``Port_DMAC3``
3. Next hops already existing in config for ``rifx`` with IP ``IP:192.168.2.9``-``IP:192.168.2.11``:``nhopx1``-``nhopx3``
4. send packet with ``DMAC:SWITCH_MAC`` ``DIP:IP:192.168.2.9-11`` on port5
5. Verify packet received on port9 to Port11 when sending packet with different DIPs

- test_svi_broadcast

1. rounte interface already existing in config for VLAN20 SVI:``rifx``
2. Broadcast neighbor already existing in config within VLAN20 subnet (broadcase IP and DMAC)
3. send ARP packet with ``DMAC:SWITCH_MAC`` ``DIP:IP:192.168.2.255`` on port5
4. Verify packet received on port9-11

- test_trap_cpu

1. Create Route to ``CPU_PORT`` for ``IP:10.1.1.99``
2. Host interface trap already existing in config with queue4 for IP2ME
3. send on packet with ``SIP:192.168.0.1`` ``DIP:10.1.1.101`` ``DMAC:SWITCH_MAC`` on port5
4. verify queue4 increased by 1


## Test Group2: Neighbor
### Case1: test_host_route_v4
### Case2: test_host_route_v4
### Case3: test_no_host_route_v4
### Case4: test_no_host_route_v4
### Case5: test_host_route_v6
### Case6: test_host_route_v6
### Case7: test_no_host_route_v6
### Case8: test_no_host_route_v6
### Testing Objective <!-- omit in toc --> 
Verify the basic Neighbor functions:
- no_host_route attribute

### Test steps <!-- omit in toc --> 
- test_host_route

1. Add a neighbor for IP ``10.1.1.99`` on LAG1 Route interface
2. Send packet with on port5 with ``DMAC:SWITCH_MAC`` ``DIP:10.1.1.99``
3. verify packet received on one of LAG1 member

- test_no_host_route

1. Add a neighbor for IP ``10.1.1.99`` on LAG1 Route interface, set NO_HOST_ROUTE=True
2. Send packet with on port5 with ``DMAC:SWITCH_MAC`` ``DIP:10.1.1.99``
3. Verify no packet received on any port

## Test Group3: Next Hop group
### Case1: test_ecmp_lags
### Case2: test_ingress_no_diff
### Case3: test_ecmp_lpm_lag
### Case4: test_ecmp_lpm_lag_add
### Case5: test_ecmp_lpm_lag_disable
### Case6: test_ecmp_lpm_lag_remove
### Case7: test_ecmp_lags_v6
### Case8: test_ingress_no_diff_v6
### Case9: test_ecmp_lpm_lag_v6
### Case10: test_ecmp_lpm_lag_add_v6
### Case11: test_ecmp_lpm_lag_disable_v6
### Case12: test_ecmp_lpm_lag_remove_v6
### Case13: test_next_hop_group_and_ecmp_entry_api
### Testing Objective <!-- omit in toc --> 
Verify the basic Next Hop group functions: 
- test_next_hop_group_and_ecmp_entry


### Precondition <!-- omit in toc -->
- Make sure hash field already configured for LAG and ECMP(V6 and V4)
  SAI_NATIVE_HASH_FIELD_SRC_IP
  SAI_NATIVE_HASH_FIELD_DST_IP
  SAI_NATIVE_HASH_FIELD_IP_PROTOCOL
  SAI_NATIVE_HASH_FIELD_L4_DST_PORT
  SAI_NATIVE_HASH_FIELD_L4_SRC_PORT

### Test steps <!-- omit in toc --> 
- test_ecmp_lags

1. Make sure ECMP for T1s already exists (To remote VMs through T1)
2. Generate Packets for ECMP testing, ``SIP:192.168.0.1-192.168.0.99`` 
3. Change other elements in the packets, includes ``DIP:192.168.60.1-192.168.60.99`` ``L4_port``
4. Verify packet received on differnt lags and their members

- test_ingress_no_diff

1. Make sure ECMP for T1s already exists (To remote VMs through T1)
2. Generate Packets for ECMP testing, ``SIP:192.168.0.1`` ``DIP:192.168.60.1``
3. Send packet from Port5 - Port8
4. Verify packet received on a certain LAG's member, with corresponding SIP, DIP and SMAC:SWITCH_MAC
5. Generate Packets for ECMP testing, ``SIP:192.168.0.1`` ``DIP:192.168.60.2``
6. Send packet from Port5 - Port8
7. Verify packet received on a certain LAG's member but different from step4

- test_ingress_disable

1. Make sure ECMP for T1s already exists (To remote VMs through T1)
2. Generate Packets for ECMP testing, ``SIP:192.168.0.1`` ``DIP:192.168.60.1``
3. Disable the ingress for Port5 Port8 related RIF
4. Send packet from Port5 - Port8
5. Verify no packet received on a any LAG's member


- test_ecmp_lpm

1. Make sure ECMP for T1s already exists (To remote VMs through T1)
2. Generate Packets for ECMP testing, ``SIP:192.168.0.1-192.168.0.99`` 
3. Change other elements in the packets, includes ``DIP:192.168.60.1`` ``L4_port``
4. Verify packet received on differnt lags and their members, with corresponding SIP, DIP and SMAC:SWITCH_MAC
5. Create three neighbor for ``10.1.61.101`` ``10.1.62.101``, ``DMAC1`` ``DMAC2``
6. Add two next hop for IP ``DIP:192.168.60.1/32``, ip nexthop with IP ``10.1.61.101`` ``10.1.62.101`` to LAG1 and LAG2
7. Create next hop group add two new next hops
8. Specify the Routes source mac as ``SWITCH_MAC_2`` and add new next hop group as next hop
9. Generate Packets for ECMP testing, ``SIP:192.168.0.1-192.168.0.99`` 
10. Change other elements in the packets, includes ``DIP:192.168.60.1`` ``L4_port``
11. Verify Packets only get received on LAG1 and LAG2 and with ``SMAC:SWITCH_MAC_2``

- test_ecmp_lpm_add

1. run steps 1-11 in test_ecmp_lpm
2. Create neighbor for ``10.1.63.101``, ``DMAC3`` 
3. Add one next hop for IP ``DIP:192.168.60.1/32``, ip nexthop with IP ``10.1.63.101`` to LAG3
4. Specify the Routes source mac as ``SWITCH_MAC_2`` and add new next hop group as next hop
5. add new next hop to next hop group in test_ecmp_lpm
6. Generate Packets for ECMP testing, ``SIP:192.168.0.1-192.168.0.99`` 
7. Change other elements in the packets, includes ``DIP:192.168.60.1`` ``L4_port``
8. Verify Packets only can be received on LAG1 LAG2 and LAG3, with ``SMAC:SWITCH_MAC_2``

- test_ecmp_lpm_disable

1. run steps 1-8 in test_ecmp_lpm_add
2. Dsiable LAG3 members
3. Generate Packets for ECMP testing, ``SIP:192.168.0.1-192.168.0.99`` 
4. Change other elements in the packets, includes ``DIP:192.168.60.1`` ``L4_port``
5. Verify Packets no packet lost and only can be received on LAG1 LAG2 and LAG3, with ``SMAC:SWITCH_MAC_2``

- test_ecmp_lpm_remove

1. run steps 1-8 in test_ecmp_lpm_add
2. remove the next hop from next hop group in test_ecmp_lpm: nexthop - IP ``DIP:192.168.60.1/32``, ip nexthop with IP ``10.1.63.101`` to LAG3 
3. Generate Packets for ECMP testing, ``SIP:192.168.0.1-192.168.0.99`` 
4. Change other elements in the packets, includes ``DIP:192.168.60.1`` ``L4_port``
5. Verify Packets only can be received on LAG1 LAG2 and LAG3, with ``SMAC:SWITCH_MAC_2``

- test_next_hop_group_and_ecmp_entry_api

1. Get those attributes [number_of_ecmp_groups, ecmp_members, available_next_hop_group_entry, available_next_hop_group_member_entry]
2. remove ecmp member and next group member
3. Get attributes again and check the value

## Test Group4: Route interface
### Case1: test_ingress_disable


### Test steps <!-- omit in toc --> 

- test_ingress_disable

1. Generate Packets for ECMP testing, ``SIP:192.168.0.1`` ``DIP:10.1.1.101`` ``DMAC:SWITCH_MAC``
2. Send packet on Port5
3. Verify no packet received on one of the LAG1's member

- test_ingress_mac_update

1. Generate Packets for ECMP testing, ``SIP:192.168.0.1`` ``DIP:10.1.1.101`` ``DMAC:SWITCH_MAC``
2. Send packet on Port5
3. Verify packet received on one of the LAG1's member
4. Set RIF mac to ``MacX``, the RIF related to Port5
5. Send packet on Port5 
6. Verify no packet received on any LAG1's member

- test_ingress_mtu

1. Generate Packets for ECMP testing, ``SIP:192.168.0.1`` ``DIP:10.1.1.101`` ``DMAC:SWITCH_MAC``
2. Send packet on Port5
3. Verify packet received on one of the LAG1's member
4. Set RIF MTU to ``200``, the RIF related to Port5
5. Send packet on Port5 with length (200 + 14) ( extra 14 for IPv4, 14 + 40 for IPv6. Bytes from the floor Ethernet layer, It contains the source and destination MAC Address, And the type of agreement)
6. Verify packet received on one of the LAG1's member
7. Send packet on Port5 with length (201 + 14)
8. Verify no packet received on any LAG1's member