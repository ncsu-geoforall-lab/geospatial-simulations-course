
########## Code to run calibration on a test dataset ############

## To install the most recent version of the PoPS Package 
  ## if you don't have devtools package, install it with install.packages("devtools")
  ## if the pops package needs to install some dependencies, let it install all of them
library(devtools)
devtools::install_github("ncsu-landscape-dynamics/rpops", ref="landscape_pattern")  # If it needs to install any dependencies, just let it do that

## load necessary packages
library(PoPS)
library(raster)

## Set working directory to the folder you downloaded 
setwd("C:/Users/dagaydos/Downloads")

## load files necessary GIS files
infected_file = "calibration_validation_sample_data/initial_infection.tif"
host_file = "calibration_validation_sample_data/host.tif"
total_plants_file = "calibration_validation_sample_data/all_plants.tif"
infected_years_file = "calibration_validation_sample_data/infected_years.tif"
treatments_file = "calibration_validation_sample_data/treatments.tif"
treatment_years = c(2001, 2002, 2003)
management = FALSE


## initalize MCMC process
num_iterations = 1000
start_reproductive_rate = 0.5
start_short_distance_scale = 20
sd_reproductive_rate = 0.2
sd_short_distance_scale = 1


## run the calibration code
   # this will create a dataset called params. When it's done running, open it to see what all is being calculated. 
params <- PoPS::calibrate(infected_years_file, num_interations, start_reproductive_rate, 
                                      start_short_distance_scale, sd_reproductive_rate, sd_short_distance_scale,
                                      infected_file, host_file, total_plants_file, reproductive_rate =.5,
                                      use_lethal_temperature = FALSE, temp = FALSE, precip = FALSE, management = management, mortality_on = FALSE,
                                      temperature_file = "", temperature_coefficient_file = "", 
                                      precipitation_coefficient_file ="", treatments_file = treatments_file,
                                      season_month_start = 1, season_month_end = 12, time_step = "month",
                                      start_time = 2001, end_time = 2004, treatment_years = treatment_years,
                                      dispersal_kern = "cauchy", percent_short_distance_dispersal = 1.0,
                                      short_distance_scale = 20, long_distance_scale = 0.0,
                                      lethal_temperature = 12, lethal_temperature_month = 1,
                                      mortality_rate = 0.05, mortality_time_lag = 2,
                                      wind_dir = "NONE", kappa = NA)



## Function to get the mode of a dataset
getmode <- function(v) {
  uniqv <- unique(v)
  uniqv[which.max(tabulate(match(v, uniqv)))]
}


## Get spore rate parameter in a separate dataframe
sp_rate <- data.frame(table(params$reproductive_rate))
sp_rate <- sp_rate[sp_rate$Freq >0,]

## find the most common spore rate to use as parameter for the model
most_common_sp_rate <- getmode(params$reproductive_rate)
print(paste("Spore Rate: ", most_common_sp_rate))


## Get distance parameter in a separate dataframe
dist <- data.frame(table(params$short_distance_scale))
dist <- dist[dist$Freq >0,]

## find the most common distance to use as a parameter for the model
most_common_dist <- getmode(params$short_distance_scale)
print(paste("Distance: ", most_common_dist))
