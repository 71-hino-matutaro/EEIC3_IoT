boolean syncNTPTime(const char* ntp_server){
    unsigned long unix_time=getNTPtime();
    if(unix_time>0){
        setTime(unix_time);
        return true;
    }
    return false;
}