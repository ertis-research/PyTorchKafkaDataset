# PyTorch Kafka Dataset: A definition of a dataset to get data for training from Kafka.

## Usage
To use this library, you just have to create a TrainingKafkaDataset with a ControlMessage, boostrapServers, and a group_id.
Once the object has been created and the data has been obtained from Kafka, the object is usable as a normal PyTorch Dataset, being for example, iterable with a DataLoader.

ControlMessage is a dictionary, which principal keys are `topic` and `input_config`.

In `topic`, you have to proportionate a comma-separated string with the different topic, partition, start and end offset (those values separated with double dots, like in Kafka). 
In `input_config`, you have to indicate the reshapes of the data fetched from Kafka, this is because Kafka works in bytes, and its needed to decode back the inputs of our model.

`boostrap_servers` and `group_id` are common parameters used in KafkaConsumers. This parameters are given directly to the KafkaConsumers inside the object.

Here you have an example of craeting a TrainingKafkaDataset:

```python
kafkaControl = {'topic': 'pytorch_mnist_test:0:0:20000,pytorch:0:20000:50000,pytorch_mnist_test:0:120000:140000',
                'input_config': {'data_type': 'uint8', 
                                 'label_type': 'uint8', 
                                 'data_reshape': '28 28', 
                                 'label_reshape': ''}, 
                }
boo_svr = ["localhost:9094"]
grp_id = 'sink'
```

## Examples
There is a folder with full example of Data Fetching and training of a model, specifically with MNIST dataset.
