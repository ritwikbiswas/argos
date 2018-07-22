#!/usr/bin/env Rscript
# args <- commandArgs(trailingOnly=TRUE)

# Clean runtime env.
rm(list = ls())

args <- commandArgs(trailingOnly=T);
argsLen <- length(args);
# print(argsLen)

# include the needed libraries
library(rgl)
library(Rcmdr)
library(plotrix)
#"/Users/ritwikbiswas/argos-demo/vision-dump/Vision_4_2018-05-27-10-18-22.csv"
# read data file and assign vectors

# print(commandArgs(TRUE)[1])
#"/Users/ritwikbiswas/argos-demo/vision-dump/Vision_4_2018-05-27-10-18-22.csv"
feq <- read.csv(file=args[1], header=TRUE)
# head(feq)
# dim(feq)

# Extract the needed vectors
elapsed_time <- feq$elapsed_time
av_feq <- feq$avg_FEQ
# plot(elapsed_time,av_feq)
n_rows = length(av_feq)


# CUSTOMIZE threshold inputs

# Define the duration of a session segment (in min)
start_time <- 0
end_time <- 1

# Define time window for computation in seconds
time_window <- 1

# Define FEQ level thresholds (low, moderate, intense)
moderate_FEQ_cutoff <- 0.2
intense_FEQ_cutoff <- 0.5

# Define time duration thresholds (beginning, middle, end)
time_middle_cutoff <- 0.2
time_end_cutoff <- 0.8


# Check for valid session segment spec
total_duration_in_minutes <- (tail(elapsed_time,n=1)/60.0)
if (start_time >= total_duration_in_minutes || end_time >= total_duration_in_minutes){
  stop("Incorrect session segment duration")
  return(1)
}

# SECTION: Compute average of the time windows for the **entire session**
# initialize null vectors
windowed_elapsed_time <- vector() 
windowed_average_feq <- vector() 
temp_vector <- vector() 

old_window_time <- floor(elapsed_time[1]/time_window) * time_window
for (i in 1:n_rows) {
  e_time <- elapsed_time[i]
  v_feq <- av_feq[i]
  
  if ((i == 1) && (e_time > time_window)){
    # the csv file started at a large time value
    # create aporioriate number of zeroed entries
    for (j in 1:floor(e_time/time_window)){
      windowed_elapsed_time <- append(windowed_elapsed_time,((j-1)*time_window))
      windowed_average_feq <- append(windowed_average_feq,0)
    }
    old_window_time <- j*time_window
  } 
  # do usual stuff
  new_window_time <- floor(e_time/time_window) * time_window
  
  if (new_window_time > old_window_time){
    
    windowed_elapsed_time <- append(windowed_elapsed_time,old_window_time)
    if(is.na(mean(temp_vector)) || is.nan(mean(temp_vector))){
      windowed_average_feq <- append(windowed_average_feq,0)
    }else{
      windowed_average_feq <- append(windowed_average_feq,mean(temp_vector))
    }
    # emplty the temp_vector
    temp_vector <- vector() 
    old_window_time <- old_window_time + time_window
    
    temp_vector <- rbind(temp_vector,v_feq)
  }else{
    temp_vector <- rbind(temp_vector,v_feq)
  }
}
windowed_elapsed_time <- append(windowed_elapsed_time,new_window_time)
if(is.na(mean(temp_vector)) || is.nan(mean(temp_vector))){
  windowed_average_feq <- append(windowed_average_feq,0)
}else{
  windowed_average_feq <- append(windowed_average_feq,mean(temp_vector))
}





# SECTION: Compute the FEQ range counts for the **entire session**
low_cnt <- 0
moderate_cnt <- 0
intense_cnt <- 0

for (i in 1:length(windowed_average_feq)){
  
  # Check for Na and NaNs and replace them by zeros
  if (is.na(windowed_average_feq[i]) || is.nan(windowed_average_feq[i])){
    windowed_average_feq[i] <- 0
    next
  }
  
  if (windowed_average_feq[i] < moderate_FEQ_cutoff){
    low_cnt <- low_cnt + 1
  }else{
    if (windowed_average_feq[i] < intense_FEQ_cutoff){
      moderate_cnt <- moderate_cnt + 1
    }else{
      intense_cnt <- intense_cnt + 1
    }
  }
}
total_low_cnt <- low_cnt
total_moderate_cnt <- moderate_cnt
total_intense_cnt <- intense_cnt








# SECTION: Compute the av. FEQ in different parts of the **entire session**  
session_middle_cutoff <- floor(time_middle_cutoff * length(windowed_average_feq))
session_end_cutoff <- floor(time_end_cutoff * length(windowed_average_feq))

beg_vector <- vector() 
middle_vector <- vector()
end_vector <- vector()

for (i in 1:length(windowed_average_feq)){
  
  # Check for Na and NaNs and replace them by zeros
  if (is.na(windowed_average_feq[i]) || is.nan(windowed_average_feq[i])){
    windowed_average_feq[i] <- 0
    next
  }
  
  if (i < session_middle_cutoff){
    beg_vector <- rbind(beg_vector,windowed_average_feq[i])
  }else{
    if (i < session_end_cutoff){
      middle_vector <- rbind(middle_vector,windowed_average_feq[i])
    }else{
      end_vector <- rbind(end_vector,windowed_average_feq[i])
    }
  }
}

total_beg_av_feq <- mean(beg_vector)
total_middle_av_feq <- mean(middle_vector)
total_end_av_feq <- mean(end_vector)

total_beg_av_feq
total_middle_av_feq
total_end_av_feq





# SECTION: Compute the FEQ range counts for the **session segment**

start_index <- start_time * 60 / time_window
end_index <- end_time * 60 / time_window

# length(windowed_average_feq[start_index:end_index])

low_cnt <- 0
moderate_cnt <- 0
intense_cnt <- 0

for (i in 1:length(windowed_average_feq[start_index:end_index])){
  
  # Check for Na and NaNs and replace them by zeros
  if (is.na(windowed_average_feq[start_index+i]) || is.nan(windowed_average_feq[start_index+i])){
    windowed_average_feq[start_index+i] <- 0
    next
  }
  if (windowed_average_feq[start_index+i] < moderate_FEQ_cutoff){
    low_cnt <- low_cnt + 1
  }else{
    if (windowed_average_feq[start_index+i] < intense_FEQ_cutoff){
      moderate_cnt <- moderate_cnt + 1
    }else{
      intense_cnt <- intense_cnt + 1
    }
  }
}
range_low_cnt <- low_cnt
range_moderate_cnt <- moderate_cnt
range_intense_cnt <- intense_cnt


# Foorama
length(windowed_average_feq)




# SECTION: Compute the av. FEQ in different parts of the **session segment**  
session_middle_cutoff <- floor(time_middle_cutoff * length(windowed_average_feq[start_index:end_index]))
session_end_cutoff <- floor(time_end_cutoff * length(windowed_average_feq[start_index:end_index]))

# length(windowed_average_feq[start_index:end_index])
# session_middle_cutoff
# session_end_cutoff

beg_vector <- vector() 
middle_vector <- vector()
end_vector <- vector()

for (i in 1:length(windowed_average_feq[start_index:end_index])){
  
  # Check for Na and NaNs and replace them by zeros
  if (is.na(windowed_average_feq[start_index+i]) || is.nan(windowed_average_feq[start_index+i])){
    windowed_average_feq[start_index+i] <- 0
    next
  }
  
  if (i < session_middle_cutoff){
    beg_vector <- rbind(beg_vector,windowed_average_feq[start_index+i])
  }else{
    if (i < session_end_cutoff){
      middle_vector <- rbind(middle_vector,windowed_average_feq[start_index+i])
    }else{
      end_vector <- rbind(end_vector,windowed_average_feq[start_index+i])
    }
  }
}

session_beg_av_feq <- mean(beg_vector)
session_middle_av_feq <- mean(middle_vector)
session_end_av_feq <- mean(end_vector)

session_beg_av_feq 
session_middle_av_feq 
session_end_av_feq 










# SECTION: Plots and reports for the *entire session*
# set the plot environment
pdf("FEQ_plot.pdf")
# plot.new()        # new plot frame
# frame()           # clear the frame
par(mfrow=c(1,1)) # create plot area of three rows and two columns 
plot(elapsed_time/60, 
      av_feq, 
     main="Raw Friendliness", xlab="Elapsed time (Min)", ylab="Friendly Appearance", col="dark green", "p", lwd = 4, pch=16, cex=.5)

# plot.new()        # new plot frame
# frame()           # clear the frame

par(mfrow=c(2,2)) # create plot area of three rows and two columns 


# Plot the average values on an window by window basis

plot((windowed_elapsed_time)/60, 
     windowed_average_feq, 
     main="Friendliness", xlab="Elapsed time (Min)", ylab="Friendly Appearance", col="dark green", "h", lwd = 1, pch=16, cex=.5)


# Plot distribution of FEQ 
# hist(windowed_average_feq[start_index:end_index], main="Distrubution", xlab="FEQ", xlim=c(0.1,1), freq=TRUE, breaks=10, col="brown")
hist(windowed_average_feq, main="Distrubution", xlab="Friendly Appearance", freq=TRUE, breaks=50, col="brown")

# Plot the FEQ ranges as a Pie-chart 
slices <- c(total_low_cnt * time_window / 60, total_moderate_cnt * time_window / 60, total_intense_cnt * time_window / 60) 
lbls <- c("Low", "Moderate", "High")
pct <- round(slices/sum(slices)*100)
lbls <- paste(lbls, pct) # add percents to labels 
lbls <- paste(lbls,"%",sep="") # ad % to labels 
pie(slices,labels = lbls, col=rainbow(length(lbls)),
    main="Full Session Split")

# Show the av. FEQ values in the beg., middle, and end 
my_vector=c(total_beg_av_feq,total_middle_av_feq,total_end_av_feq)
names(my_vector)=c("Beginning","Middle","End")
barplot(my_vector, width = 0.5, col="magenta", ylab="Friendly Appearance Av.", main="In Different Segments")




# Plot stats for **session segment**
# set the plot environment
# plot.new()        # new plot frame
# frame()           # clear the frame
par(mfrow=c(2,2)) # create plot area of three rows and two columns 

# Plot the average values on an window by window basis
plot((windowed_elapsed_time[start_index:end_index])/60, 
     windowed_average_feq[start_index:end_index], 
     main="Friendliness", xlab="Elapsed time (Min)", ylab="Friendly Appeaerance", col="red", "h", lwd = 1, pch=16, cex=.5)

# Plot distribution of FEQ 
# hist(windowed_average_feq[start_index:end_index], main="Distrubution", xlab="FEQ", xlim=c(0.1,1), freq=TRUE, breaks=10, col="brown")
hist(windowed_average_feq[start_index:end_index], main="Distrubution", xlab="Friendly Appearance", freq=TRUE, breaks=50, col="blue")

# Plot the FEQ ranges as a Pie-chart 
slices <- c(range_low_cnt * time_window / 60, range_moderate_cnt * time_window / 60, range_intense_cnt * time_window / 60) 
lbls <- c("Low", "Moderate", "High")
pct <- round(slices/sum(slices)*100)
lbls <- paste(lbls, pct) # add percents to labels 
lbls <- paste(lbls,"%",sep="") # ad % to labels 
pie(slices,labels = lbls, col=rainbow(length(lbls)),
    main="Session Segment Split")

# Plot the average values on an window by window basis
my_vector=c(session_beg_av_feq,session_middle_av_feq,session_end_av_feq)
names(my_vector)=c("Beginning","Middle","End")
barplot(my_vector, width = 0.5, col="dark green", ylab="Friendly Appearance Av.", main="In Different Segments")

dev.off()





# SECTION: Trying with tables

# # Format tables with the collected stats
# low_row <- c("Neutral", total_low_cnt * time_window / 60, range_low_cnt * time_window / 60)
# moderate_row <- c("Moderate", total_moderate_cnt * time_window / 60, range_moderate_cnt * time_window / 60)
# intense_row <- c("Friendly", total_intense_cnt * time_window / 60, range_intense_cnt * time_window / 60)
# 
# low_row
# moderate_row
# intense_row
# 
# table_1 <- rbind(low_row, moderate_row, intense_row)
# #table_1 <- table_1[,-1]
# table_1
# colnames(table_1) <- c("","Full Session","Session Segment")
# table_1
# 
