# Classifier 3 - MobileNet
No Hyperparameters Tuned
160 x 160
depth_multiplier = 0.5
~390 Male ~390 Female
262 Variables
87.5% accuracy on Test Set



python retrain.py --image_dir /Users/ritwikbiswas/deep_learning/gender_pics --tfhub_module https://tfhub.dev/google/imagenet/mobilenet_v2_050_160/feature_vector/1  --train_batch_size 200 


python label_image.py \
--graph=/Users/ritwikbiswas/deep_learning/transfer_learn/testing_set/gender_stuff/gender_1/output_graph.pb \
--labels=/Users/ritwikbiswas/deep_learning/transfer_learn/testing_set/gender_stuff/gender_1/output_labels.txt \
--input_layer=Placeholder \
--output_layer=final_result \
--image=/Users/ritwikbiswas/deep_learning/transfer_learn/testing_pics/subir_1.jpg

#download ethnic faces for training 
 #male
 #female

#turn on distortions (random resize/coloring)
turn on all flags

#play with learning rate
.3 .5 .7

#play with batch size

#look at --print-misclassified_tes_images

#play with training steps