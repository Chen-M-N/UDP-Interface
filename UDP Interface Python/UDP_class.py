# -*- coding: utf-8 -*-
"""
Created on Sun Jun  6 20:33:51 2021

@author: Chen Mengnan
"""
import socket
import numpy as np
import struct
np.set_printoptions(precision=4)
class UDP_class:
   def __init__(self,IP,writePort,readPort):
       self.localIP  = IP
       self.writePort= writePort
       self.readPort = readPort
       self.retransmission=0
   def do_open_UDP(self):
       self.u=socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)
   def set_TX_parameters(self,sim,LabviewAddress):
       msg_header=bytearray()
       msg_content=bytearray()
       TX_command_content=[]
       TX_command_content.append(bytearray(np.single(sim.TX_Frequency)))
       TX_command_content.append(bytearray(np.single(sim.TX_Sample_Rate)))
       TX_command_content.append(bytearray(np.single(sim.J)))
       TX_command_content.append(bytearray(np.single(sim.R)))
       #compare sim_parameters.encoder
       if 'PC_convolutional'==sim.encoder:
           TX_command_content.append(bytearray(np.single(0)))
       elif 'convolutional'==sim.encoder:
           TX_command_content.append(bytearray(np.single(1)))
       else:
           TX_command_content.append(bytearray(np.single(2)))
       TX_command_content.append(bytearray(np.single(sim.K)))
       TX_command_content.append(bytearray(np.single(sim.M)))
       TX_command_content.append(bytearray(np.single(sim.P)))
       #compare sim_parameters.waveform.name
       if 'SWH'==sim.waveform_name:
           TX_command_content.append(bytearray(np.single(0)))
       elif 'OTFS'==sim.waveform_name:
           TX_command_content.append(bytearray(np.single(1)))
       elif 'OCDM'==sim.waveform_name:
           TX_command_content.append(bytearray(np.single(2)))
       else:
           TX_command_content.append(bytearray(np.single(3)))
       TX_command_content.append(bytearray(np.single(sim.waveform_Q)))
       TX_command_content.append(bytearray(np.single(sim.waveform_Q2)))
       #add puncture information
       #change to list with string and remove spaces
       punc_list=sim.punc.split()
       #get the length of punc_list
       TX_command_content.append(bytearray(np.single(len(punc_list)))) 
       #add the punc_list elements to the TX_command_content
       for ele in range(len(punc_list)):
           TX_command_content.append(bytearray(np.single(punc_list[ele])))
       #just arrange the order of TX_command_content
       TX_command_content.reverse()
       #combine the arraybyte
       for i in range(len(TX_command_content)):
           msg_content+=TX_command_content[i]
       msg_content.reverse()
       #add header
       msg_header=bytearray(np.single(len(TX_command_content)))+bytearray(np.single(1))+bytearray(np.single(0)) #command payload size+total number of command packet+ID
       msg_header.reverse()
       msg=msg_header+msg_content
       self.u.sendto(msg,LabviewAddress)
   def set_RX_parameters(self,sim,LabviewAddress):
       msg_header=bytearray()
       msg_content=bytearray()
       RX_command_content=[]
       RX_command_content.append(bytearray(np.single(sim.RX_Frequency)))
       RX_command_content.append(bytearray(np.single(sim.RX_Sample_Rate)))
       RX_command_content.append(bytearray(np.single(sim.N_iterations)))
       #compare sim_parameters.equalizer
       if 'CWCU_MMSE_low_complexity'==sim.equalizer:
           RX_command_content.append(bytearray(np.single(0)))
       elif 'CWCU_MMSE_general'==sim.equalizer:
           RX_command_content.append(bytearray(np.single(1)))
       else:
           RX_command_content.append(bytearray(np.single(2)))
       RX_command_content.reverse()
       #combine the arraybyte
       for i in range(len(RX_command_content)):
           msg_content+=RX_command_content[i]
       msg_content.reverse()
       #add header
       msg_header=bytearray(np.single(len(RX_command_content)))+bytearray(np.single(1))+bytearray(np.single(1)) #command payload size+total number of command packet+ID
       msg_header.reverse()
       msg=msg_header+msg_content
       self.u.sendto(msg,LabviewAddress)
   def do_UDP_write_data(self,sim,LabviewAddress):
       if sim.data_type==1: 
          self.send_data=sim.data
          self.divisor=int(sim.data_size/sim.UDP_data_packet_size) 
          self.remainder=sim.data_size%sim.UDP_data_packet_size
          if self.remainder!=0:
              self.total_number_of_packets=self.divisor+1
          else:
              self.total_number_of_packets=self.divisor
          for j in range(self.divisor): #each time generate a fix size UDP Data packet
              #before each transmission,everything should be cleared
              data_content_msg=bytearray()
              data_header_msg=bytearray()
              msg=bytearray()
              #generate data header for each loop  #Data type+data payload size+total number of command packet+ID    
              data_header_msg=bytearray(np.single(1))+bytearray(np.single(sim.UDP_data_packet_size))+bytearray(np.single(self.total_number_of_packets))+bytearray(np.single(2))
              data_header_msg.reverse()
              for i in range(sim.UDP_data_packet_size): 
                  buffer=bytearray(np.single(self.send_data[j*sim.UDP_data_packet_size+i]))
                  buffer.reverse()
                  data_content_msg=data_content_msg+buffer
              msg=data_header_msg+data_content_msg
              self.u.sendto(msg,LabviewAddress)
          if self.remainder!=0: #generate random bits with the size of remainder
              #clear all data
              data_content_msg=bytearray()
              data_header_msg=bytearray()
              msg=bytearray()
              #generate data header  #Data type+data payload size+total number of command packet+ID    
              data_header_msg=bytearray(np.single(1))+bytearray(np.single(self.remainder))+bytearray(np.single(self.total_number_of_packets))+bytearray(np.single(2))
              data_header_msg.reverse()
              for j in range(self.remainder): #generate last data packet
                  remaining_data=bytearray(np.single(self.send_data[self.divisor*sim.UDP_data_packet_size+j]))
                  remaining_data.reverse()
                  data_content_msg=data_content_msg+remaining_data
              msg=data_header_msg+data_content_msg
              self.u.sendto(msg,LabviewAddress)
       else:   #generate random complex matrix
          #get the real and imag part and change the data precision
          new_array=np.empty(0)
          if(np.isrealobj(sim.array)):
              print('The input array is the real array')
              self.send_data=np.single(sim.array)
              self.send_data=self.send_data.reshape(-1,1)
          else:
              print('The input array is the complex array')
              for i in range(sim.K):
                  buffer=[sim.array[i,:]]
                  real_part=np.single(np.real(buffer))
                  imag_part=np.single(np.imag(buffer))
                  m=np.concatenate((real_part,imag_part))
                  m=m.transpose()
                  n=m.reshape(-1,1)
                  new_array=new_array.reshape(-1,1)
                  new_array=np.concatenate((new_array,n))
                  self.send_data=new_array
                 
          self.divisor=int(len(self.send_data)/sim.UDP_data_packet_size) 
          self.remainder=len(self.send_data)%sim.UDP_data_packet_size
          if self.remainder!=0:
              self.total_number_of_packets=self.divisor+1
          else:
              self.total_number_of_packets=self.divisor
          for j in range(self.divisor): #each time generate a fix size UDP Data packet
              #before each transmission,everything should be cleared
              data_content_msg=bytearray()
              data_header_msg=bytearray()
              msg=bytearray()
              #generate data header for each loop  #Data type+data payload size+total number of command packet+ID    
              data_header_msg=bytearray(np.single(0))+bytearray(np.single(sim.UDP_data_packet_size))+bytearray(np.single(self.total_number_of_packets))+bytearray(np.single(2))
              data_header_msg.reverse()
              for i in range(sim.UDP_data_packet_size): 
                  buffer=bytearray(np.single(self.send_data[j*sim.UDP_data_packet_size+i]))
                  buffer.reverse()
                  data_content_msg=data_content_msg+buffer
              msg=data_header_msg+data_content_msg
              self.u.sendto(msg,LabviewAddress)
          if self.remainder!=0: #generate random bits with the size of remainder
              #clear all data
              data_content_msg=bytearray()
              data_header_msg=bytearray()
              msg=bytearray()
              #generate data header  #Data type+data payload size+total number of command packet+ID    
              data_header_msg=bytearray(np.single(0))+bytearray(np.single(self.remainder))+bytearray(np.single(self.total_number_of_packets))+bytearray(np.single(2))
              data_header_msg.reverse()
              for j in range(self.remainder): #generate last data packet
                  remaining_data=bytearray(np.single(self.send_data[self.divisor*sim.UDP_data_packet_size+j]))
                  remaining_data.reverse()
                  data_content_msg=data_content_msg+remaining_data
              msg=data_header_msg+data_content_msg
              self.u.sendto(msg,LabviewAddress)    
   def do_UDP_read_data(self,sim,Labview_Send_Address):
       self.server = socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)
       self.server.bind(Labview_Send_Address)
       self.received_data=[]
       status_count=0
       self.data_byte=bytearray()
       while True:
               byte=self.server.recv(4096)
               if len(byte)!=0:  
                  four_byte=byte[0:4] 
                  [y]=struct.unpack('>f',four_byte)
                  if y==6: #check if data package
                      status_count=status_count+1
                      print('Waiting for new data packets...')
                      if status_count>4:
                          print('Time out')
                          print('No new packets come in,data transmission is complete ')
                          [x]=struct.unpack('>f',byte[4:8])
                          print('Status ID',y)
                          print('Current data packet size',round(x,4))
                          [x]=struct.unpack('>f',byte[8:12])
                          print('The average throughput is:',round(x,4))
                          break
                      else:
                          [x]=struct.unpack('>f',byte[8:12])
                          print('The average throughput is:',round(x,4))
                  else:
                      status_count=0;
                      print('received new data')
                      self.data_byte=self.data_byte+byte                     
       for i in range(np.int(len(self.data_byte)/4)):
           four_byte=self.data_byte[i*4:i*4+4] 
           [y]=struct.unpack('>f',four_byte)   
           self.received_data.append(y)
          
   def do_retransmission(self,sim,LabviewAddress):
       self.retransmission=0
      
       status_count=0
       self.data_byte=bytearray()
       print('Begin to try to retransmission the same packet')
       reset_msg=bytearray(np.single(1))+bytearray(np.single(3))
       reset_msg.reverse()
       self.u.sendto(reset_msg,LabviewAddress)
       clean_reset_msg=bytearray(np.single(0))+bytearray(np.single(3))
       clean_reset_msg.reverse()
       self.u.sendto(clean_reset_msg,LabviewAddress) 
       for i in range(5):
           self.received_data=[]
           print(i)
           self.do_UDP_write_data(sim,LabviewAddress)
           while True:
                byte=self.server.recv(4096)
                if len(byte)!=0:  
                    four_byte=byte[0:4] 
                    [y]=struct.unpack('>f',four_byte)
                    if y==6: #check if data package
                        status_count=status_count+1
                        if status_count>4:
                            status_count=0
                            break
                    else:
                        status_count=0
                        self.data_byte=self.data_byte+byte 
           for j in range(np.int(len(self.data_byte)/4)):
               four_byte=self.data_byte[j*4:j*4+4] 
               [y]=struct.unpack('>f',four_byte)   
               self.received_data.append(y)             
           self.received_data=np.array(self.received_data)
           self.received_data=self.received_data.reshape(-1,1)    
           if len(self.received_data)==len(self.send_data):
               diff=self.received_data-self.send_data
               err_number=np.count_nonzero(diff)
               print('The error number is',err_number)
               err_percent=err_number/len(diff)
               print('The error percent is',err_percent)
               if err_number==0:
                   print('This time the transmission was successful')
                   break
           else:
               if i==4:
                   self.retransmission=1
                   print('Retransmission failed,please rerun Python')
    
   def do_evaluate(self,sim,LabviewAddress):
       self.received_data=np.array(self.received_data)
       self.received_data=self.received_data.reshape(-1,1)
       if len(self.received_data)==len(self.send_data):
           diff=self.received_data-self.send_data
           err_number=np.count_nonzero(diff)
           print('The error number is',err_number)
           err_percent=err_number/len(diff)
           print('The error percent is',err_percent)
           if err_number==0:
               print('This time the transmission was successful')
           else:
               print('This time the transmission failed')    
               print('Reason: All data is received, but elements are not correct')
               self.do_retransmission(sim,LabviewAddress)
       else:
           print('This time the transfer failed')
           print('Reason: not all data is received')
           self.do_retransmission(sim,LabviewAddress)                
    
   def do_close_UDP(self):
       self.u.close()                  