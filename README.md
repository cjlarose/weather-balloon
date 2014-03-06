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
&geq; 1.5, but the Dockerfile will install version 1.3. I've forked and patched
the repository with this change, which we can pull and use.

    git clone https://github.com/cjlarose/collectd-graphite.git
    docker build -t graphite collectd-graphite
    docker run -d -p 8080 -p 2003 graphite

This will expose Graphite's web interface and HTTP API (from port 8080) and
Carbon's plaintext metrics collection server (from port 2003). If you run
`docker ps`, you can see which ports on the host forward to the Graphite
container.

    docker ps
    CONTAINER ID        IMAGE                      COMMAND                CREATED             STATUS              PORTS
    134f523e4fe9        graphite:latest     /bin/sh -c exec supe   3 seconds ago       Up 2 seconds        0.0.0.0:49161->2003/tcp, 0.0.0.0:49162->8080/tcp, 2004/tcp, 22/tcp, 25826/udp, 7002/tcp

In this case, you can point your browser to your host's port `49162` and see
the Graphite dashboard, but we don't have any metrics in yet, so it's pretty
boring.

### Nagios

    docker build -t nagios nagios
    docker run -d -p 80 -name nagios nagios

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

Now, the hosts service supports just two methods, `set_hosts(list<hosts>
hosts)` and `get_metrics(string host_id)`. When `set_hosts` is called, the host
service removes all hosts currently monitored by Nagios, then adds all of the
hosts that were passed in. Then, it sends a "RESTART_PROGRAM" command to
[Nagios' external commands interface], which, as you might imagine, restarts
the monitoring daemon.

When `get_metrics` is called, the hosts service performs a request against
[Graphite's HTTP API][4] to get JSON, then marshalls the response into the
format specified by [the interface][2].

In Docker, the hosts service container needs to be able to share files with the
running Nagios container, so here, we make use of [data volumes][6]. This is so
the hosts service can write the new list of hosts every time it's updated (i.e.
`set_hosts` was invoked). It also needs access to Graphite's API, so here we
make use of [container linkage][7].

To run it:

    docker build -t wb_hosts hosts
    docker run -d -p 8000 -volumes-from nagios -link graphite:graphite wb_hosts

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
