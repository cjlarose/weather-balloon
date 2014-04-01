namespace py wb_services.cloud

struct UserStats {
    1: i32 cpu_time_seconds;     // multiplied by cpus
    2: i32 total_uptime_seconds; // not adjusted by number of cpus
    3: i32 instance_count;
    4: bool is_staff;
    5: string username;
}

service Cloud {
    list<UserStats> get_leaderboard(1: i32 start_time, 2: i32 end_time);
    list<UserStats> get_user_stats(1: i32 start_time, 2: i32 end_time, 3: string username);
}
