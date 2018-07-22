# Clean runtime env.
rm(list = ls())

# include the needed libraries
library(rgl)
library(Rcmdr)
library(plotrix)
library("scatterplot3d")

#Args
args <- commandArgs(trailingOnly=T);
argsLen <- length(args);

# Define functions 
check_Na_NaN <- function(x){
  if(all(is.na(x)) || all(is.nan(x))){
    stop("Stopping ...")
    return(1)
  }
}

# Define the output PDF
pdf("Merged_VEQ_FEQ.pdf")

for (index in 0:8){
  high_pass_th <- index/10

# read data file and assign vectors
# vision <- read.csv(file="Kaneya_Vision.csv", header=TRUE)
# voice <- read.csv(file="Kaneya_Voice.csv", header=TRUE)

vision <- read.csv(file=args[1], header=TRUE)
voice <- read.csv(file=args[2], header=TRUE)

# Extract the needed vectors from the vision file
vision_t_stamp <- vision$time_stamp
check_Na_NaN(vision_t_stamp)

vision_elapsed_time <- vision$elapsed_time
check_Na_NaN(vision_elapsed_time)

av_feq <- vision$avg_FEQ
check_Na_NaN(av_feq)

# Extract the needed/essential vectors from the voice file
voice_t_stamp <- voice$time_stamp
check_Na_NaN(voice_t_stamp)

voice_elapsed_time <- voice$elapsed_time
check_Na_NaN(voice_elapsed_time)

# Convert string time to time objects that can be used for time arithmatic 
vision_t_stamp <- strptime(vision_t_stamp, format = "%Y-%m-%d-%H:%M:%S")
voice_t_stamp <- strptime(voice_t_stamp, format = "%Y-%m-%d-%H-%M-%S")

n_vision_rows <- length(vision_t_stamp)
n_voice_rows <- length(voice_t_stamp)

# Take consecutive voice entries as a window and find all vision entries within that window
# Compute vision feq average over that window and store in vector: new_av_feq
voice_start_ptr = 1
voice_end_ptr = 2

temp_vector <- vector() 
new_av_feq <- vector() 

# Loop through all vision timestamps
for (i in 1:n_vision_rows){
  # voice_start_ptr
  # voice_end_ptr

  # vision data is inside the current voice window
  if (vision_t_stamp[i] > voice_t_stamp[voice_start_ptr] &&
      vision_t_stamp[i] <= voice_t_stamp[voice_end_ptr]){
    #print(vision_t_stamp[i])
    #add point to vector for later averaging
    if(is.na(av_feq[i]) || is.nan(av_feq[i])){
      temp_vector <- c(temp_vector, 0)
    }else{
      if (av_feq[i] >= high_pass_th){   #--------------------------------
        temp_vector <- c(temp_vector, av_feq[i])
      }                                 #--------------------------------
      # temp_vector <- c(temp_vector, av_feq[i])
    }
  } else{ # vision data is either before or after the voice window
    
    # vision data is after the window
    if (vision_t_stamp[i] > voice_t_stamp[voice_end_ptr]){
     
      #adding average for current window to final output vector 
      if (is.na(mean(temp_vector)) || is.nan(mean(temp_vector))){
        new_av_feq <- c(new_av_feq,0)
      }else{
        # new_av_feq <- c(new_av_feq,mean(temp_vector))
        new_av_feq <- c(new_av_feq,length(temp_vector) * mean(temp_vector) / 300)  #----------------
      }
      
      # Flush temp_vector and add new FEQ point
      temp_vector <- vector() 
      if(is.na(av_feq[i]) || is.nan(av_feq[i])){
        temp_vector <- c(temp_vector, 0)
      }else{
        if (av_feq[i] >= high_pass_th){  #--------------------------------
          temp_vector <- c(temp_vector, av_feq[i])
        }                               #--------------------------------
        # temp_vector <- c(temp_vector, av_feq[i])
      }
      
      # Update window bounds
      voice_start_ptr <- voice_end_ptr
      voice_end_ptr <- voice_end_ptr +1
      
      # Is the voice data vector exhausted? (Is last window reached) If yes, terminate.
      if (voice_start_ptr == n_voice_rows){
        break
      }
    }
  }
}

# adding average for the current window  
if (is.na(mean(temp_vector)) || is.nan(mean(temp_vector))){
  new_av_feq <- c(new_av_feq,0)
}else{
  # new_av_feq <- c(new_av_feq,mean(temp_vector))
  new_av_feq <- c(new_av_feq,length(temp_vector) * mean(temp_vector)/ 300)  #----------------new_av_feq <- c(new_av_feq,mean(temp_vector))
}

# Add pading if the vision data runs out before the voice windows are over
difff <- length(voice_t_stamp)-length(new_av_feq)
if (difff > 0){
  for (i in 1:difff){
    new_av_feq <- c(new_av_feq,0)
  }
}

# check_Na_NaN(new_av_feq)
# length(new_av_feq)
# dim(voice)
# new_av_feq

# Merge new_av_feq vector to the voice data frame without the last row
new_av_feq <- new_av_feq[-(length(new_av_feq))]
voice <- voice[1:nrow(voice)-1,]

length(new_av_feq)
dim(voice)
joint <- cbind(voice,new_av_feq)

# save the merged frame in a new .csv file

write.csv(joint,'Audio_video_Merged.csv')

# Now plot the needed stuff
elapsed_time <- joint$elapsed_time
check_Na_NaN(elapsed_time)

new_av_feq <- joint$new_av_feq
check_Na_NaN(new_av_feq)

word_count <- voice$word_count
check_Na_NaN(word_count)

s_composite <- joint$composite
check_Na_NaN(s_composite)

s_vader <- joint$vader_sentiment
check_Na_NaN(s_vader)

s_ibm <- joint$ibm_sentiment
check_Na_NaN(s_ibm)

s_blob <- joint$blob_sentiment
check_Na_NaN(s_blob)

s_binary <- joint$binary_composite
check_Na_NaN(s_binary)

# Vokaturi stuff

v_neutral <- voice$v_neutral
check_Na_NaN(v_neutral)

v_sad <- voice$v_sad
check_Na_NaN(v_sad)
        
par(mfrow=c(2,2)) 

plot(elapsed_time/60, 
     new_av_feq, 
     main="Friendliness", 
     xlab="Elapsed time (Min)", 
     ylab="Friendly Appearance", 
     col="dark green", 
     "h", lwd = 5, pch=16, cex=.5)

plot(elapsed_time/60, 
     word_count * 2, 
     main="Words Spoken", 
     xlab="Elapsed time (Min)", 
     ylab="No. of Words Per Min.", 
     col="blue", 
     "h", lwd = 5, pch=16, cex=.5)

plot(elapsed_time/60, 
     s_composite, 
     main="Speech Sentiment", 
     xlab="Elapsed time (Min)", 
     ylab="Speech Sentimnt Level", 
     col="Brown", 
     "h", lwd = 5, pch=16, cex=.5)

plot(elapsed_time/60, 
     s_binary, 
     main="Sentiment Direction", 
     xlab="Elapsed time (Min)", 
     ylab="Sign of Sentiment", 
     col="Black", 
     "h", lwd = 5, pch=16, cex=.5)

par(mfrow=c(2,1)) 
plot(elapsed_time/60, 
     v_sad, 
     main="Sadness in Voice", 
     xlab="Elapsed time (Min)", 
     ylab="Voice Sadnedd Index", 
     col="purple", 
     "h", lwd = 5, pch=16, cex=.5)

plot(elapsed_time/60, 
     v_neutral, 
     main="Voice Neutrality", 
     xlab="Elapsed time (Min)", 
     ylab="Voice Neutrality Index", 
     col="Red", 
     "h", lwd = 5, pch=16, cex=.5)

v_happy_hat <- v_neutral
par(mfrow=c(1,1)) 
pairs(~new_av_feq+
        word_count+
        s_composite+
        v_happy_hat,
      main="Correlations", col = "blue", pch=10)
}

dev.off()