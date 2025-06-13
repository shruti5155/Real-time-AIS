ais_temp1=['date_time','start_char','header','vender_id','firmware_version','packet_type','packet_history','imie_no','VRN','GPS_fix','date','time','latitude','latitude_dir','logitude','logitude_dir','end_char']

def extract_packet_info(packet):
    packet_list=packet.split(',') 
    packet_dict=dict(zip(ais_temp1,packet_list))
    return packet_dict



packet="28012025_121750,$,AIS,LIT1,AIS01.1,NR1,L,868517078931239,MH14CD4321,1,28012025,121753,18.523807,N,73.815727,E,*"
info=extract_packet_info(packet)  # Output: 28012025_121750,$,A


