from client.index.PersistentFilter import PersistentFilter
import time

KEY = "9a61e14f3327dcf3f251a37c63e8a6bcc439a4891ac7dde6cc0ce54d7b28546e"
data = ["6000"]

def test():
    for i in data:
        t0 = time.time()
        pf = PersistentFilter("/home/wsantos/codes/SSRS/testes/may2018/index/in/{}.pdf".format(i), "/home/wsantos/out/{}".format(i), KEY)
        pf.build_filter()
        pf.save_filter()
        del pf
        print("Total time {}".format(time.time()-t0))
        print("")

test()
