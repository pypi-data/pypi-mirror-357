# Micro GC Fusion API

Micro GC Fusion API is a python module created from the INFICON Inc. Micro GC Fusion API Guide. Using this module allows users to build their program faster rather than interpereting the API guide.

## Installation

Use the package manager [pip](https://pypi.org/project/MicroGCFusionAPI/#description) to install Micro GC Fusion API.

```bash
pip install MicroGCFusionAPI
```

Use the package manager to also update to the latest version of Micro-GC-Fusion-API

```bash
pip install --upgrade MicroGCFusionAPI
```

## Usage

```python
from MicroGCFusionAPI import Fusion

#Enter Micro GC Fusion IP Address (Ex: 10.10.0.1)
f = Fusion('10.10.0.1')

#Return connected status (True / False):
f.connected()

#Return instrument status ( {'sequence': 'public:sequence-not-loaded', 'system': 'public:ready'})
status = f.status()
sequenceStatus = status['sequence']
systemStatus = status['system']
'''
Avalible Status Options: 
System States:
----------------------------------
public:bakeout
public:error-carrier-gas-pressure
public:error-method-load-failed
public:error-running-too-long
public:loading-method
public:manual-purge
public:method-running
public:preparing
public:ready
public:shutdown
public:standby
public:waiting-for-modules


Sequence States:
---------------------------------
public:error-event-sequencer-down
public:sequence-loaded
public:sequence-not-loaded
public:sequence-running


Possible Error States
---------------------------------
public:error-moduleA
public:error-moduleB
public:error-moduleC
public:error-moduleD
public:error-system-uninitialized
public:uninitialized

'''

################################################## Info #############################################################
#Subclasss of Fusion that provides information about the system

    #Return the system serial number (return: '70000001')
    f.info.serialNumber()

    #Retrun the system part number (return: 'F08504W02W02')
    f.info.partNumber()
    
    #Return the system host name (return: 'NatGas2')
    f.info.hostname()

    #Return the system storage limit status (return: 'ok', 'approaching', 'exceeded')
    f.info.storageLimit()

################################################## Network ##########################################################
#Subclass of Fusion that provides networking information
    
    #Return the networking information in JSON format:
     f.network.info()
    #Return Example:
    '''
        {'IPAddress': ['10.215.38.131'],
            'date': 1725973498712,
            'dhcpAddress': '10.215.38.131',
            'hostname': 'NatGas2',
            'macAddress': {'eth0': 'XX:XX:XX:XX:XX:XX', 'wlan0': 'XX:XX:XX:XX:XX:XX'},
            'staticIP': {'address': '10.10.1.12',
                'enabled': False,
                'gateway': '',
                'subnet': '255.255.0.0'},
            'wifiEnable': True,
            'wifiPassword': 'inficongc'}
    '''
   

    #Enable / Disable the wifi using the toggle wifi command.
    #Returns the current state of the system after toggle (return: True / False)
    f.network.toggleWifi()

    #Get the current Wifi password of the system (return: 'inficongc')
    f.network.getWifiPassword()

    #Set the wifi password of the system:
    f.network.setWifiPassword('NewWifiPassword')

    #Set the hostname of the system:
    f.network.setHostname('NewHostName')

    #Sync the system time to local computer:
    f.network.syncTime()

################################################## Control ##########################################################
#Subclass of Fusion that provides control over the system
    
    #Run the system when ready:
    f.control.run()

    #Run with run name and tags (input options: Name, [tags])
    f.control.runWithName('SampleName',['tagOne','tagTwo','tagThree'])

    #Stop a sequence in progress (the current run will run through completion)
    f.control.stopSequence()

    #Abort a current run and/or sequence immediately. Note this may cause future chromatography issues and is not recommended.
    f.control.abortCurrentRun()

    #Load a specific method using the method name:
    f.control.loadMethod('nameOfMethod')

    #Load a specifi sequence using the sequence name:
    f.control.loadSequence('nameOfSequence')

    #Reboot the system immediately
    f.control.reboot()

    #Start a bakeout procedure specified in minutes. Default is 30 minutes
    f.control.bakeout(minutes=120)

    #Send a get request with any string after ip address. Ex: https//10.215.38.3{string} where {string} = /v1/lastRun (return: JSON object)
    f.control.getStringCommand('string')

################################################## Methods ##########################################################
#Subclass of Fusion that provides access to the user methods on the system

    #Retrun all of the methods on the system in JSON structure, listed by method name
    f.methods.getAll()

    #Return a specific method by providing a method name
    f.methods.get('nameOfMethod')

    #Create a default method based on the system part number. These methods were created by INFICON GC experts and are a better starting point (Returns: name of new method)
    f.methods.methodByPN()

################################################## Module ###########################################################
#Subclass of Fusion that provides access to individual module information
#This subclass requires the user to know the system configuration and which modules are installed in the system
    #Return serial number of each module in the system (Ex: 4 module system)
    f.moduleA.serialNumber()
    f.moduleB.serialNumber()
    f.moduleC.serialNumber()
    f.moduleD.serialnumber()
    #The rest of the examples will use "moduleA" as an example

    #Return the module information in a dictionary, (return Information: column type, injector, detector)
    f.moduleA.info()
    #Return Example:
    '''
    {'column': 'Rt-Molsieve 5A, 0.25mm (10m) [Rt-Q-BOND (3m)]',
    'detector': 'TCD2',
    'injector': 'Backflush 1.0 uL',
    'reserved': '0'}
    '''
    #Return module serial number (return: '70094396')
    f.moduleA.serialNumber()

    #Return module part number (return: 'W02')
    f.moduleA.partNumber()

    #Return state of all module heaters in a dictionary
    f.moduleA.heaters()
    #Return Example:
    '''
    {'columnHeater': 59.98,
    'externalColumnHeater': 60.0,
    'flowManifoldHeater': 55.07,
    'injectorDieHeater': 89.7,
    'tcdHeater': 61.13}
    '''

    #Return current pressure(s) of the module
    f.moduleA.pressures()
    #Retrun Example:
    '''
    {'carrier': 20.0, 
    'inject': 0}
    '''

    #Return the raw TCD signal from the module (return: -188591.42065048218)
    f.moduleA.tcdSignal()

    #Return the current valve state (0 = inactive, 0.5 = active)
    f.moduleA.valves()
    #Return Ex:
    '''
    {'backflush': 0, 
    'forflush': 0, 
    'inject': 0, 
    'sample': 0.5, 
    'switch': 0}
    '''

    #Return fan duty cycle (1 = 100%)
    f.moduleA.fan()

################################################## Databrowser ######################################################
#Subclass of Fusion that provides access to the databrowser database.

    #Return the full datafile of the last run in JSON format. Note, these datafiles have a significant amount of data in them.
    f.data.lastRun()

    #Return the run ID (UUID) of the last run.  This can be used to check if a new run is available ('ea9d0e98-c254-4481-a1aa-834ab2b8e38b')
    f.data.lastRunID()

    #Return the full datafiles of the last "X" number of runs. Note, a large X valves will take a significant amount of time to process.
    f.data.getLastX(5) #grabs the last 5 runs in a list []

    #Return datafile based on the run ID (uuid)
    f.data.getData("e4aca6cd-e2a0-4148-bad3-bdbdefec4ee9")

    #Return total number of runs in database
    f.data.totalCount() #Returns integer ~ 21293

    #Return based on the query text from the API guide:
    f.data.queryText('text=foo&sortByData=DESC') #Return a list of run IDs that contain the text "foo" sort that list in decending order
    #Query Text Options:
    '''
    Query parameter	    Type	    Description
    id	                String	    A string containing the id or pipe(|) delmited ids a document can contain
    text	            String	    A string containing the text or pipe(|) delmited names a document can contain
    date	            String	    ISO8601 string containing the date or pipe(|) delmited dates for when a run was executed.
    startDate	        String	    ISO8601 string for runs after this date.
    endDate	            String	    ISO8601 string for runs before this date.
    startDateInclusive	boolean	    rue if the start date is inclusive (default), false otherwise.
    endDateInclusive	boolean	    True if the end date is inclusive (default), false otherwise.
    limit	            Integer	    The number of rows to be returned.
    offset	            Integer	    The offset within the results set.
    sortByDatum	        String	    The name of the field to sort on. Only one supported currently.
    datumSortOrder	    String	    ASC or DESC to indicate the results should be sorted by a datum element in the document in that order.
    sortByDate	        String	    ASC or DESC to indicate the results should be sorted by date in that order. (Default:DESC)
    allData	            boolean	    Flag for whether or not to return all the data. Default: false.
    includeData	        String	    The data field name to include in the return.
    countOnly	        boolean	    Flag for whether or not to data, or the total number of rows in the data set. Default: false.
    noId	            boolean	    Flag for whether or not to return $id in run. Default: false
    updatedSince	    String	    ISO8601 string for runs updated after this date.
    '''
    
    #Replace a data file to the database by providing the correct datafile JSON structure. Typically this is done by pulling data, modifying then returning
    runData = f.data.lastRun()  #Pull the datafile of the last run
    runData['annotations']['name'] = 'newSampleName' #Change the sample name by modifying the annotations/name section of the datafile 
    f.data.replaceData(runData)  #Return the datafile to the databrowser with the updated sample name

    #Add a new datafile to the databrowser, the run ID (uuid) cannot already be in the the databrowser or the upload will not work properly. 
    f.data.addNewData(datafileInJsonStructure)
    
    #Reprocess a specific datafile by sending the run ID (uuid)
    f.data.reprocess("e4aca6cd-e2a0-4148-bad3-bdbdefec4ee9")

    #Reprocess several data files by providing a list of run IDs 
    runIDList = [
        "e4aca6cd-e2a0-4148-bad3-bdbdefec4ee9",
        "24b5d865-8ac9-4d68-99dc-719772ceb6c2",
        "fa230e0e-5927-482a-a214-a696facc4bc2",
        "3e9159d9-bcf8-4050-967b-1d18661bed65"
    ]
    f.data.reprocessMany(runIDList)

    #Return a simplier version of the last run data file
    f.data.compoundResults()
    #Return Example:
    '''

    '''

################################################## Valco ############################################################
#Subclass of the Fusion enabling status and control of a connected Valco Stream Selector valve
    
    #Return a True / False if the valve is currently connected
    f.valco.enabled()

    #Return information about the valco valve in a JSON structure
    f.valco.info()
    #Return Example:
    '''
    {'dataRate': 9600, 
    'mode': 3, 
    'position': 1, 
    'positions': [1, 2, 3, 4]}
    '''

    #Return the current position of the valve (return: 4)
    f.valco.getPos()

    #Set the position of the valve changing it
    f.valco.setPos(3) # change the valve postion to postion 3

################################################## Notifications ####################################################
#Subclass of the Fusion enabling messaging through notification system within the Micro GC Fusion GUI.
    #Send Info message (Blue notification appears in bottom right of the GUI, will disappear after a few seconds)
    f.notifications.info('this is an info message')

    #Send Warning message (Yellow notification appears in the bottom right of the GUI, will stay until the GUI user removes it)
    f.notifications.error("this is a warning message")
    
    #Send Error message (Red notification appears in the bottom right of the GUI, will stay until the GUI user removes it)
    f.notifications.error('this is an error message')
```
## Contributing

Reach out to us via email with questions: fusion.syr@inficon.com

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Changelog
### Version 0.0.8
-Add numpy dependency
-Add get total number of runs in database request
-Bug fix for adding conditioning methods
-Bug fix for compound result annotations
### Version 0.0.7
-Add bakeout command
-Add getStringCommand
-Add preset method
-Clear all method preset option
### Version 0.0.6
-Readme typo fix
-MethodByPN bug fix & installation issue
-Removed Manifest.in from package
### Version 0.0.5
-Homepage update and bug fixes
### Version 0.0.4
-Error handling for invalid ip address

