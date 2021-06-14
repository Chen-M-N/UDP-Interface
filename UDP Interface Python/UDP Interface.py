# -*- coding: utf-8 -*-
"""
Created on Sun Jun  6 20:21:33 2021

@author: Chen Mengnan
"""
import UDP_class
import sim_parameters_class
import numpy as np
IP="127.0.0.1"
writePort=8847
readPort=8848
Labview_Receive_Address=(IP,writePort)
Labview_Send_Address=(IP,readPort)

sim=sim_parameters_class.sim_parameters()
u=UDP_class.UDP_class(IP,writePort,readPort)      
u.do_open_UDP()
u.set_TX_parameters(sim,Labview_Receive_Address)
u.set_RX_parameters(sim,Labview_Receive_Address)
for i in range(100):
    print('This is the',i,'th test:')
#   Data generation
#   sim.data=np.random.randint(5,size=sim.data_size) #generate random int with data_size 
    sim.array=np.random.rand(sim.K,sim.M)+1j*np.random.rand(sim.K,sim.M) #generate random complex array
#    sim.array=np.random.rand(sim.K,sim.M)       #generate random real array
    sim.UDP_data_packet_size=np.random.randint(99)
    u.do_UDP_write_data(sim,Labview_Receive_Address)
    u.do_UDP_read_data(sim,Labview_Send_Address)
    u.do_evaluate(sim,Labview_Receive_Address)
    if u.retransmission==1:
        break
    print('-------------------------------------------');
    print(' ');
    print(' ');
    print('' );
u.do_close_UDP()
