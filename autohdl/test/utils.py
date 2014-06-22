import os

def mkCores(iPath):
    src = os.path.join(iPath, 'src')
    if not os.path.exists(src):
        os.makedirs(src)
    f = open(os.path.join(src, 'core1.v'), 'w')
    f.write('module core1 (input a, output b);' +
            'endmodule'
    )
    f.close()

    f = open(os.path.join(src, 'core2.v'), 'w')
    f.write('module core2 (input a, output b);' +
            'endmodule'
    )
    f.close()


def mkDsn1(iPath):
    src = os.path.join(iPath, 'src')
    resource = os.path.join(iPath, 'resource')
    script = os.path.join(iPath, 'script')
    for i in (src, resource, script):
        if not os.path.exists(i):
            os.makedirs(i)

    f = open(os.path.join(resource, 'build.xml'), 'w')
    f.write("""\
  <wsp>
    <dsn id="dsn1">
      <dep>../../cores</dep>
    </dsn>
  </wsp>
  """)
    f.close()

    f = open(os.path.join(src, 'dsn1_m1.v'), 'w')
    f.write('module dsn1_m1 (input a, output b);' +
            'dsn1_m2 inst0 (a, b);' +
            'core1 inst1 (a, b);' +
            'core2 inst2 (a, b);' +
            'endmodule'
    )
    f.close()

    f = open(os.path.join(src, 'dsn1_m2.v'), 'w')
    f.write('module dsn1_m2 (input a, output b);\n' +
            'endmodule'
    )
    f.close()


def mkFakeRepo(iPath):
    mkCores(os.path.join(iPath, 'cores'))
    mkDsn1(os.path.join(iPath, 'dir1', 'dir2', 'dsn1'))


if __name__ == '__main__':
    print('hi')
