# Copyright 2013-2014 Massachusetts Open Cloud Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the
# License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an "AS
# IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.  See the License for the specific language
# governing permissions and limitations under the License.

"""Unit tests for cli.py"""

from time import sleep
from haas import model, api, cli
import pytest
from haas import config
from haas.cli import cfg
import unittest

config.load()


print "LIST OF SECTIONS --->",cfg.sections()

# Here's the fake HTTP infrastructure. Use monkeypatch to stash the method, url,
# and data and return a fake status code, then return them when needed.
#
# will need updating to provide data results for query.
#
class FakeResponse:
    method = None               # 
    url = None                  # static class variables
    data = {}                   # empty dict 
    text = ""                   # empty string
    
    def __init__(self, method, url, data):#, response):
        self.status_code = 200       # always return 200 OK
        FakeResponse.method = method # 
        FakeResponse.url = url       # class (not instance) variables
        FakeResponse.data = data     # 
        FakeResponse.text = ""
        print "Fake is Initialized ++++ "

    @staticmethod
    def check(method, url, values):
        """ checks method and URL.
        'values': if None, verifies no data was sent.
        if list of (name,value) pairs, verifies that each pair is in 'values'
        """
        print "url fake: ", FakeResponse.url
        print "values: ", FakeResponse.data
        assert FakeResponse.method == method
        assert FakeResponse.url == url
        if not bool(values):
            assert FakeResponse.data == {}
        else:
            for key,value in values.iteritems():
                print "check values",key, value
                print FakeResponse.data
                assert FakeResponse.data[key] == value
        assert FakeResponse.text == ""

@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    monkeypatch.setattr('haas.cli.do_put',
                        lambda url,data={}: FakeResponse('PUT', url, data))
    monkeypatch.setattr("haas.cli.do_post",
                        lambda url,data={}: FakeResponse('POST', url, data))
    monkeypatch.setattr("haas.cli.do_delete",
                        lambda url: FakeResponse('DELETE', url, {}))
    monkeypatch.setattr("haas.cli.do_get",
                        lambda url: FakeResponse('GET', url, {}))




class TestCLI(unittest.TestCase):
    """ Test it.
    Note that these only test that (a) the cli functions don't crash,
    and (b) the http parameters match what we expect. 
    """
    
    def setUp(self):
        if not cfg.has_section('client'):
            cfg.add_section('client')
        cfg.set('client', 'endpoint', 'http://abc:5000')

    
                            #User CLI calls
    def test_user_create(self):
        cli.user_create('joe', 'password')
        FakeResponse.check('PUT', 'http://abc:5000/user/joe', 
                           {'password':'password'})

    def test_user_delete(self):
        cli.user_delete('sam')
        FakeResponse.check('DELETE', 'http://abc:5000/user/sam', {})

                          #Network CLI calls
    
    def test_network_create(self):
        cli.network_create('net10', 'group1', None, 3)
        FakeResponse.check('PUT', 'http://abc:5000/network/net10',
                           {'creator':'group1', 'access':None,'net_id':3})
   
    def test_network_create_simple(self):
        cli.network_create_simple('net11', 'proj1')
        FakeResponse.check('PUT', 'http://abc:5000/network/net11',
                            {'creator': 'proj1', 'access': 'proj1', 'net_id':""})

    def test_network_delete(self):
        cli.network_delete('net10')
        FakeResponse.check('DELETE', 'http://abc:5000/network/net10', {})

    
                            #Project CLI test
    
    # This does not work , PUT vs POST actually taking url from previous function
    def test_project_create(self):
        cli.project_create('proj1')
        FakeResponse.check('PUT', 'http://abc:5000/project/proj1', {})
    
    
    def test_project_delete(self):
        cli.project_delete('proj1')
        FakeResponse.check('DELETE', 'http://abc:5000/project/proj1', {})

    def test_project_add_user(self):
        cli.project_add_user('proj1', 'sam')
        FakeResponse.check('POST', 'http://abc:5000/project/proj1/add_user',
                           {'user':'sam'})

    def test_project_remove_user(self):
        cli.project_remove_user('proj1', 'sam')
        FakeResponse.check('POST','http://abc:5000/project/proj1/remove_user',
                           {'user':'sam'})




    def test_project_connect_node(self):
        cli.project_connect_node('proj1', 'node1')
        FakeResponse.check('POST', 'http://abc:5000/project/proj1/connect_node',
                           {'node':'node1'})

    def test_project_detach_node(self):
        cli.project_detach_node('proj1', 'node1')
        FakeResponse.check('POST', 'http://abc:5000/project/proj1/detach_node',
                           {'node':'node1'})


                          #Head Node CLI test
    
    def test_headnode_start(self):
        cli.headnode_start('hn-0')
        FakeResponse.check('POST', 'http://abc:5000/headnode/hn-0/start', {})

    def test_headnode_create(self):
        cli.headnode_create('hn-0', 'proj1', 'img1')
        FakeResponse.check('PUT', 'http://abc:5000/headnode/hn-0',
                           {'project': 'proj1',
                            'base_img':'img1'})

    def test_headnode_delete(self):
        cli.headnode_delete('hn-0')
        FakeResponse.check('DELETE', 'http://abc:5000/headnode/hn-0', {})    
    
    
    def test_headnode_stop(self):
        cli.headnode_stop('hn-1')
        FakeResponse.check('POST', 'http://abc:5000/headnode/hn-1/stop', {})
    
                   #Head Node HNIC CLI test
    
    def test_headnode_create_hnic(self):
        cli.headnode_create_hnic('hn-0','hn-0-eth0')
        FakeResponse.check('PUT','http://abc:5000/headnode/hn-0/hnic/hn-0-eth0', {})

    def test_headnode_delete_hnic(self):
        cli.headnode_delete_hnic('hn-0','hn-0-eth0')
        FakeResponse.check('DELETE', 'http://abc:5000/headnode/hn-0/hnic/hn-0-eth0', {})
   
    def test_headnode_connect_network(self):
        cli.headnode_connect_network('hn-0','hn-0-eth0','hammernet')
        FakeResponse.check('POST','http://abc:5000/headnode/hn-0/hnic/hn-0-eth0/connect_network',
                           {'network':'hammernet'})
    
    def test_headnode_detach_network(self):
        cli.headnode_detach_network('hn-0','hn-0-eth0')
        FakeResponse.check('POST','http://abc:5000/headnode/hn-0/hnic/hn-0-eth0/detach_network',
                           {})
         
                   #Node CLI test

    def test_node_register(self):
        cli.node_register('node-99','ipmihost','root','saturn')
        FakeResponse.check('PUT','http://abc:5000/node/node-99',
                           {'ipmi_host':'ipmihost',
                            'ipmi_user': 'root',
                            'ipmi_pass': 'saturn'})
   
    def test_node_delete(self):
        cli.node_delete('node-99')
        FakeResponse.check('DELETE','http://abc:5000/node/node-99', {})
    
    def test_node_power_cycle(self):
        cli.node_power_cycle('node-99')
        FakeResponse.check('POST','http://abc:5000/node/node-99/power_cycle',{})
    
    
    
    def test_node_register_nic(self):
        cli.node_register_nic( 'node-99','eth0','DE:AD:BE:EF:20:14')
        FakeResponse.check('PUT','http://abc:5000/node/node-99/nic/eth0',
                           {'macaddr':'DE:AD:BE:EF:20:14'})

    def test_node_delete_nic(self):
        cli.node_delete_nic('node-99','eth0')
        FakeResponse.check('DELETE','http://abc:5000/node/node-99/nic/eth0', {})
 
    
    def test_node_connect_network(self):
        cli.node_connect_network('node-99','eth0','hammernet')
        FakeResponse.check('POST','http://abc:5000/node/node-99/nic/eth0/connect_network',
                            {'network':'hammernet'})
    
    def test_node_detach_network(self):
        cli.node_detach_network('node-98','eth1')
        FakeResponse.check('POST','http://abc:5000/node/node-98/nic/eth1/detach_network', {})
     
        
                        #Port CLI tests
    
    def test_port_register(self):
        cli.port_register('1')
        FakeResponse.check('PUT','http://abc:5000/port/1', {}) 
            
    def test_port_delete(self):
        cli.port_delete('1')
        FakeResponse.check('DELETE','http://abc:5000/port/1', {})
    
    
    def test_port_connect_nic(self):
        cli.port_connect_nic('1', 'node-99', 'eth1')
        FakeResponse.check('POST','http://abc:5000/port/1/connect_nic',
                           {'node': 'node-99', 'nic': 'eth1'})

    def test_port_detach_nic(self):
        cli.port_detach_nic('1')
        FakeResponse.check('POST','http://abc:5000/port/1/detach_nic', {})

                    # List or Show Commands

    def test_list_free_nodes(self):
        cli.list_free_nodes()
        FakeResponse.check('GET','http://abc:5000/free_nodes', {})

    def test_list_project_nodes(self):
        cli.list_project_nodes('proj1')
        FakeResponse.check('GET','http://abc:5000/project/proj1/nodes', {})

    def test_list_project_network(self):
        cli.list_project_networks('proj1')
        FakeResponse.check('GET','http://abc:5000/project/proj1/networks', {})

    def test_show_node(self):
        cli.show_node('node-95')
        FakeResponse.check('GET','http://abc:5000/node/node-95', {})

    def test_show_headnode(self):
        cli.show_headnode('hn-0')
        FakeResponse.check('GET','http://abc:5000/headnode/hn-0', {})

    def test_list_headnode_images(self):
        cli.list_headnode_images()
        FakeResponse.check('GET','http://abc:5000/headnode_images', {})

    def test_show_console(self):
        cli.show_console('node-96')
        FakeResponse.check('GET','http://abc:5000/node/node-96/console', {})

    def test_start_console(self):
        cli.start_console('node-96')
        FakeResponse.check('PUT','http://abc:5000/node/node-96/console', {})

    def test_stop_console(self):
        cli.stop_console('node-96')
        FakeResponse.check('DELETE','http://abc:5000/node/node-96/console', {})

    
    
    
        
        

