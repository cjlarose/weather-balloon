Weather Balloon: Atmosphere Monitoring
======================================

Weather Balloon is built on Docker, so you'll need to [install that][1] to get
started. Fundamentally, Weather Balloon is a collection of related services
running in Docker containers and exposing their APIs over [Apache Thrift][5].

Hosts Service
-------------

The hosts service is responsible for monitoring Atmosphere instances as well
storing and retriving instace metrics over time. Strictly speaking, though, the
service doesn't know anything about Atmosphere instances, *per se*: it just
monitors `hosts`, which are basically just a named servers with a public-facing
IP addresss. It exposes a very simple [interface][2] that is designed to be
agnostic to the implementation decisions for server monitoring and metrics
collection. Currently, the hosts service uses [Nagios][8] for monitoring and
[Graphite][9] for metrics. Here's how to set it all up, assuming that this
repository is at the present working directory.

### Graphite

DotCloud (the company behind Docker) has actually already written a good
[Dockerfile for Graphite][10]. It also includes an installation of collectd,
which we won't use. At the time of writing, though, the repo is unfortunately
unmaintained and contains one fatal bug: modern Graphite uses Django version
≥ 1.5, but the Dockerfile will install version 1.3. I've forked and patched
the repository with this change, which we can pull and use.

    git clone https://github.com/cjlarose/collectd-graphite.git

Before we build the graphite image, we need to make sure we set a
rentention policy for our metrics. Open `graphite/storage-schemas.conf` and add
an entry before the last one (called `hf`):

    [nagios]
    pattern = ^nagios\.
    retentions = 10m:90d

This says that for all keys that begin in `nagios.`, retain the metric data at
10-minute resolution for ninety days. Now we can build our graphite image and
run it in a new container.

    docker build -t graphite collectd-graphite
    docker run -d -p 8080 -p 2004 -name graphite graphite

This will expose Graphite's web interface and [HTTP API][4] (from port 8080)
and Carbon's [pickle metrics collection server][11] (from port 2004). If you run
`docker ps`, you can see which ports on the host forward to the Graphite
container.

    docker ps
    CONTAINER ID        IMAGE                      COMMAND                CREATED             STATUS              PORTS
    134f523e4fe9        graphite:latest     /bin/sh -c exec supe   3 seconds ago       Up 2 seconds        0.0.0.0:49161->2004/tcp, 0.0.0.0:49162->8080/tcp, 2004/tcp, 22/tcp, 25826/udp, 7002/tcp

In this case, you can point your browser to your host's port `49162` and see
the Graphite dashboard, but we don't have any metrics in yet, so it's pretty
boring.

### Nagios

Our Nagios image includes an installation of [Graphios][12], which takes Nagios
performance data and sends them on over to Graphite. To let our Nagios
container talk to our Graphite container, we'll use [container linkage][7].

    docker build -t nagios nagios
    docker run -d -p 80 -name nagios -link graphite:graphite nagios

Now, Nagios is up and running and exposing it's web interface. If you run
`docker ps`, you can see which port on the host forwards to the Nagios
container.

    docker ps
    CONTAINER ID        IMAGE                      COMMAND                CREATED             STATUS              PORTS
    30af95be3f2b        nagios:latest              /usr/local/bin/start   22 hours ago        Up 22 hours         0.0.0.0:49159->80/tcp

Here, you can point your browser to your host's port `49159` and see
the Nagios dashboard, but it's pretty uninteresting so far because the only
monitored host is `localhost`.

### Hosts Serivce

#### Generate Thrift files

The hosts service runs a Thrift server. It depends on some 
automatically-generated Python files. You'll need to download and install 
`thrift`. Then, generate the files for the host service, and copy them
into the hosts directory.

    thrift --gen py thriftfiles/hosts.thrift
    cp -R gen-py/wb_services hosts

#### Build the hosts service

Now, the hosts service supports just two methods, `set_hosts(list<hosts>
hosts)` and `get_metrics(string host_id)`. When `set_hosts` is called, the host
service removes all hosts currently monitored by Nagios, then adds all of the
hosts that were passed in. Then, it sends a `RESTART_PROGRAM` command to
[Nagios' external commands interface][3], which, as you might imagine, restarts
the monitoring daemon.

When `get_metrics` is called, the hosts service performs a request against
[Graphite's HTTP API][4] to get JSON, then marshalls the response into the
format specified by [the interface][2].

In Docker, the hosts service container needs to be able to share files with the
running Nagios container, so here, we make use of [data volumes][6]. This is so
the hosts service can write the new list of hosts every time it's updated (i.e.
`set_hosts` was invoked). It also needs access to Graphite's API, so here we
make use of [container linkage][7] again.

To run it:

    docker build -t wb_hosts hosts
    docker run -d -p 8000 -volumes-from nagios -link graphite:graphite wb_hosts

This will start a new container with the hosts service exposing its Thrift 
server over port 8000.

Cloud Service
-------------

The cloud service is responsible for repeatedly querying the clouds for the
most up-to-date information, storing it to a database, and providing a
well-defined way to query some of that information. Currently, it stores tons
of information, and we only use to it query "leaderboard" information--it
answers the question of which users have used the most resources. However, it
is designed to be trivially extensible.

### PostgreSQL

We use PostgreSQL to store our cloud-related data. Before you build, feel free
to modify the username, password, and database name in `cloud_db/Dockerfile`.
That's my security disclaimer.

To build:
    
    docker build -t wb_cloud_db cloud_db
    docker run -d -P -name wb_cloud_db wb_cloud_db

This container will accept database connections on port `5432`. If you'd like
to back up the data (which is probably something you should do), just fire up a
new container that links against the `wb_cloud_db` container with an image that
has `pg_dump`. The Docker documentation has a [good example][13] on how to do
something similar.

### Cloud Service

Like the hosts service, we'll have to generate some files with Thrift.

    thrift --gen py thriftfiles/cloud.thrift
    cp -R gen-py/wb_services cloud

Modify `cloud/wb_cloud/settings.py` to include the database credentials you
picked in the previous step, as well as any cloud configuration variables you'd
like to include.

Build and run:

    docker build -t wb_cloud cloud
    docker run -d -P -link wb_cloud_db:db wb_cloud

The cloud service will accept connections over port 8000.

[1]: http://docs.docker.io/en/latest/installation/ubuntulinux/
[2]: http://github.com/iPlantCollaborativeOpenSource/weather-balloon/tree/master/thriftfiles/hosts.thrift
[3]: http://nagios.sourceforge.net/docs/3_0/extcommands.html
[4]: https://graphite.readthedocs.org/en/1.0/url-api.html
[5]: http://thrift.apache.org/
[6]: http://docs.docker.io/en/latest/use/working_with_volumes/
[7]: http://docs.docker.io/en/latest/use/working_with_links_names/
[8]: http://www.nagios.com/
[9]: http://graphite.wikidot.com/
[10]: https://github.com/dotcloud/collectd-graphite
[11]: https://graphite.readthedocs.org/en/1.0/feeding-carbon.html#the-pickle-protocol
[12]: https://github.com/shawn-sterling/graphios
[13]: http://docs.docker.io/en/latest/examples/postgresql_service/#using-container-linking
