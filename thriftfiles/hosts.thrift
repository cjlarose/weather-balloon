namespace py wb_services.hosts

struct Datapoint {
    1: i32 time;
    2: double value;
}

typedef map<string, list<Datapoint>> Metrics

struct Host {
    1: string name;
    2: list<string> host_groups;
}

service Hosts {
    void set_hosts(1: list<Host> hosts);
    Metrics get_metrics(1: string host_name, 2: string key);
}
