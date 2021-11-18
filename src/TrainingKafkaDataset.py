from kafka import KafkaConsumer, TopicPartition
import numpy as np
from torch.utils.data import Dataset

###################################

class TrainingKafkaDataset(Dataset):
    def __init__(self, controlMessage, bootstrap_servers, group_id, transform=None, label_transform=None):
        self.transform = transform
        self.label_transform = label_transform
        self.data = []
        
        for kafkaControl in self.__splitPartitionsIntoControlMsgs__(controlMessage):
            consumer, end_offset = self.__createconsumer__(kafkaControl, bootstrap_servers, group_id)

            for message in consumer:
                decoded_data = self.__decodedata__(message, controlMessage)
                self.data.append(decoded_data)     
                
                if message.offset >= end_offset-1:
                    consumer.unsubscribe()
                    break
                    

    def __splitPartitionsIntoControlMsgs__(self, controlMsg):
        res = []
        partitions = controlMsg['topic'].split(',')
        for topic in partitions:
            auxControlMSG = controlMsg.copy()
            auxControlMSG['topic'] = topic
            res.append(auxControlMSG)
        
        return res

    def __createconsumer__(self, controlMessage, bootstrap_servers, group_id):
        topic = controlMessage['topic'].split(":")
        consumer = KafkaConsumer(topic[0],
                        bootstrap_servers = bootstrap_servers,
                        enable_auto_commit = False,
                        group_id = group_id,
                        )
        consumer.poll()
        tp, start_offset, end_offset = TopicPartition(topic[0], int(topic[1]) ), int(topic[2]), int(topic[3])
        consumer.seek(tp, start_offset)

        return consumer, end_offset

    def __decodedata__(self, input, controlMessage):
        # if controlMessage["input_format"] == 'RAW':
        
        input_config = controlMessage['input_config']
        # Data decoding
        value = np.copy(np.frombuffer(input.value, dtype=input_config['data_type']))
        if input_config['data_reshape'] != None and input_config['data_reshape'] != '':
            value.shape = np.fromstring(input_config['data_reshape'], dtype=int, sep=' ')

        # Label decoding                                            
        label = np.copy(np.frombuffer(input.key, dtype=input_config['label_type']))

        if len(label) == 1:
            label = label[0]
        elif input_config['label_reshape'] != None and input_config['label_reshape'] != '':
            value.shape = np.fromstring(input_config['data_reshape'], dtype=int, sep=' ')
           
        return (value, label)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        res_tuple = self.data[idx]
        
        res_data, res_label = res_tuple[0], res_tuple[1]
        if self.transform:
            res_data = self.transform(res_tuple[0])
        if self.label_transform:
            res_label = self.label_transform(res_tuple[1])

        return (res_data, res_label)