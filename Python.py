MainService.py
#필요한 기능 import
import socket, threading;
import time
import sys
import RPi.GPIO as GPIO
from sdk.api.message import Message
from sdk.exceptions import CoolsmsException
from random import *

GPIO.setwarning(False)
GPIO.setmode(GPIO.BCM)

sensor = 18

GPIO.setup(sensor, GPIO.OUT)

EMULATE_HX711 = False

i = str(randint(1000, 9999))
# 무게 센서 사용 준비
referenceUnit = 1
if not EMULATE_HX711:
  import RPi.GPIO as GPIO
  from hx711 import HX711
else:
  from emulated_hx711 import HX711
  
def cleanAndExit():
  print("Cleaning...")
  
  if not EMULATE_HX711:
    GPIO.cleanup()
  
  print("Bye!")
  sys.exit()
#coolSMS 설정 및 API 인증
api_key = "NCS75PSB2MPWNBPK"
api_secret = "RPYGG0WZPDOYHTPIUXMDMOMLLOYRSNRD"

params = dict()
params['type'] = 'sms'
params['to'] = '01020820957'
params['from'] = '01020820957'
params['text'] = 'your temporary password is " + i
cool = Message(api_key, api_secret)
# 무게 센서 설정
hx = HX711(5, 6)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(448)
hx.reset()
hx.tare()
# 바인더 함수(server-client간 데이터를 msg 변수로 통신)
def binder(client_socket, addr):
  print('Connected by', addr):
  try:
    while True:
      data = client_socket.recv(4);
      length = int.from_bytes(data, "little");
      data = client_socket_recv(length);
      msg = data.decode();
      print(msg);
      msg = i + "echo : " + msg;
      data = msg.encode();
      length = len(data);
      client_socket.sendall(length.to_bytes(4, byteorder='little;));
      client_socket.sendall(data);
      while True:
        try:
          val = hx.get_weight(5)
          print(val)
          
          hx.power_down()
          hx.power_up()
          time.sleep(0.1)
          if val>30:
            try:
              time.sleep(5)
              GPIO.output(sensor, False)
              time.sleep(5)
              GPIO.output(sensor, True)
              response = cool.send(params)
              sleep(2)
              break
              if "error_list" in response:
                print("Error List : %s" % response['error_list'])
            except CoolsmsException as e:
              print("Error code : %s " % e.code)
              print("Error Message : %s" % e.msg)
            break     
        except(KeyboardInterrupt, SystemExit):
          cleanAndExit()
  except:
    print("connection termination");
  finally:
    client_socket.close();
# 소켓 생성 및 포트 번호 설정
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
server_socket.bind(('', 5766));
server_socket.listen();
# 소켓 통신 시작
try:
  while True:
    client_socket, addr = server_socket.accept();
    th = threading.Thread(target=binder, args=(client_socket, addr));
    th.start();
except:
  print("server");
finally:
  server_socket.close();

                    