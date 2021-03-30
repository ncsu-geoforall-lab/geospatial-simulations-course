library(PoPS)
library(folderfun)

setff("In", "/path/to/files/")

### Calibration from 2017 to 2018

# number of infected cells
number_of_observations <- 88

# if we had prior years of calibration
prior_number_of_observations <- 0
prior_means <- c(0, 0, 0, 0, 0, 0)
prior_cov_matrix <- matrix(ncol = 6, nrow = 6, 0)

# reproductive_rate, natural_dispersal_distance, percent_natural_dispersal, anthropogenic_dispersal_distance, natural kappa, and anthropogenic kappa
params_to_estimate <- c(T, T, F, F, T, F)

# lower these if too slow
number_of_generations <- 5
generation_size <- 30

# 1: difference between number of infected cells in different years * 2
# 2: difference in distance in different years * 2
checks = c(80, 20000, 0, 0)
success_metric <- "number of locations and total distance"

# input files
infected_years_file <- ffIn("cum_inf_2018eu.tif")
infected_file <- ffIn("end_inf_2017eu.tif")
host_file <- ffIn("lide_100m_median_2015.tif")
total_plants_file <- ffIn("lemma_max100m.tif")
temperature_coefficient_file <- ffIn("weather_coef_2018.tif")
mask <- NULL

# PoPS model parameters
temp <- TRUE
precip <- FALSE
precipitation_coefficient_file <- ""
model_type <- "SI"
latency_period <- 0
time_step <- "week"
season_month_start <- 1
season_month_end <- 12
start_date <- '2018-01-01'
end_date <- '2018-12-31'
use_lethal_temperature <- FALSE
temperature_file <- ""
lethal_temperature <- -30
lethal_temperature_month <- 1
mortality_on <- FALSE
mortality_rate <- 0
mortality_time_lag <- 0
management <- FALSE
treatment_dates <- c('2018-12-24')
treatments_file <- ""
treatment_method <- "ratio"
natural_kernel_type <- "exponential"
anthropogenic_kernel_type <- "cauchy"
natural_dir <- "N"
natural_kappa <- 2
anthropogenic_dir <- "NONE"
anthropogenic_kappa <- 0
pesticide_duration <- c(0)
pesticide_efficacy <- 1.0
output_frequency <- "year"
output_frequency_n <- 1
movements_file = ""  ## ignore - for pigs
use_movements = FALSE
percent_natural_dispersal <- 1.0
anthropogenic_distance_scale <- 0.0

# calibration
eu_sod_2017_2018_ratio <- PoPS::calibrate(infected_years_file, 
                                    number_of_observations, prior_number_of_observations,
                                    prior_means, prior_cov_matrix, params_to_estimate,
                                    number_of_generations,
                                    generation_size,
                                    checks,
                                    infected_file, host_file, total_plants_file, 
                                    temp, temperature_coefficient_file, 
                                    precip, precipitation_coefficient_file,
                                    model_type, latency_period,
                                    time_step, 
                                    season_month_start, season_month_end, 
                                    start_date, end_date, 
                                    use_lethal_temperature, temperature_file,
                                    lethal_temperature, lethal_temperature_month,
                                    mortality_on, mortality_rate, mortality_time_lag, 
                                    management, treatment_dates, treatments_file,
                                    treatment_method,
                                    natural_kernel_type, anthropogenic_kernel_type,
                                    natural_dir, natural_kappa, 
                                    anthropogenic_dir, anthropogenic_kappa,
                                    pesticide_duration, pesticide_efficacy,
                                    mask, success_metric, output_frequency, output_frequency_n,
                                    movements_file, use_movements)
# explore results
summary(eu_sod_2017_2018_ratio)
means_2017_2018_ratio = as.data.frame(eu_sod_2017_2018_ratio$posterior_means)
cov_2017_2018_ratio = as.data.frame(eu_sod_2017_2018_ratio$posterior_cov_matrix)
raw_calib_2017_2018_ratio = as.data.frame(eu_sod_2017_2018_ratio$raw_calibration_data)
total_obs_2017_2018 = as.data.frame(eu_sod_2017_2018_ratio$total_number_of_observations)
