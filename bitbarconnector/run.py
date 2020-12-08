import argparse
import sys
import time
import json

from testdroid import Testdroid
from testdroid import RequestResponseError
from configparser import ConfigParser


###################################
# Arguments
###################################

parser = argparse.ArgumentParser(description='Run some tests.')
parser.add_argument('--api-key', dest='api_key', required=True, help='Bitbar API key')
parser.add_argument('--config-file', dest='config_file', help='Config file path')
parser.add_argument('--app-file', dest='app_file', help='App file path')
parser.add_argument('--test-file', dest='test_file', help='Test file path')

args = parser.parse_args()
testdroid = Testdroid(apikey=args.api_key, url="https://cloud.bitbar.com")

###############################
# Upload app and test files
###############################
app_file_id = testdroid.upload_file(filename=args.app_file)['id']
test_file_id = testdroid.upload_file(filename=args.test_file)['id']

###################################
# Read Bitbar Configuration from ini file
###################################

config = ConfigParser(allow_no_value=True)

config.read(args.config_file)
app_file_name = config.get('bitbar','app_file_name')
test_file_name = config.get('bitbar','test_file_name')
osType = config.get('bitbar','osType')
instrumentationRunner = config.get('bitbar','instrumentationRunner')
limitationType = config.get('bitbar','limitationType')
limitationValue = config.get('bitbar','limitationValue')
scheduler = config.get('bitbar','scheduler')
maxTestTimeout_unit = config.get('bitbar','maxTestTimeout_unit')
frameworkId = config.getint('bitbar','frameworkId')
projectId = config.getint('bitbar','projectId')
deviceId = config.getint('bitbar','deviceId')
computedDevice = config.getint('bitbar','computedDevice')
timeout = config.getint('bitbar','timeout')
maxTestTimeout_unit_value = config.getint('bitbar','maxTestTimeout_unit_value')
runAvailable = config.getboolean('bitbar','runAvailable')

###############################
# Launch a test run
###############################
 
run_config = {
        "osType": osType,
        "frameworkId": frameworkId,
        "projectId": projectId,
        "instrumentationRunner": instrumentationRunner,
        "deviceIds": [deviceId],
        "computedDevices": [computedDevice],
        "limitationType": limitationType,
        "limitationValue": limitationValue,
        "runAvailable": runAvailable,
        "scheduler": scheduler,
        "timeout": timeout,
        "maxTestTimeout": { "unit": maxTestTimeout_unit, "value": maxTestTimeout_unit_value },
        "files": [{
                "id": test_file_id,
                "action": "RUN_TEST"
            }, 
            {
                "id": app_file_id,
                "action":"INSTALL"                
            }
        ]
    }

testrun = testdroid.start_test_run_using_config(json.dumps(run_config))

###############################
# Wait until test run is FINISHED
###############################
while True:
    run_state = testdroid.get_test_run(projectId, testrun['id'])['state']
    if run_state == "FINISHED":
        break
    time.sleep(5)

###############################
# Download results
###############################
testdroid.download_test_run(projectId, testrun['id'])
