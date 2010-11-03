from autohdl.all import *


iTopModule = 'ctrl_v2_kiortest'

#dsn = structure.Design(iName = iTopModule)
#print dsn
# test them ALL!
aldec.tb(iTopModule = iTopModule)

# default - batch mode
#synthesis.run(iTopModule = iTopModule)

# wanna to run in gui mode?
#synthesis.run('synplify_gui', iTopModule)

#implement.run(iTopModule = iTopModule)
