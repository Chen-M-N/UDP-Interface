clc;
clear;
UDP.IP='127.0.0.1';
UDP.write_port=8847;
UDP.read_port=8848;
TX_Frequency=2320; %Hz
TX_Sample_Rate=3;
RX_Frequency=2000;
RX_Sample_Rate=2;
sim_parameters.K =64;
sim_parameters.M =4;   
sim_parameters.J = 4;
sim_parameters.waveform.name = 'SWH'; 
sim_parameters.N_iterations = 4;
sim_parameters.waveform.Q = 16;
sim_parameters.waveform.Q2 = 4;
sim_parameters.R = 1/2; 
sim_parameters.punc = [1 1 0 1 1 0];
sim_parameters.encoder = 'PC_convolutional';
SNR = 7; 
sim_parameters.P = 10^(SNR/10);
sim_parameters.data_type=1;  %0: random modulated signal, 1:random bits 0 or 1
sim_parameters.data_size=299; %Number of bits
sim_parameters.equalizer = 'CWCU_MMSE_low_complexity';
sim_parameters.UDP_data_packet_size=60;

%step 1: initalization UDP 
obj = UDP_func(UDP);
%step 2: open UDP
obj = do_open_UDP(obj);
%step 3: set TX parameters and waveform parameters
obj = set_TX_parameters(obj,TX_Frequency,TX_Sample_Rate,sim_parameters);
%step 4: set RX parameters
obj = set_RX_parameters(obj,RX_Frequency,RX_Sample_Rate,sim_parameters);
%data_type=0==> random modulated signal
%data_type=1==> random bits 
Nevents=200;
for j=1:Nevents
disp(['Test process : ',num2str((j/Nevents)*100),'%']);
disp(['This is the ', num2str(j), 'th iteration']);   
%% Data generation
% sim_parameters.matrix = rand(sim_parameters.K,sim_parameters.M)+1i*rand(sim_parameters.K,sim_parameters.M);
sim_parameters.random_bit=randi(2,1,sim_parameters.data_size)-1;
%%
obj = do_UDP_write_data(obj,sim_parameters);
obj = do_UDP_read(obj);
obj = do_evaluate(obj,sim_parameters);
if(obj.retransmission==1)
    break
end
disp('-------------------------------------------');
disp(' ');
disp(' ');
disp('' );
end
obj = do_UDP_close(obj);



















