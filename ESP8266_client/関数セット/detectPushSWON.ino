boolean detectPushSWON() {
    static boolean prev_sw_status = false;
    boolean current_sw_status = !digitalRead(2); 
    boolean push_detected = (prev_sw_status == false) && (current_sw_status == true);
    prev_sw_status = current_sw_status;
    if(push_detected){
        delay(100); //チャタリング対策
        return push_detected;
    }
}