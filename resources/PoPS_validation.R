
####### Code to run the PoPS model with parameter set derived and conduct validation on outcomes ######

##load necessary packages
library(PoPS)
library(raster)

## Set working directory to the folder you downloaded
setwd("C:/Users/dagaydos/Downloads/")

## Read in data
infected_file = "calibration_validation_sample_data/initial_infection.tif"
host_file = "calibration_validation_sample_data/host.tif"
total_plants_file = "calibration_validation_sample_data/all_plants.tif"
treatments_file = "calibration_validation_sample_data/treatments.tif"

Run the 
## Put in the parameters you derived from the calibration code
reproductive_rate = .7
short_distance_scale = 20

      ### Initialize conditions for model: ###
## set management conditions
management = FALSE
treatment_years = c(2001, 2002, 2003)

## set mortality conditions
mortality_on = FALSE
mortality_rate = .05
mortality_time_lag = 2

## set wind conditions
wind_dir = "NONE"
kappa = 3

## set lethal temperature conditions
use_lethal_temperature = FALSE
lethal_temperature = NA
lethal_temperature_month = NA

## set weather conditions
weather = FALSE

## set end and start dates
season_month_start = 1
season_month_end = 12
time_step = "month"
start_time = 2001
end_time = 2005


## get data formatted:
random_seed = 42
number_of_years = end_time-start_time+1

if (time_step == "week") {
  number_of_time_steps = (end_time-start_time+1)*52
} else if (time_step == "month") {
  number_of_time_steps = (end_time-start_time+1)*12
} else if (time_step == "day") {
  number_of_time_steps = (end_time-start_time+1)*365
}

infected = raster(infected_file)
infected[is.na(infected)] <- 0
host = raster(host_file)
host[is.na(host)] <- 0
susceptible = host - infected
susceptible[is.na(susceptible)] <- 0
total_plants = raster(total_plants_file)
total_plants[is.na(total_plants)] <- 0


if (use_lethal_temperature == TRUE) {
  temperature_stack = stack(temperature_file)
  temperature_stack[is.na(temperature_stack)] <- 0
  temperature = list(as.matrix(temperature_stack[[1]]))
  for(i in 2:number_of_years) {
    temperature[[i]] <- as.matrix(temperature_stack[[i]])
  }
} else {
  temperature <- host
  values(temperature) <- 1
  temperature <- list(as.matrix(temperature))
}

if (weather == TRUE){
  weather_coefficient_stack[is.na(weather_coefficient_stack)] <- 0
  weather_coefficient <- list(as.matrix(weather_coefficient_stack[[1]]))
  for(i in 2:number_of_time_steps) {
    weather_coefficient[[i]] <- as.matrix(weather_coefficient_stack[[i]])
  }
} else {
  weather_coefficient <- host
  values(weather_coefficient) <- 1
  weather_coefficient <- list(as.matrix(weather_coefficient))
}

if (management == TRUE) {
  treatment_stack <- stack(treatments_file)
  treatment_stack[is.na(treatment_stack)] <- 0
  treatment_maps <- list(as.matrix(treatment_stack[[1]]))
  if (nlayers(treatment_stack) >= 2) {
    for(i in 2:nlayers(treatment_stack)) {
      treatment_maps[[i]] <- as.matrix(treatment_stack[[i]])
    }
  }
  treatment_years = treatment_years
} else {
  treatment_map <- host
  values(treatment_map) <- 0
  treatment_maps = list(as.matrix(treatment_map))
  treatment_years = c(0)
}

mortality_tracker = infected
values(mortality_tracker) <- 0
mortality <- mortality_tracker
ew_res = xres(susceptible)
ns_res = yres(susceptible)
infected = as.matrix(infected)
susceptible = as.matrix(susceptible)
total_plants = as.matrix(total_plants)
mortality_tracker = as.matrix(mortality_tracker)
mortality <- as.matrix(mortality)



 ##### Run the pops model once ######
data <- pops_model(random_seed = random_seed, 
                   lethal_temperature = lethal_temperature, use_lethal_temperature, lethal_temperature_month,
                   reproductive_rate = reproductive_rate, 
                   weather = weather, mortality_on = mortality_on,
                   short_distance_scale = short_distance_scale, infected = infected,
                   susceptible = susceptible, mortality_tracker = mortality_tracker, mortality = mortality,
                   total_plants = total_plants, 
                   treatment_maps = treatment_maps, treatment_years = treatment_years,
                   temperature = temperature,
                   weather_coefficient = weather_coefficient, 
                   ew_res = ew_res, ns_res = ns_res,
                   time_step = time_step, mortality_rate = mortality_rate, mortality_time_lag = mortality_time_lag,
                   season_month_start = season_month_start, season_month_end = season_month_end,
                   start_time = start_time, end_time = end_time,
                   dispersal_kern = "cauchy", percent_short_distance_dispersal = 1.0,
                   long_distance_scale = 0.0,
                   wind_dir = wind_dir, kappa = kappa)

 
 ###### Run the pops model 100 times to generate a range of outputs #####
data2 <- list(data)
for (seed in 1:100) {
  random_seed <- round(stats::runif(1, 1, 1000000))
  data2[[seed]] <- pops_model(random_seed = random_seed, 
                              lethal_temperature = lethal_temperature, use_lethal_temperature, lethal_temperature_month,
                              reproductive_rate = reproductive_rate, 
                              weather = weather, mortality_on = mortality_on,
                              short_distance_scale = short_distance_scale, infected = infected,
                              susceptible = susceptible, mortality_tracker = mortality_tracker, mortality = mortality,
                              total_plants = total_plants, 
                              treatment_maps = treatment_maps, treatment_years = treatment_years,
                              temperature = temperature,
                              weather_coefficient = weather_coefficient, 
                              ew_res = ew_res, ns_res = ns_res,
                              time_step = time_step, mortality_rate = mortality_rate, mortality_time_lag = mortality_time_lag,
                              season_month_start = season_month_start, season_month_end = season_month_end,
                              start_time = start_time, end_time = end_time,
                              dispersal_kern = "cauchy", percent_short_distance_dispersal = 1.0,
                              long_distance_scale = 0.0,
                              wind_dir = wind_dir, kappa = kappa)
}


## process outputs to create stacks with all modeled infection data
infected = raster(infected_file)
infected[is.na(infected)] <- 0
infected_stack <- stack()
infected_list <- list()
for (j in 1:length(data2)) {
  infected_stack <- stack()
  for (q in 1:length(data2[[1]]$infected_before_treatment)) {
    infected[] <- data2[[j]]$infected_before_treatment[[q]]
    infected_stack <- stack(infected_stack, infected)
  }
  infected_list[[j]] <- infected_stack
}
m <- c(0, .99, 0,
       1, Inf,1)
rcl_mat <- matrix(m, ncol=3, byrow=TRUE)
prediction_list <- list()
probability <- prediction <- reclassify(infected_list[[1]], rcl_mat)
probability[probability > 0] <- 0
for (i in 1:length(infected_list)) {
  prediction <- reclassify(infected_list[[i]], rcl_mat)
  prediction_list[[i]] <- prediction
  probability <- probability + prediction
}
all_2001_inf = stack()
all_2002_inf = stack()
all_2003_inf = stack()
all_2004_inf = stack()
all_2005_inf = stack()
for (k in 1:length(infected_list)) {
  run = infected_list[[k]]
  run_stack = stack(run)
  inf_2001 = subset(run_stack, 1:1)
  inf_2002 = subset(run_stack, 2:2)
  inf_2003 = subset(run_stack, 3:3)
  inf_2004 = subset(run_stack, 4:4)
  inf_2005 = subset(run_stack, 5:5)
  all_2001_inf = stack(all_2001_inf, inf_2001)
  all_2002_inf = stack(all_2002_inf, inf_2002)
  all_2003_inf = stack(all_2003_inf, inf_2003)
  all_2004_inf = stack(all_2004_inf, inf_2004)
  all_2005_inf = stack(all_2005_inf, inf_2005)
}


##### Create the quantity allocation function
quantity_allocation_disagreement <- function(reference, comparison){
  # test that the comparison raster is the same extent, resolution, and crs as the reference (if not end)
  raster::compareRaster(reference, comparison)
  compare <- reference - comparison
  # compare3 <- reference + comparison
  # extent = extent(reference)
  # num_of_cells = max(cellsFromExtent(reference, extent(reference)))
  
  # calculate number of infected patches
  reference_no0 <- reference
  comparison_no0 <- comparison
  reference_no0[reference_no0 == 0] <- NA
  comparison_no0[comparison_no0 == 0] <- NA
  NP_ref <- landscapemetrics::lsm_c_np(reference_no0, directions = 8)$value
  if (sum(comparison_no0[comparison_no0 >0]) == 0) {
    NP_comp <- 0
    ENN_MN_comp <- 0
    PARA_MN_comp <- 0
    LPI_comp <- 0
  } else {
    NP_comp <- landscapemetrics::lsm_c_np(comparison_no0, directions = 8)$value
  }
  
  change_NP <- abs((NP_comp - NP_ref)/NP_ref)
  
  # calculate the mean euclidean distance between patches
  if (NP_ref > 1) {
    ENN_MN_ref <- landscapemetrics::lsm_c_enn_mn(reference_no0, directions = 8, verbose = TRUE)$value
  } else  if (NP_ref == 1) {
    ENN_MN_ref <- 0
  }
  
  if (sum(comparison_no0[comparison_no0 > 0]) != 0 && NP_comp > 1) {
    ENN_MN_comp <- landscapemetrics::lsm_c_enn_mn(comparison_no0, directions = 8, verbose = TRUE)$value
  } else  if (sum(comparison_no0[comparison_no0 > 0]) != 0 && NP_comp <= 1) {
    ENN_MN_comp <- 0
  }
  
  if (ENN_MN_ref != 0) {
    change_ENN_MN <- abs((ENN_MN_comp - ENN_MN_ref)/ENN_MN_ref)
  } else if (ENN_MN_comp == 0 && ENN_MN_ref == 0) {
    change_ENN_MN <- 0
  } else {
    change_ENN_MN <- 1
  }
  
  # calculate the mean perimeter-area ratio of patches and the difference
  PARA_MN_ref <- landscapemetrics::lsm_c_para_mn(reference_no0, directions = 8)$value
  if (sum(comparison_no0[comparison_no0 >0]) == 0) {
    PARA_MN_comp <- 0
  } else if (sum(comparison_no0[comparison_no0 >0]) != 0) {
    PARA_MN_comp <- landscapemetrics::lsm_c_para_mn(comparison_no0, directions = 8)$value
  }
  
  change_PARA_MN <- abs((PARA_MN_comp - PARA_MN_ref)/PARA_MN_ref) 
  
  # calculate the largest patch index and difference
  LPI_ref <- landscapemetrics::lsm_c_lpi(reference_no0, directions = 8)$value
  if (sum(comparison_no0[comparison_no0 >0]) == 0) {
    LPI_comp <- 0
  } else if (sum(comparison_no0[comparison_no0 >0]) != 0) {
    LPI_comp <- landscapemetrics::lsm_c_lpi(comparison_no0, directions = 8)$value
  }
  
  change_LPI <- abs(LPI_comp - LPI_ref) / 100
  
  # calculate landscape similarity index between reference and comparison
  LSI <- 1 - ((change_NP + change_ENN_MN + change_PARA_MN + change_LPI) / 4)
  if (LSI < 0) { LSI <- 0 }
  
  ## create data frame for comparison
  output <- data.frame(quantity_disagreement = 0, allocation_disagreement = 0, total_disagreement = 0, omission = 0, commission = 0 , number_of_infected_comp = 0, directional_disagreement = 0, landscape_similarity = 0)
  output$total_disagreement <- sum(compare[compare == 1]) + abs(sum(compare[compare == -1]))
  output$quantity_disagreement <- abs(sum(compare[compare == 1]) + sum(compare[compare == -1]))
  output$allocation_disagreement <- output$total_disagreement - output$quantity_disagreement
  output$omission <- abs(sum(compare[compare == 1]))
  output$commission <- abs(sum(compare[compare == -1]))
  output$number_of_infected_comp <- sum(comparison[comparison == 1])
  output$directional_disagreement <- sum(compare[compare == 1]) + sum(compare[compare == -1])
  output$landscape_similarity <- LSI
  # output$true_positives <- abs(sum(compare3[compare3 ==2]))
  # output$true_negatives <- num_of_cells - output$omission - output$commission - output$true_positives
  # output$odds_ratio = (output$true_positives*output$true_negatives)/(output$omission*output$commission)
  
  return(output)
}


## for every modeled infection in 2005, compare to real infection and write to a dataset
actual_infections = stack("input_data/infected_years.tif")
actual_inf_2005 = subset(actual_infections, 5:5)
validation_2005 <- data.frame()
rcl <- c(1, 50000, 1, 0, 0.99, NA)
rclmat <- matrix(rcl, ncol=3, byrow=TRUE)
for (i in 1:nlayers(all_2005_inf)){
  reference = reclassify(actual_inf_2005, rclmat)
  comparison = subset(all_2005_inf, i:i)
  comparison = reclassify(comparison, rclmat)
  output = data.frame(quantity_allocation_disagreement(reference, comparison))
  validation_2005 <- rbind(validation_2005, output)
}


## get summary stats from dataset about total disagreement and landscape similarity
average_total_disagreement = mean(validation_2005$total_disagreement)
print(paste("Average Total Disagreement: ", average_total_disagreement))
average_landscape_similarity = mean(validation_2005$landscape_similarity)
print(paste("Average Landscape Similarity: ", average_landscape_similarity))
