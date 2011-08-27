import serial
import argparse
import sys


parser = argparse.ArgumentParser(description='test dcs channel')
parser.add_argument('-baud', default='1000000', help='baudrate')
parser.add_argument('-port', default='COM12', help='serial port number')
p = parser.parse_args()

ser = serial.Serial(
  baudrate=p.baud,
  port=p.port
)

if ser.isOpen():
  ser.close()

ser.open()
print ser

def calCrc(d, c='11111111'):
  newcrc = []
  newcrc[0] = d[6] ^ d[4] ^ d[3] ^ d[0] ^ c[0] ^ c[3] ^ c[4] ^ c[6]
  newcrc[1] = d[7] ^ d[5] ^ d[4] ^ d[1] ^ c[1] ^ c[4] ^ c[5] ^ c[7]
  newcrc[2] = d[6] ^ d[5] ^ d[2] ^ c[2] ^ c[5] ^ c[6]
  newcrc[3] = d[7] ^ d[6] ^ d[3] ^ c[3] ^ c[6] ^ c[7]
  newcrc[4] = d[7] ^ d[6] ^ d[3] ^ d[0] ^ c[0] ^ c[3] ^ c[6] ^ c[7]
  newcrc[5] = d[7] ^ d[6] ^ d[3] ^ d[1] ^ d[0] ^ c[0] ^ c[1] ^ c[3] ^ c[6] ^ c[7]
  newcrc[6] = d[7] ^ d[4] ^ d[2] ^ d[1] ^ c[1] ^ c[2] ^ c[4] ^ c[7]
  newcrc[7] = d[5] ^ d[3] ^ d[2] ^ c[2] ^ c[3] ^ c[5]
  return crc
  


def parse(iPacket, all):
  atype = int(iPacket[0][0:5], 2)
  if atype == 1:
    print 'type: set ust for drive'
    print ' bus: ', int(iPacket[1][1:5], 2),
    print ' addr: ', int(iPacket[1][5:]+iPacket[2][:2], 2),
    print ' ust: ', int(iPacket[2][2:]+iPacket[3], 2),
    print ' crc: ', int(iPacket[4], 2)
  elif atype == 2:
    print 'type: set grp'
    print ' bus: ', int(iPacket[1][6:]+iPacket[2][0:2], 2),
    print ' addr: ', int(iPacket[2][2:6], 2),
    print ' grp: ', int(iPacket[2][6]+iPacket[3], 2),
    print ' crc: ', int(iPacket[4], 2)
  elif atype == 3:
    print 'type: set ust for grp'
    print ' grp: ', int(iPacket[1][1:]+iPacket[2][:2], 2),
    print ' ust: ', int(iPacket[2][2:]+iPacket[3], 2),
    print ' crc: ', int(iPacket[4], 2)

def str2bin(iStr):
  return '{0:0>8b}'.format(ord(iStr))


def main():
  state = 'idle'
  bodyCnt = 0
  packet = []
  all = []

  while True:
    try:
      byte = ser.read()
    except KeyboardInterrupt:
      print 'exit...'
      return
    res = str2bin(byte)
    print res

    if state == 'idle':
      all = []
      if res[0]=='1' and res[1]=='1':
        state = 'body'
        packet.append(res[2:])
        all.append(res)
      else:
        packet = []

    elif state == 'body':
      if res[0]=='0' and bodyCnt < 4:
        bodyCnt += 1
        packet.append(res[1:])
        all.append(res)
      else:
        packet = []
        state = 'idle'
      if bodyCnt == 3:
        bodyCnt = 0
        state = 'tail'

    elif state == 'tail':
      if res[0] == '1' and res[1] == '0':
        packet.append(res[1:])
#        all.append(res)
        print '------------'
        print packet
        parse(packet, all)
        print '\n'
      else:
        packet = []
      state = 'idle'
      packet = []




if __name__ == '__main__':
  main()
