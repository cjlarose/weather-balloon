namespace py wb_services.hosts

struct Datapoint {
    1: i32 time;
    2: double value;
}

typedef map<string, list<Datapoint>> Metrics

struct Host {
    1: string id;
    2: string display_name;
    3: string address;
}

service Hosts {
    void set_hosts(1: list<Host> hosts);
    Metrics get_metrics(1: string host_name, 2: string key);
}
