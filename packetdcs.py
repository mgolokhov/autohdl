class PacketDcs(object):
  def __init__(self, bitsNum):
    self.state = 'head'
    self.byteCnt = 0
    self.packet = []
    self.crc = '11111111'
    self.BYTES = (2*bitsNum + 9)/14 + 1
    self.d = [0,0,0,0,0,0]

  def str2bin(self, byte):
    return '{0:0>8b}'.format(ord(byte))

  def _xor(self, arg):
  #  print arg
    it = iter(arg)
    res = int(it.next(), 2)
    while True:
      try:
        res = res ^ int(it.next(), 2)
      #      print res
      except StopIteration:
        return str(res)

  def crc0x31(self, d, c = '11111111'):
    """Poly  : 0x31    x^8 + x^5 + x^4 + 1"""
    newcrc = []
    newcrc.append(self._xor((d[5], d[3], d[2], c[2], c[3], c[5]))) #7th bit
    newcrc.append(self._xor((d[7], d[4], d[2], d[1], c[1], c[2], c[4], c[7]))) #6th bit
    newcrc.append(self._xor((d[7], d[6], d[3], d[1], d[0], c[0], c[1], c[3], c[6], c[7]))) #5th bit
    newcrc.append(self._xor((d[7], d[6], d[3], d[0], c[0], c[3], c[6], c[7]))) #4th bit
    newcrc.append(self._xor((d[7], d[6], d[3], c[3], c[6], c[7]))) #3d bit
    newcrc.append(self._xor((d[6], d[5], d[2], c[2], c[5], c[6]))) #2d bit
    newcrc.append(self._xor((d[7], d[5], d[4], d[1], c[1], c[4], c[5], c[7]))) #1st bit
    newcrc.append(self._xor((d[6], d[4], d[3], d[0], c[0], c[3], c[4], c[6]))) #0th bit
    return newcrc

  def parse(self):
    """get data and check crc"""
    print 'packet:\n', '\n'.join([hex(int(''.join(i), 2)) for i in self.packet])
    for i in self.packet[:-1]:
      self.crc = self.crc0x31(i[::-1], self.crc[::-1])
    print 'calc crc:', ''.join(self.crc[2:]), hex(int(''.join(self.crc[2:]), 2))
    print 'got  crc:', self.packet[-1][2:], hex(int(self.packet[-1][2:], 2))
    for i in range(2, 8):
      if self.packet[-1][i] != self.crc[i]:
        self.d[i-2] += 1
    print self.d

  def clean(self):
    self.byteCnt = 0
    self.packet = []
    self.crc = '11111111'

  def nextByte(self, byte):
    # convert to list
    data = self.str2bin(byte)
    #    print data

    if self.state == 'head':
      if data[0] == '1' and data[1] == '1':
        self.packet.append(data)
        self.byteCnt += 1
        self.state = 'body'
    elif self.state == 'body':
      if data[0] == '0' and self.byteCnt < self.BYTES-1:
        self.packet.append(data)
        self.byteCnt += 1
      else:
        print 'Mask err body'
        self.clean()
        self.state = 'head'
      if self.byteCnt == self.BYTES-1:
        self.state = 'tail'
    elif self.state == 'tail':
      if data[0] == '1' and data[1] == '0':
        self.packet.append(data)
        self.parse()
      else:
        print 'Mask err tail'
      self.clean()
      self.state = 'head'


if __name__ == '__main__':
  dcs = PacketDcs(55)

  for i in 'C4 04 04 0F 56 14 04 04 a9 C5 4C 04 7F 57 7F 7F 7F A7'.split():
    dcs.nextByte(chr(int(i, 16)))