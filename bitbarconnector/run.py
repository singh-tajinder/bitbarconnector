import argparse
import sys
import time
import json

from testdroid import Testdroid
from testdroid import RequestResponseError
from configparser import ConfigParser

class bitbar:
    def execute_test(config_file):
        
        config = ConfigParser(allow_no_value=True)

        config.read(config_file)
        bitbar_api_key = config.get('bitbar', 'bitbar_api_key')
        app_file = config.get('bitbar','app_file')
        test_file = config.get('bitbar','test_file')
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
        # Upload app and test files
        ###############################
        testdroid = Testdroid(apikey=bitbar_api_key, url="https://cloud.bitbar.com")
        app_file_id = testdroid.upload_file(filename=app_file)['id']
        test_file_id = testdroid.upload_file(filename=test_file)['id']
        
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
        
bitbar.execute_test('config.ini')