##############################################################################
# COPYRIGHT Ericsson 2019
# The copyright to the computer program(s) herein is the property of
# Ericsson Inc. The programs may be used and/or copied only with written
# permission from Ericsson Inc. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
##############################################################################
==============================================================================
ENMAAAS MONITORING SOLUTION DEPLOYMENT
==============================================================================

Description
--------------
This section contains an Ansible project to configure and install the full monitoring solution
for the ENMaaS deployments

The following components are installed in the environment:
1. Pre-requiste s/w: Docker, Docker-compose
2. All required docker images loaded from Tarball
3. Directory structure for monitoring tools
4. Prometheus and its supporting tools (push gateway, alert manager etc.)
5. Grafana
6. AWX (Ansible Tower)


Pre-requisites
---------------

The following components needs to be pre-installed to run the project
1. Ansible 
2. Python 2.7 (pip)


User
-----
Run the project as root user


Usage
-----
1. Ensure that all the variables are pre-filled accordingly in the Inventory file
Inventory File: installer/inventories/inventory

Variables to be set
- Base_Dir: 		Base Directory where the "monitoring" folder has to created. 
			This path has to be mounted to a persistant storage

- Grafana Port:		External Port for Grafana Web UI

- Prom Port:		External Port for Prometheus Web UI

- Host Port: 		External Port for AWX

- Push gateway port

- Alert Manager port
  
- Dockercompose ver:	Version of Docker-compose to be installed	

2. Ensure that the VERSION file is present in the root directory alongside installer folder and this Readme file

3. Execute the ansible project
$ ansible-playbook -i installer/inventories/inventory installer/install.yml


Post-Install
------------
1. Ensure that the following containers are created and UP:
awx_task
awx_web
awx_rabbitmq
awx_memcached
awx_postgres
prometheus-server
grafana-server


2. Check Docker logs for AWX. Ensure status is Successful
$ docker logs awx_task

3. Open Web browser and check for Grafana, Prometheus and AWX Tower UI access & login
	Grafana - admin/admin
	Prometheus - no cred
	AWX Tower - admin/password


Monitoring Configuration
-------------------------
After the Infra is setup:
1. Go to AWX tower, create Inventory, host, cloud-credential (cloud-user).
	- Add all the EMP nodes (or LAF nodes) as host
2. Create a new project folder under "projects" dir and add the neccesary playbooks under it.
	Projects Dir: {Base Dir}/monitoring/data/awx/projects
	Resource Dir: {Base Dir}/monitoring/data/awx/resource
3. Create new template mapping the Inventory and the Playbook under the "Project"	
