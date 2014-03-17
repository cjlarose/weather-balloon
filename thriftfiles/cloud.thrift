namespace py wb_services.cloud

struct UserStats {
    1: i32 cpu_time_seconds;     // multiplied by cpus
    2: i32 total_uptime_seconds; // not adjusted by number of cpus
    3: i32 instance_count;
    4: bool is_staff;
}

service Cloud {
    list<UserStats> get_leaderboard();
}
