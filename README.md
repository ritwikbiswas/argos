# Argos

![](https://i.imgur.com/p1LNKEj.png)

## Components Overview
### 1. [Google Vision Kit](https://github.com/ritwikbiswas/argos/wiki/Architecture#vision-kit)
### 2. [Client for Data Collection](https://github.com/ritwikbiswas/argos/wiki/Architecture#client-end)
### 3. [AWS EC2 Instance for training models](https://github.com/ritwikbiswas/argos/wiki/Architecture#aws-instance)

## General Architecture
The Vision Kit collects raw facial data from a subject and send the data to the client machine via an SSH connection. The client machine then processes the data, generating time series and correlated plot data to be viewed by the user. For custom trained model, the client machine collects google image data pertaining to each class and sends the images to an AWS EC2 Instance. These images are used to retrain the last layer of a Convolutional Neural Network (MobileNet) to create the model. The model is then frozen and compiled for the Vision Kit hardware and sent to the Vision Kit to be used for facial data capture.

## Vision Kit
### Hardware Details 
The primary hardware used for data collection is Google's [AIY Vision Kit](https://aiyprojects.withgoogle.com/vision/). This consists of:
* [Raspberry Pi Zero](https://www.raspberrypi.org/products/raspberry-pi-zero/)
* Raspberry Pi Camera v2
* Vision Bonnet

The Vision Bonnet is an image processing accelerator with a [Movidius VP2 Chip](https://www.movidius.com/myriad2). It allows tensorflow model to run natively on the hardware as opposed to via an API as is commonly done for IoT devices

### Joy Detection Code 
For detecting the subject emotion, the Raspberry Pi's camera image is run through a [face detection model](https://github.com/google/aiyprojects-raspbian/blob/aiyprojects/src/aiy/vision/models/face_detection.py). This model generates a bounding box on a detected face and generates a joy score between 0 and 1 (ranging from frown-0 to smile-1). This model was pretrained, compiled, and loaded with the vision kit.
### Custom Models
So far the system supports two custom models for detection gender and demographic based on the camera image. These models were custom trained on the EC2 instance and loaded onto the pi for usage. The process is described in much more detailed in [the EC2 section below](https://github.com/ritwikbiswas/argos/wiki/Architecture#aws-instance).
### Consolidated scripts
The machine learning models are combined and attached to a Camera Interface in a consolidated script. This script writes the data real time to CSV file with a latency of 100ms and SCP transfers the data to the client to be processed and viewed.

## Client End
### Data collection workflow
The client codebase consists of multiple Python and R scripts designed for various functions ranging from controlling the Vision Kit remotely to processing the data after a collection cycle. The client automatically generates reports of the Facial Emotional data for a given data collection cycle. Some example reports look like:
![](https://i.imgur.com/J9BuCJk.png)

## AWS Instance
Custom models were trained and compiled on an AWS [Elastic Cloud Compute (EC2)](https://aws.amazon.com/ec2/) instance. Tensorflow requires training to be done on a linux machine. 
### EC2 Instance Details
The EC2 instance used was a `t2.micro` which has **1 vCPU** and **1 GB** of ram. ECS T2 instances supports high CPU [Burstable Performance](https://aws.amazon.com/ec2/instance-types/#burst) which supports the necessary workload required for training custom models.
### Transfer Learning  
For the purposes of the models used on the vision kit we used transfer learning on the popular [MobileNetV2](https://ai.googleblog.com/2017/06/mobilenets-open-source-models-for.html) to retrain the bottleneck layer for the specific classification of each model.
#### Mobile Net
MobileNet is a Convulational Neural Network Model designed by Google designed for running on mobile devices or embedded applications. The network is low powered, low latency to meet resource constraints of devices like the Vision Kit. The basic network has 30 layers and for more information you can read about it [here](https://ai.googleblog.com/2017/06/mobilenets-open-source-models-for.html).
![MobileNet Architecture](https://i.imgur.com/NW4zQUZ.png)
#### Retraining the Bottleneck Layer
The concept of transfer learning is to modify the penultimate layer of MobileNet to classify the intended images. The previous layers of the network distinguish between macro level features that allow image classification in general. 

For example, the retrained model uses _~600 male faces_ and _~600 female faces_ pictures from Google Images. The hyperparameters are tuned for **4000 training steps** with a **learning rate of 0.01**. The input image size of the camera interface is set to 224 by 224 pixels and for the node depth, this model only uses half of the full MobileNet network. The retraining script call looks like :


    IMAGE_SIZE=224
    ARCHITECTURE="mobilenet_0.50_${IMAGE_SIZE}"

    python -m scripts.retrain \
        --bottleneck_dir=tf_files/bottlenecks \
        --how_many_training_steps=4000 \
        --learning_rate=0.1  \
        --model_dir=tf_files/models/ \
        --summaries_dir=tf_files/training_summaries/"${ARCHITECTURE}" \
        --output_graph=tf_files/retrained_graph_gender_2.pb \
        --output_labels=tf_files/retrained_labels_gender_2.txt \
        --architecture="${ARCHITECTURE}" \
        --image_dir=tf_files/gender_pics

This model only yield an accuracy of **84.4%** on the validation set, but further tuning the hyperparameters may increase the performance.

#### Compiling the Model
Finally, before the script can be run from the Vision Bonnet, it must be compiled into a `binaryproto` format by a bonnet model compiler. This compiled version of the model can run on natively on the Vision Bonnet chip for real time classification based on real-time camera input. For example, the call for the compilation of the gender classifier looks like:

    ./bonnet_model_compiler.par \
        --frozen_graph_path=retrained_graph_gender.pb \
        --output_graph_path=retrained_graph_gender_new.binaryproto \
        --input_tensor_name=input \
        --output_tensor_names=final_result \
        --input_tensor_size=${IMAGE_SIZE}

The newly compiled binaryproto model can be loaded on the Vision Kit via SCP and integrated with a script for data collection.


## Built With

* Google Vision Kit to capture facial data
* Python and R used in the client end to process data 
* Tensorflow used for training custom models (Gender and Demographic detection)
* Amazon Web Services to train and create tensorflow models to run on the Vision Kit

## Authors

* **Ritwik** 

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
