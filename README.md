# PyTorch Kafka Dataset: A definition of a dataset to get training data from Kafka.

## Objectives
The main objective of this library is to take training data from Kafka to create a PyTorch Dataset. This is useful when we have data distributed in Kafka and we want to train a model with this framework. The structure of data messages in Kafka should be key:value, where key is the label and value the input.

## Usage
To use this library, you just have to create a TrainingKafkaDataset with a ControlMessage, boostrapServers, and a group_id.
Once the object has been created and the data has been obtained from Kafka, the object is usable as a normal PyTorch Dataset, being for example, iterable with a DataLoader.

ControlMessage is a dictionary, which principal keys are `topic` and `input_config`.

In `topic`, you have to proportionate a comma-separated string with the different topic, partition, start and end offset (those values separated with double dots, like in Kafka). 
In `input_config`, you have to indicate the reshapes of the data fetched from Kafka, this is because Kafka works in bytes, and its needed to decode back the inputs of our model.

`boostrap_servers` and `group_id` are common parameters used in KafkaConsumers. This parameters are given directly to the KafkaConsumers inside the object.

Here you have an example of creating a TrainingKafkaDataset:

```python
kafkaControlMessage = {'topic': 'pytorch_mnist_test:0:0:20000,pytorch:0:20000:50000,pytorch_mnist_test:0:120000:140000',
                'input_config': {'data_type': 'uint8', 
                                 'label_type': 'uint8', 
                                 'data_reshape': '28 28', 
                                 'label_reshape': ''}, 
                }
bootstrap_server = ["localhost:9094"]
group_id = 'sink'
df = TrainingKafkaDataset(kafkaControlMessage, bootstrap_server, group_id, ToTensor())
```

## Examples
There is a folder with full example of Data Fetching and training of a model, specifically with MNIST dataset.
