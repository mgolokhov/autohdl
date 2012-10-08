import serial
import argparse
import sys


parser = argparse.ArgumentParser(description='test dcs channel')
parser.add_argument('-baud', default='115200', help='baudrate')
parser.add_argument('-port', default='COM40', help='serial port number')
p = parser.parse_args()

ser = serial.Serial(
  baudrate=p.baud,
  port=p.port
)

if ser.isOpen():
  ser.close()

ser.open()
print ser

def xoratung(arg):
#  print arg
  it = iter(arg)
  res = int(it.next(), 2)
  while True:
    try:
      res = res ^ int(it.next(), 2)
    #      print res
    except StopIteration:
      return str(res)

def calCrc(d, c='11111111'):
  newcrc = []
  newcrc.append(xoratung((d[5], d[3], d[2], c[2], c[3], c[5]))) #7th bit
  newcrc.append(xoratung((d[7], d[4], d[2], d[1], c[1], c[2], c[4], c[7]))) #6th bit
  newcrc.append(xoratung((d[7], d[6], d[3], d[1], d[0], c[0], c[1], c[3], c[6], c[7]))) #5th bit
  newcrc.append(xoratung((d[7], d[6], d[3], d[0], c[0], c[3], c[6], c[7]))) #4th bit
  newcrc.append(xoratung((d[7], d[6], d[3], c[3], c[6], c[7]))) #3d bit
  newcrc.append(xoratung((d[6], d[5], d[2], c[2], c[5], c[6]))) #2d bit
  newcrc.append(xoratung((d[7], d[5], d[4], d[1], c[1], c[4], c[5], c[7]))) #1st bit
  newcrc.append(xoratung((d[6], d[4], d[3], d[0], c[0], c[3], c[4], c[6]))) #0th bit
  return newcrc
  


def parse(packet):
#  print '\n'.join(packet)
#  print 'crc ', crc
  print 'ext tm', int(''.join((packet[0], packet[1][0])),2)
  print 'type ', int(packet[1][1:4], 2)
  print 'adr ', int(''.join((packet[1][4:], packet[2][0])), 2)
  print 'ka ', int(packet[2][1:4], 2)
  print 'enc', int(''.join((packet[2][4:], packet[3], packet[4], packet[5])), 2)


def str2bin(iStr):
  return '{0:0>8b}'.format(ord(iStr))


def main():
  state = 'idle'

  while True:
    try:
      byte = ser.read()
    except KeyboardInterrupt:
      print 'exit...'
      return
    res = str2bin(byte)
#    print res

    if state == 'idle':
      bodyCnt = 0
      packet = []
      if res[0]=='1' and res[1]=='1':
        state = 'body'
        newcrc = calCrc(res[::-1])
        packet.append(res[2:])

    elif state == 'body':
      if res[0]=='0' and bodyCnt < 6:
        bodyCnt += 1
        packet.append(res[1:])
        newcrc = calCrc(res[::-1], newcrc[::-1])
      else:
        state = 'idle'
      if bodyCnt == 5:
        state = 'tail'

    elif state == 'tail':
      if res[0] == '1' and res[1] == '0':
        if ''.join(newcrc[2:]) == res[2:]:
          print 'crc OK'
        else:
          print 'crc BAD'
        parse(packet)
        print '\n'
      state = 'idle'

def sendSpeedToDC(speed):
  '''
  msb bit - direction
  speed 0..2048
  '''
  w0 = '110100{}'.format(speed[:2])
  newcrc = calCrc(w0[::-1])
  w1 = '0{}'.format(speed[2:9])
  newcrc = calCrc(w1[::-1], newcrc[::-1])
  w2 = '0{}0111'.format(speed[9:12]) # adr 7 by default
  w3 = '10{}'.format(calCrc(w2[::-1], newcrc[::-1]))
  ser.write()



if __name__ == '__main__':
  main()
