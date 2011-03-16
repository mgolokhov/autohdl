from autohdl.all import *


top = 'YOUR_TOP_MODULE_NAME'

aldec.export()
# test them ALL!
#aldec.tb(iTopModule = top)

# default - batch mode
#synthesis.run(iTopModule = top)

# wanna to run in gui mode?
#synthesis.run(iMode = 'synplify_gui', iTopModule = top)

#implement.run(iTopModule = top)
