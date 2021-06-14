classdef UDP_func
    properties
        %UDP properties
        IP                               %Local computer IP
        write_port
        read_port
        u   
        send_data
        received_data
        count
        retransmission
    end
    methods
        %% initialization
        function obj=UDP_func(UDP_Obj)        
            %UDP_properties
            obj.IP=UDP_Obj.IP;
            obj.write_port=UDP_Obj.write_port;
            obj.read_port=UDP_Obj.read_port;
            obj.count=0;
            obj.retransmission=0;
        end
        %%functions
        function obj = do_open_UDP(obj) 
            obj.u=udp('127.0.0.1','RemotePort',obj.write_port,'LocalPort',obj.read_port);
            obj.u.OutputBufferSize=50000;
           
            fopen(obj.u); 
             fwrite(obj.u,[3,0],'single');
        end
        
        function obj = set_TX_parameters(obj,TX_Frequency,TX_Sample_Rate,sim_parameters) 
            switch(sim_parameters.encoder)
                case 'PC_convolutional'
                    sim_parameters.encoder='0';
                case 'convolutional'
                    sim_parameters.encoder='1';
                otherwise
                    sim_parameters.encoder='2';
            end
            switch(sim_parameters.waveform.name)
                case 'SWH' 
                    sim_parameters.waveform.name='0';
                case 'OTFS'
                    sim_parameters.waveform.name='1';
                case 'OCDM'
                    sim_parameters.waveform.name='2';
                otherwise
                    sim_parameters.waveform.name='3';
            end
    
            TX_command_content=[];
            TX_command_content(1)=TX_Frequency;
            TX_command_content(2)=TX_Sample_Rate;
            TX_command_content(3)=sim_parameters.J;
            TX_command_content(4)=sim_parameters.R;
            TX_command_content(5)=str2double(sim_parameters.encoder);
            TX_command_content(6)=sim_parameters.K;
            TX_command_content(7)=sim_parameters.M;
            TX_command_content(8)=sim_parameters.P;
            TX_command_content(9)=str2double(sim_parameters.waveform.name);
            TX_command_content(10)=sim_parameters.waveform.Q;
            TX_command_content(11)=sim_parameters.waveform.Q2;
            TX_command_content(12)=size(sim_parameters.punc,2);
            TX_command_content(13:13+size(sim_parameters.punc,2)-1)=sim_parameters.punc;
            content_payload_size=size(TX_command_content,2);
            fwrite(obj.u,[0,1,content_payload_size,TX_command_content],'single'); %send header
        end
        function obj = set_RX_parameters(obj,RX_Frequency,RX_Sample_Rate,sim_parameters)
            switch(sim_parameters.equalizer)
                case 'CWCU_MMSE_low_complexity'
                    sim_parameters.equalizer='0';
                case 'CWCU_MMSE_general'
                    sim_parameters.equalizer='1';
                otherwise
                    sim_parameters.equalizer='2';
            end
            RX_command_content=[];
            RX_command_content(1)=RX_Frequency;
            RX_command_content(2)=RX_Sample_Rate;
            RX_command_content(3)=sim_parameters.N_iterations;
            RX_command_content(4)=str2double(sim_parameters.equalizer);
            content_payload_size=size(RX_command_content,2);
            fwrite(obj.u,[1,1,content_payload_size,RX_command_content],'single');
        end
   
        function obj = do_UDP_write_data(obj,sim_parameters)
            obj.send_data=[]; %%clear before each writting
            if(~sim_parameters.data_type) %data_type=0,generate random complex matrix
                matrix= sim_parameters.matrix .';
                for i=1:size(matrix,1)
                    real_part=real(matrix(i,:));
                    imag_part=imag(matrix(i,:));
                    newmatrix=reshape(([real_part;imag_part]),[],1);
                    obj.send_data=[obj.send_data;newmatrix];
                end
            else %data_type=1,generate random bits
                obj.send_data=randi(2,1,sim_parameters.data_size)-1;
            end
            obj.send_data=reshape(obj.send_data,[],1); 
            UDP_data_packet_size=sim_parameters.UDP_data_packet_size;
            divisor=floor(size(obj.send_data,1)/UDP_data_packet_size);
            remainder=mod(size(obj.send_data,1),UDP_data_packet_size);
            if(remainder)
                total_number_data_packets=divisor+1;
            else
                total_number_data_packets=divisor;
            end
            for j=1:divisor
                fwrite(obj.u,[2,total_number_data_packets,UDP_data_packet_size,sim_parameters.data_type,reshape(obj.send_data((j-1)*UDP_data_packet_size+1:j*UDP_data_packet_size),1,[])],'single'); %send data with format 'single' 
            end
            %data_type=0==> random modulated signal (Afer constellation mapper and modulation)
            %data_type=1==> random bits 0 or 1
            fwrite(obj.u,[2,total_number_data_packets,UDP_data_packet_size,sim_parameters.data_type,reshape(obj.send_data(divisor*UDP_data_packet_size+1:divisor*UDP_data_packet_size+remainder,1),1,[])],'single');
        end
        
        function obj = do_UDP_read(obj) %UDP read status and data respectively
            obj.received_data=[]; %clear before each reading
            obj.send_data=reshape(obj.send_data,1,[]);
            data_packet_counter=0;
              while (true)
                new_received_data=swapbytes(typecast(uint8(fread(obj.u)),'single'));
                if(size(new_received_data,1)~=0)
                    %check if status or data
                    if(new_received_data(1)==6)
                        obj.count=obj.count+1;
                        disp('Waiting for new packets...');
                        if(obj.count>4)
                            disp('Time out!!');
                            disp('No new packets come in, data transmission is complete.');
                            disp(['Status ID:' num2str(new_received_data(1))]);
                            disp(['Current data packet size:' num2str(new_received_data(2))]);
                            disp(['The average throughput is:' num2str(new_received_data(3)) ' MB/s']);
                            break
                        else
                            disp(['The average throughput is:' num2str(new_received_data(3)) ' MB/s']);
                        end
                    else  %data packet
                        obj.count=0;   
                        data_packet_counter=data_packet_counter+1;
                        obj.received_data=[obj.received_data,reshape(new_received_data,1,[])];
                        disp(['New data packet received: this is ' num2str(data_packet_counter) 'th data packet']);
                        
                    end
                end
              end     
              
               
        end
        function obj=do_evaluate(obj,sim_parameters)
               obj.received_data=single(reshape(obj.received_data,1,[]));
               obj.send_data=single(reshape(obj.send_data,1,[]));
               if(size(obj.received_data,2)==size(obj.send_data,2)) 
                    err_number=length(find((obj.received_data-obj.send_data)~=0));
                    err_percent=err_number/size(obj.received_data,2);
                    disp(['The error percent is ', num2str(err_percent*100), '%']);
                    disp(['The err_number is :' num2str(err_number)]);
                    if(err_percent==0)
                         disp('This time the transmission was successful');
                    else
                          disp('This time the transmission failed');
                          disp('Reason: All data is received, but elements are not correct');
                          obj = do_retransmission(obj);
                    end
               else
                    disp('This time the transfer failed');
                    disp('Reason: not all data is received');
                    obj = do_retransmission(obj,sim_parameters);                
                end
              
        end
        function obj = do_retransmission(obj,sim_parameters)
            fwrite(obj.u,[3,1],'single');
            fwrite(obj.u,[3,0],'single');
            obj.send_data=single(reshape(obj.send_data,1,[]));
            
            obj.count=0;
            disp('Begin to try to retransmission the same packet');
                    for i=1:5 
                            disp(i);
                            obj = do_UDP_write_data(obj,sim_parameters);
                            while (true)
                                new_received_data=swapbytes(typecast(uint8(fread(obj.u)),'single'));
                                if(size(new_received_data,1)~=0)
                                    %check if status or data
                                    if(new_received_data(1)~=6)
                                        obj.count=0;
                                        obj.received_data=[obj.received_data,reshape(new_received_data,1,[])];
                                    else
                                        obj.count=obj.count+1;
                                        if(obj.count>4)
                                            obj.count=0;
                                            break
                                        end
                                    end
                                end
                            end
                        if(size(obj.received_data,2)==size(obj.send_data,2)) 
                            err_number=length(find((obj.received_data-obj.send_data)~=0));
                            err_percent=err_number/size(obj.received_data,2);
                            disp(['The error percent is ', num2str(err_percent*100), '%']);
                            disp(['The err_number is :' num2str(err_number)]);
                            if(err_percent==0)
                                disp('This time the transfer was successful');
                                break;
                            end
                        end
                        if(i==5)
                            obj.retransmission=1;
                            disp('Retransmission failed,please rerun Matlab');
                        end
                    end
             
                 
        end
        
        function obj = do_UDP_close(obj)
            fclose(obj.u);  %close UDP connection
            delete(obj.u);  %delete UDP connection
        end
    end
end

