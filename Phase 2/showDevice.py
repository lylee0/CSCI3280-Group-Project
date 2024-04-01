import pyaudio

def getDeviceList():
    p = pyaudio.PyAudio()
    returnList = []
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
            returnList.append([i, p.get_device_info_by_host_api_device_index(0, i).get('name')])
    print(returnList)
    return returnList

def getOutputDeviceList():
    p = pyaudio.PyAudio()
    returnList = []
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        device_info = p.get_device_info_by_host_api_device_index(0, i)
        if device_info.get('maxOutputChannels') > 0:
            print("Output Device ID:", i)
            print("    Name:", device_info.get('name'))
            returnList.append([i, device_info.get('name')])
    print(returnList)
    return returnList

if __name__ == "__main__":
    getDeviceList()
    getOutputDeviceList()