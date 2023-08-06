#checking os platform
from sys import platform

# script configuration
import config

# wake word  detection
import pvporcupine
from pvrecorder import PvRecorder

# OSC
from pythonosc import udp_client
from pythonosc.osc_message_builder import OscMessageBuilder

#configuring porcupine
access_key = config.access_key
keyword_model_mac=['Hello_Neurons_en_mac_v2_2_0.ppn']
keyword_model_windows=['Hello-Neurons_en_windows_v2_2_0.ppn']
keyword_model_paths = ['']

if platform == 'win32': 
  keyword_model_paths = keyword_model_windows
elif platform == 'darwin': 
  keyword_model_paths = keyword_model_mac
else:
  print('Operating system not supported. Run this program on a Windows or Mac machine')


wakeword = 'Hello Neurons'

# print(pvporcupine.KEYWORDS)
porcupine = pvporcupine.create(access_key=access_key, keyword_paths=keyword_model_paths)

# Show available audio devices
for i, device in enumerate(PvRecorder.get_available_devices()):
  print('Device %d: %s' % (i, device))

# Setup OSC client
IP = '127.0.0.1'
PORT = 10000
client = udp_client.UDPClient(IP, PORT)

# init voice recorder
recorder = PvRecorder(device_index=2, frame_length=porcupine.frame_length)
recorder.start()
print(f'Listening ... Say "{wakeword}" to trigger (press Ctrl+C to exit)')

# Listen for wake word and send OSC message
try:
  while True:    
    pcm = recorder.read()
    result = porcupine.process(pcm)
    if result >= 0:
        print("Wake Word detected!")

    # Send OSC message
    builder = OscMessageBuilder(address="/wake_neurons")
    builder.add_arg(result)
    msg = builder.build()
    client.send(msg)


except KeyboardInterrupt:
  print('Stopping ...')

finally:
  recorder.delete()
  porcupine.delete()
