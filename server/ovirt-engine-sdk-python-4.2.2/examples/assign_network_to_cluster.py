#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2017 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import logging

import ovirtsdk4 as sdk
import ovirtsdk4.types as types

logging.basicConfig(level=logging.DEBUG, filename='example.log')

# This example will connect to the server and assign 'mynetwork'
# network to cluster 'mycluster':

# Create the connection to the server:
connection = sdk.Connection(
    url='https://engine40.example.com/ovirt-engine/api',
    username='admin@internal',
    password='redhat123',
    ca_file='ca.pem',
    debug=True,
    log=logging.getLogger(),
)

# Locate the networks service and use it to find the network:
networks_service = connection.system_service().networks_service()
network = networks_service.list(
    search='name=mynetwork and datacenter=mydatacenter'
)[0]

# Locate the clusters service and use it to find the cluster:
clusters_service = connection.system_service().clusters_service()
cluster = clusters_service.list(search='name=mycluster')[0]

# Locate the service that manages the networks of the cluster:
cluster_service = clusters_service.cluster_service(cluster.id)
cluster_networks_service = cluster_service.networks_service()

# Use the "add" method to assign network to cluster:
cluster_networks_service.add(
    network=types.Network(
        id=network.id,
        required=True,
    ),
)

# Close the connection to the server:
connection.close()
