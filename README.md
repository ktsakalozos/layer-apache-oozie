# Overview

## Oozie, Workflow Engine for Apache Hadoop
 
Oozie v3 is a server based Bundle Engine that provides a higher-level oozie 
abstraction that will batch a set of coordinator applications. The user will
be able to start/stop/suspend/resume/rerun a set coordinator jobs in the bundle
level resulting a better and easy operational control.

## Oozie provides:

- Oozie is a workflow scheduler system to manage Apache Hadoop jobs.
- Oozie Workflow jobs are Directed Acyclical Graphs (DAGs) of actions.
- Oozie Coordinator jobs are recurrent Oozie Workflow jobs triggered by time 
(frequency) and data availabilty.
- Oozie is integrated with the rest of the Hadoop stack supporting several types 
of Hadoop jobs out of the box (such as Java map-reduce, Streaming map-reduce, 
Pig, Hive, Sqoop and Distcp) as well as system specific jobs (such as Java programs
and shell scripts).
- Oozie is a scalable, reliable and extensible system.


## Usage

This charm leverages our pluggable Hadoop model with the `hadoop-client`
layer. This means that you will need to deploy a base Apache Hadoop cluster
and relate it to Oozie.
You may manually deploy the recommended environment as follows:

    juju deploy apache-hadoop-namenode namenode
    juju deploy apache-hadoop-resourcemanager resourcemanager
    juju deploy apache-hadoop-slave slave
    juju deploy apache-hadoop-plugin plugin
    juju deploy apache-oozie oozie

    juju add-relation resourcemanager namenode
    juju add-relation slave resourcemanager
    juju add-relation slave namenode
    juju add-relation plugin resourcemanager
    juju add-relation plugin namenode
    juju add-relation plugin oozie

At this point you will then need to expose hue:

    juju expose oozie

And then browse to the OOZIE_IP:OOZIE_PORT shown in 'juju status --format tabular'
to see the web console.

## Test deployment

Oozie comes with a set of sample jobs. We will be triggering the `map-reduce` one.

    juju ssh oozie/0
    sudo su oozie
    cd /tmp
    cp /usr/lib/oozie/oozie-examples.tar.gz /tmp
    tar -zxvf ./oozie-examples.tar.gz

At this point you need to update the job properties file of the `map-reduce`
with the hadoop namenode and resource manager of your hadoop cluster.
Edit ./examples/apps/map-reduce/job.properties and set:

    nameNode=hdfs://namenode-0:8020
    jobTracker=resourcemanager-0:8032

Upload the exampled directory to HDSF and trigger the job.
    
    hadoop  fs -put examples examples
    oozie job -oozie http://localhost:11000/oozie -config ./examples/apps/map-reduce/job.properties -run

Going back to the web console you should see the job RUNNING or you could query the job status via:

    oozie job -oozie http://localhost:11000/oozie -info <JOB_ID>

## Contact Information

- <bigdata-dev@lists.launchpad.net>

## Help

- [Oozie home page](http://oozie.apache.org)
- `#juju` on `irc.freenode.net`
