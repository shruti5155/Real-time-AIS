# Updated Flask App for Deployment on Render
# Key Fix: Removed absolute Windows path and replaced with relative path.
# Added dynamic PORT handling for Render deployment.

from flask import Flask, render_template, request, redirect, send_from_directory, url_for
import os
import re

app = Flask(__name__, template_folder='templates')

LOGS_DIRECTORY = './logs/'
EMERGENCY_LOGS_DIRECTORY = './emergency_logs/'  # Changed from absolute Windows path

# Templates
emr_template = ['date_time', 'header', 'packet_type', 'imei', 'packet_Status', 'date_time', 'GPS_validity', 'latitude', 'latitude_dir', 'logi', 'logi_dir', 'Altitude', 'Speed', 'Distance', 'Provider', 'VRN', 'Reply_Num']

pvt_template = ['date_time', 'header', 'vender_id', 'firmware_version', 'packet_type', 'alert_ID', 'packet_Status', 'imei_no', 'VRN', 'GPS_fix', 'date', 'time', 'latitude', 'latitude_dir', 'logitude', 'logitude_dir', 'Speed', 'Heading', 'No_of_Sat', 'Altitude', 'PDOP', 'HDOP', 'Network_Op', 'Ignition', 'Main_Power_Status', 'Main_Input', 'Internal_Battery_Vol', 'Emergency_Status', 'Tamper_Alert', 'GSM_Signal_Strength', 'MCC ', 'MNC', 'LAC', 'Cell_ID', 'Cell_ID_1st', 'LAC_1st ', 'GSM_Signal_Strength_1st', 'Cell_ID_2nd', 'LAC_2nd', 'Cell_ID_3rd', 'LAC_3rd', 'GSM_Signal_Strength_3rd', 'Cell_ID_4th', 'LAC_4th', 'GSM_Signal_Strength_4th', 'Digital_Input_Status', 'Digital_Output_Status', 'Frame_Num', 'Checksum', 'end_char']

lgn_template = ['date_time', 'header', 'VRN', 'imei_no', 'firmware_version', 'Protocol_Version', 'Latitude', 'Longitude']

health_template = ['date_time', 'start_char', 'header', 'vender_id', 'firmware_version', 'imei_no', 'Battery_percentage', 'Low_battery', 'Memory_percen', 'Data_ON', 'Data_update_rate_when_ignition_OFF', 'Digital_I/o_status', 'Analog_I/o_status']

def extract_packet_info(packet, packet_type):
    if packet_type == 'PVT':
        selected_template = pvt_template
    elif packet_type == 'LGN':
        selected_template = lgn_template
    elif packet_type == 'HEL':
        selected_template = health_template
    else:
        return {}
    return dict(zip(selected_template, packet.split(',')))

def extract_emergency_packet_info(packet, packet_type):
    if packet_type in ['EPB', 'EMR']:
        return dict(zip(emr_template, packet.split(',')))
    return {}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'shruti' and password == '12345':
            return redirect(url_for('dashboard'))
        return "Invalid username or password"
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    os.makedirs(LOGS_DIRECTORY, exist_ok=True)
    all_logs = []
    for filename in os.listdir(LOGS_DIRECTORY):
        if filename.endswith(".csv"):
            match = re.match(r"(\d+)_(\d{8})\.csv", filename)
            if match:
                imei, date = match.groups()
                all_logs.append({"imei": imei, "date": date, "filename": filename})
    return render_template('dashboard.html', all_logs=all_logs)

@app.route('/logs/<filename>')
def view_ais_file(filename):
    file_path = os.path.join(LOGS_DIRECTORY, filename)
    with open(file_path, 'r') as file:
        log_content = file.readlines()[-20:]

    last_log = log_content[-1].strip()
    detected_packet = 'HEL' if 'HEL' in last_log else 'LGN' if 'LGN' in last_log else 'PVT'
    if detected_packet == 'PVT':
        log_content = log_content[1:]

    packet_dict = extract_packet_info(last_log, detected_packet)
    return render_template('view_ais_file.html', detected_packet=detected_packet, log_content=log_content, filename=filename, **packet_dict)

@app.route('/dashboard2')
def dashboard2():
    os.makedirs(EMERGENCY_LOGS_DIRECTORY, exist_ok=True)
    all_logs = []
    for filename in os.listdir(EMERGENCY_LOGS_DIRECTORY):
        if filename.endswith(".csv"):
            match = re.match(r"(\d+)_(\d{8})\.csv", filename)
            if match:
                imei, date = match.groups()
                all_logs.append({"imei": imei, "date": date, "filename": filename})
    return render_template('dashboard2.html', all_logs=all_logs)

@app.route('/emerlogs/<filename>')
def view_emr_file(filename):
    file_path = os.path.join(EMERGENCY_LOGS_DIRECTORY, filename)
    with open(file_path, 'r') as file:
        log_content = file.readlines()[-2:]

    last_log = log_content[-1].strip()
    detect_packet = 'EMR' if 'EPB' in last_log else 'UNKNOWN'

    packet_dict = extract_emergency_packet_info(last_log, detect_packet)
    return render_template('view_emr_file.html', detect_packet=detect_packet, log_content=log_content, filename=filename, **packet_dict)

@app.route('/db')
def db():
    os.makedirs(LOGS_DIRECTORY, exist_ok=True)
    return render_template('db.html', log_files=os.listdir(LOGS_DIRECTORY))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(LOGS_DIRECTORY, filename, as_attachment=True)

@app.route('/edb')
def edb():
    os.makedirs(EMERGENCY_LOGS_DIRECTORY, exist_ok=True)
    return render_template('edb.html', log_files=os.listdir(EMERGENCY_LOGS_DIRECTORY))

@app.route('/download/emergency/<filename>')
def download_emergency_file(filename):
    return send_from_directory(EMERGENCY_LOGS_DIRECTORY, filename, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render uses PORT environment variable
    app.run(debug=True, host='0.0.0.0', port=port)
