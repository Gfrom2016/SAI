# SAI Route Test plan <!-- omit in toc --> 

- [Test Configuration](#test-configuration)
- [Test Execution](#test-execution)
  - [Test Group1: Route](#test-group1-route)
    - [Case1: test_multiple_route](#case1-test_multiple_route)
    - [Case2: test_drop_route](#case2-test_drop_route)
    - [Case3: test_route_update](#case3-test_route_update)
    - [Case4: test_route_rif](#case4-test_route_rif)
    - [Case5: test_svi_route](#case5-test_svi_route)
    - [Case6: test_svi_broadcast](#case6-test_svi_broadcast)
    - [Case7: test_trap_cpu](#case7-test_trap_cpu)
    - [Case8: test_glean_cpu_no_neighbor](#case8-test_glean_cpu_no_neighbor)
    - [Test steps](#test-steps)
  - [Test Group2: Neighbor](#test-group2-neighbor)
# Test Configuration

For the test configuration, please refer to the file 
  - [Config_t0](./config_data/config_t0.md)
  
**Note. All the tests will be based on the configuration above, if any additional configuration is required, it will be specified in the Test case.**

# Test Execution

## Test Group1: Route
### Case1: test_multiple_route
### Case2: test_drop_route
### Case3: test_route_update
### Case4: test_route_rif
### Case5: test_svi_route
### Case6: test_svi_broadcast
### Case7: test_trap_cpu
### Case8: test_glean_cpu_no_neighbor

### Testing Objective <!-- omit in toc --> 
Verify the basic route functions:
- multi route to the same nhop
- drop route
- update route
- RIF route
- svi route
- svi broadcast
- trap CPU 
- packet is gleaned to CPU when nexthop RIF without a neighbor
  
### Test steps
- test_multiple_route

1. create another new route to T1. ``Dest_IP 10.1.1.99``, through next hop: ``IP 10.1.1.101`` ``LAG1``
2. Send packet with ``SIP:192.168.0.1`` ``DIP:10.1.1.99`` ``DMAC:SWITCH_MAC`` on port 1
3. verify packet received with ``SMAC:SWITCH_MAC`` ``SIP 192.168.0.1`` ``DIP:10.1.1.99`` on any of LAG1 member
4. Send packet with ``SIP:192.168.0.1`` ``DIP:10.1.1.101`` ``DMAC:SWITCH_MAC`` on port 1
5. verify packet received with ``SMAC:SWITCH_MAC`` ``SIP 192.168.0.1`` ``DIP:10.1.1.101`` on any of LAG1 member

- test_drop_route

1. create another new route to T1. ``Dest_IP 10.1.1.99`` with ``SAI_PACKET_ACTION_DROP``, through next hop: ``IP 10.1.1.101`` ``LAG1``
2. Send packet with ``SIP:192.168.0.1`` ``DIP:10.1.1.99`` ``DMAC:SWITCH_MAC`` on port 1
3. verify no packet on any of LAG1 member

- test_route_update

1. Set Route for  ``DIP 10.1.1.101`` to SAI_PACKET_ACTION_DROP
2. Send packet with ``SIP:192.168.0.1`` ``DIP:10.1.1.101`` ``DMAC:SWITCH_MAC`` on port 1
3. verify no packet on any of LAG1 member
4. Set Route for  ``DIP 10.1.1.101`` to SAI_PACKET_ACTION_FORWARD
5. verify packet received with ``SMAC:SWITCH_MAC`` ``SIP 192.168.0.1`` ``DIP:10.1.1.101`` on any of LAG1 member

- test_route_rif

1. Create route interface for LAG1:``rifx``
2. Create neighbor for ``rifx`` with IP ``IP:10.1.1.99`` with a ``DMAC``:``nbx``
3. Create next hop for ``rifx`` with IP ``IP:10.1.1.99``:``nhopx``
4. Create route through new next hop for ``DIP:10.1.1.99``
5. Send packet for ``DIP:10.1.1.99`` on port1
6. verify packet received with ``SMAC:SWITCH_MAC`` ``SIP 192.168.0.1`` ``DIP:10.1.1.99`` on any of LAG1 member

- test_svi_route

1. rounte interface already existing in config for VLAN20 SVI:``rifx``
2. Neighbors already existing in config for ``rifx`` with IP ``IP:192.168.2.9``-``IP:192.168.2.11`` with a ``Port_DMAC1``-``Port_DMAC3``
3. Next hops already existing in config for ``rifx`` with IP ``IP:192.168.2.9``-``IP:192.168.2.11``:``nhopx1``-``nhopx3``
4. send packet with ``DMAC:SWITCH_MAC`` ``DIP:IP:192.168.2.9-11`` on port 1
5. Verify packet received on port9-11

- test_svi_broadcast

1. rounte interface already existing in config for VLAN20 SVI:``rifx``
2. Broadcast neighbor already existing in config within VLAN20 subnet (broadcase IP and DMAC)
3. send ARP packet with ``DMAC:SWITCH_MAC`` ``DIP:IP:192.168.2.255`` on port 1
4. Verify packet received on port9-11

- test_trap_cpu

1. Create Route to ``CPU_PORT`` for ``IP:10.1.1.99``
2. Host interface trap already existing in config with queue4 for IP2ME
3. send on packet with ``SIP:192.168.0.1`` ``DIP:10.1.1.101`` ``DMAC:SWITCH_MAC`` on port 1
4. verify queue4 increased by 1

- test_glean_cpu_no_neighbor

1. Host interface default trap already existing in config
2. route interface for T1 LAG3 already existing in config
3. remove neighbor T1 which is for IP ``10.1.2.101`` (Keep next hop and route still there)
4. send on packet with ``SIP:192.168.0.1`` ``DIP:10.1.2.101`` ``DMAC:SWITCH_MAC`` on port 1
5. Verify no packet received on any port
6. verify queue0 increased by 1


## Test Group2: Neighbor
