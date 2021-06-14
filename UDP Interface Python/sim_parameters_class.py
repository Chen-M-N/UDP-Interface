# -*- coding: utf-8 -*-
"""
Created on Sun Jun  6 21:42:52 2021

@author: Chen Mengnan
"""
import math
import numpy as np
class sim_parameters:
    def __init__(self):
        self.TX_Frequency=2320
        self.TX_Sample_Rate=5
        self.RX_Frequency=2320
        self.RX_Sample_Rate=5
        self.K=64
        self.M=4
        self.J=4
        self.waveform_name='SWH'
        self.N_iterations=4
        self.waveform_Q=7
        self.waveform_Q2=4
        self.R=0.5
        self.punc='1 1 0 1 0 '
        self.encoder='PC_convolutional'
        self.SNR=7
        self.P=math.pow(10,self.SNR/10)
        self.equalizer = 'CWCU_MMSE_low_complexity'
        self.UDP_data_packet_size=399
        self.data_type=0
        self.data_size=500
        self.data=np.random.randint(5,size=self.data_size) #generate random array with data_size 
        self.array=np.random.rand(self.K,self.M)+1j*np.random.rand(self.K,self.M)