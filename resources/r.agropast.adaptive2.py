#!/usr/bin/env python
#
############################################################################
#
# MODULE:               r.agropast.semiadaptive.7.0.5
#
# AUTHOR(S):            Isaac Ullah, San Diego State University
#
# PURPOSE:              Simulates agricultural and pastoral landuse and tracks
#                       yields and environmental impacts. Farming and grazing
#                       strategies and yield goals are predetermined by the
#                       researcher, and do not change (adapt) during the
#                       simulation. However, catchment sizes can be adapted
#                       over time to meet these goals. This version implments
#                       a land tenuring alogrithm. Requires r.landscape.evol.
#
# ACKNOWLEDGEMENTS:     National Science Foundation Grant #BCS0410269, Center
#                       for Comparative Archaeology at the University of
#                       Pittsburgh, Center for Social Dynamics and Complexity
#                       at Arizona State University, San Diego State University
#
# COPYRIGHT:            (C) 2016 by Isaac Ullah, San Diego State University
#
#                   This program is free software under the GNU General Public
#                   License (>=v2). Read the file COPYING that comes with GRASS
#                   for details.
#
#############################################################################


#%Module
#%  description: Simulates agricultural and pastoral landuse and tracks yields and environmental impacts. Basic farming and grazing strategies and yield goals are predetermined by the researcher, and do not change (adapt) during the simulation, but it is possible for population to change based on returns. This version implments a land tenuring alogrithm. Requires r.landscape.evol. Note that some stats files will be written to current mapset, and will be appended to if you run the simulation again with the same prefix.
#%END

##################################
#Simulation Control
##################################
#%option
#% key: years
#% type: integer
#% description: Number of iterations ("years") to run
#% answer: 200
#% required: yes
#% guisection: Simulation Control
#%END
#%option
#% key: prefx
#% type: string
#% description: Prefix for all output maps
#% answer: sim
#% required: yes
#% guisection: Simulation Control
#%END

##################################
#Agent Properties
##################################
#%option
#% key: numpeople
#% type: double
#% description: Number of people in the village(s) (starting population size with flag -p, otherwise stays constant throughout the simulation)
#% answer: 120
#% guisection: Agent Properties
#%END
#%option
#% key: birthrate
#% type: double
#% description: Per-capita human fecundity (only active with flag -p)
#% answer: 0.054
#% guisection: Agent Properties
#%END
#%option
#% key: deathrate
#% type: double
#% description: Per-capita human mortality hazard (only active with flag -p)
#% answer: 0.04
#% guisection: Agent Properties
#%END
#%option
#% key: starvthresh
#% type: double
#% description: Starvation threshold. If returns are below this percentage of the normal subsistence needs, people bcome "resource-starved." No births will occur, but deaths will still happen. (only active with flag -p)
#% answer: 0.6
#% guisection: Agent Properties
#%END
#%option
#% key: agentmem
#% type: integer
#% description: Length of the "memory" of the agent in years. The agent will use the mean surplus/defict information from this many of the most recent previous years when making a subsistence plan for the current year.
#% answer: 5
#% guisection: Agent Properties
#%END
#%option
#% key: aglabor
#% type: double
#% description: The amount of agricultural labor an average person of the village can do in a year (in "person-days")
#% answer: 300
#% guisection: Agent Properties
#%END
#%option
#% key: cerealreq
#% type: double
#% description: Amount of cereals that would be required per person per year if cereals were the ONLY food item (Kg)
#% answer: 370
#% guisection: Agent Properties
#%END
#%option
#% key: animals
#% type: double
#% description: Number of herd animals that would be needed per person per year if pastoral products were the ONLY food item
#% answer: 60
#% guisection: Agent Properties
#%END
#%option
#% key: fodderreq
#% type: double
#% description: Amount of fodder required per herd animal per year (Kg)
#% answer: 680
#% guisection: Agent Properties
#%END
#%option
#% key: a_p_ratio
#% type: double
#% description: Actual ratio of agricultural to pastoral foods in the diet (0-1, where 0 = 100% agricultural and 1 = 100% pastoral)
#% answer: 0.20
#% options: 0.0-1.0
#% guisection: Agent Properties
#%END
#%option
#% key: costsurf
#% type: string
#% gisprompt: old,cell,raster
#% description: Map of movement costs from the center of the agricultural/grazing catchments (from r.walk or r.cost).
#% guisection: Agent Properties
#%END
#%flag
#% key: p
#% description: -p Allow the population to vary over time, according to subsistence returns
#% guisection: Agent Properties
#%end


##################################
#Farming Options
##################################
#%option
#% key: agcatch
#% type: string
#% gisprompt: old,cell,raster
#% description: Map of the largest possible agricultural catchment map (From r.catchment or r.buffer, where catchment is a single integer value, and all else is NULL)
#% guisection: Farming
#%END
#%option
#% key: agmix
#% type: double
#% description: The wheat/barley ratio (e.g., 0.0 for all wheat, 1.0 for all barley, 0.5 for an equal mix)
#% answer: 0.25
#% options: 0.0-1.0
#% guisection: Farming
#%END
#%option
#% key: nsfieldsize
#% type: double
#% description: North-South dimension of fields in map units (Large field sizes may lead to some overshoot of catchment boundaries)
#% answer: 20
#% guisection: Farming
#%END
#%option
#% key: ewfieldsize
#% type: double
#% description: East-West dimension of fields in map units (Large field sizes may lead to some overshoot of catchment boundaries)
#% answer: 50
#% guisection: Farming
#%END
#%option
#% key: fieldlabor
#% type: double
#% description: Number of person-days required to till, sow, weed, and harvest one farm field in a year.
#% answer: 50
#% guisection: Farming
#%END
#%option
#% key: farmval
#% type: double
#% description: The landcover value for farmed fields (Should correspond to an appropriate value from your landcover rules file.)
#% answer: 5
#% guisection: Farming
#%END
#%option
#% key: farmimpact
#% type: double
#% description: The mean and standard deviation of the amount to which farming a patch decreases its fertility (in percentage points of maximum fertility, entered as: "mean,std_dev"). Fertility impact values of indvidual farm plots will be randomly chosen from a gaussian distribution that has this mean and std_dev.
#% answer: 3,2
#% multiple: yes
#% guisection: Farming
#%END
#%option
#% key: maxwheat
#% type: double
#% description: Maximum amount of wheat that can be grown (kg/ha)
#% answer: 1750
#% guisection: Farming
#%END
#%option
#% key: maxbarley
#% type: double
#% description: Maximum amount of barley that can be grown (kg/ha)
#% answer: 1250
#% guisection: Farming
#%END
#%option
#% key: tenuretype
#% type: string
#% description: Choose the land tenuring strategy: "None" (Fields are chosen at random each year), "Satisficing" (First year's fields are chosen at random. Fields are tenured, but some may be randomly dropped or added to meet the minimum need), "Maximizing" (Same as "satisficing", but tenured fields are only dropped if production falls below the threshold defined by "tenuredrop," not according to minimum need.)
#% answer: Maximize
#% options: None,Maximize,Satisfice
#% guisection: Farming
#%END
#%option
#% key: tenuredrop
#% type: double
#% description: Threshold for dropping land out of tenure (with tenuretype as "Maximize"). If the value is 0, fields that yield less than the mean of all fields are dropped. If the value is greater than 0, then fields that are lower than that percentage of the maximum yield of all fields will be dropped.
#% answer: 0.1
#% options: 0.0-1.0
#% guisection: Farming
#%END

##################################
#Grazing Options
##################################
#%option
#% key: grazecatch
#% type: string
#% gisprompt: old,cell,raster
#% description: Map of the largest possible grazing catchment (From r.catchment or r.buffer, where catchment is a single integer value, and all else is NULL).
#% guisection: Grazing
#%END
#%option
#% key: mingraze
#% type: double
#% description: Minimum amount of vegetation on a cell for it to be considered grazeable (in value of succession stages, matching landcover rules file)
#% answer: 2
#% guisection: Grazing
#%END
#%option
#% key: grazespatial
#% type: double
#% description: Spatial dependency of the grazing pattern in map units. This value determines how "clumped" grazing patches will be. A value close to 0 will produce a perfectly randomized grazing pattern with patch size=resolution, and larger values will produce increasingly clumped grazing patterns, with the size of the patches corresponding to the value of grazespatial (in map units).
#% answer: 50
#% guisection: Grazing
#%END
#%option
#% key: grazepatchy
#% type: double
#% description: Coefficient that determines the patchiness of the grazing catchemnt. Value must be non-zero, and usually will be <= 1.0. Values close to 0 will create a patchy grazing pattern, values close to 1 will create a "smooth" grazing pattern. Actual grazing patches will be sized to the resolution of the input landcover map.
#% answer: 1.0
#% guisection: Grazing
#%END
#%option
#% key: maxgrazeimpact
#% type: integer
#% description: Maximum impact of grazing in units of "landcover.succession". Grazing impact values of individual patches will be chosen from a gaussian distribution between 1 and this maximum value (i.e., most values will be between 1 and this max). Value must be >= 1.
#% answer: 3
#% guisection: Grazing
#%END
#%option
#% key: manurerate
#% type: double
#% description: Base rate that animal dung contributes to fertility increase on a grazed patch in units of percentage of maximum fertility regained per increment of grazing impact. Actual fertility regain values are thus calculated as "manure_rate x grazing_impact", so be aware that this variable interacts with the grazing impact settings you have chosen.
#% answer: 0.03
#% options: 0.0-100.0
#% guisection: Grazing
#%END
#%option
#% key: fodder_rules
#% type: string
#% gisprompt: old,file,file
#% description: Path to foddering rules file for calculation of fodder gained by grazing
#% answer: /rules/fodder_rules.txt
#% guisection: Grazing
#%END
#%flag
#% key: f
#% description: -f Do not graze in unused portions of the agricultural catchment (i.e., do not graze on "fallowed" fields, and thus no "manuring" of those fields will occur)
#% guisection: Grazing
#%end
#%flag
#% key: g
#% description: -g Do not allow "stubble grazing" on harvested fields (and thus no "manuring" of fields)
#% guisection: Grazing
#%end

##################################
#Landcover Dynamics Options
##################################
#%option
#% key: fertilrate
#% type: double
#% description: Comma separated list of the mean and standard deviation of the natural fertility recovery rate (percentage by which soil fertility increases per year if not farmed, entered as: "mean,stdev".) Fertility recovery values of individual landscape patches will be randomly chosen from a gaussian distribution that has this mean and std_dev.
#% answer: 2,0.5
#% multiple: yes
#% guisection: Landcover Dynamics
#%END
#%option
#% key: inlcov
#% type: string
#% gisprompt: old,cell,raster
#% description: Input landcover map (Coded according to landcover rules file below)
#% guisection: Landcover Dynamics
#%END
#%option
#% key: infert
#% type: string
#% gisprompt: old,cell,raster
#% description: Input fertility map (Coded according to percentage retained fertility, with 100 being full fertility)
#% guisection: Landcover Dynamics
#%END
#%option
#% key: fireprob
#% type: string
#% gisprompt: old,cell,raster
#% description: Map of fire probabilities due to natural lightning strikes (coded 0 to 1)
#% guisection: Landcover Dynamics
#%END
#%option
#% key: maxlcov
#% type: string
#% gisprompt: old,cell,raster
#% description: Maximum value of landcover for the landscape (Can be a single numerical value or a cover map of different maximum values. Shouldn't exceed maximum value in rules file')
#% answer: 50
#% guisection: Landcover Dynamics
#%END
#%option
#% key: maxfert
#% type: string
#% gisprompt: old,cell,raster
#% description: Maximum value of fertility for the landscape (Can be a single numerical value or a cover map of different maximum values. Shouldn't exceed 100)
#% answer: 100
#% guisection: Landcover Dynamics
#%END
#%option
#% key: lc_rules
#% type: string
#% gisprompt: old,file,file
#% description: Path to reclass rules file for landcover map
#% answer: /rules/luse_reclass_rules.txt
#% guisection: Landcover Dynamics
#%END
#%option
#% key: cfact_rules
#% type: string
#% gisprompt: old,file,file
#% description: Path to recode rules file for c-factor map
#% answer: /rules/cfactor_recode_rules.txt
#% guisection: Landcover Dynamics
#%END
#%flag
#% key: c
#% description: -c Keep C-factor (and rainfall excess) maps for each year
#% guisection: Landcover Dynamics
#%end

##################################
#Landscape Evolution Options
##################################
#%option
#% key: elev
#% type: string
#% gisprompt: old,cell,raster
#% description: Input elevation map (DEM of surface)
#% guisection: Landscape Evolution
#%end
#%option
#% key: initbdrk
#% type: string
#% gisprompt: old,cell,raster
#% description: Bedrock elevations map (DEM of bedrock)
#% answer:
#% guisection: Landscape Evolution
#%end
#%option
#% key: k
#% type: double
#% gisprompt: old,cell,raster
#% description: Soil erodability index (K factor) map or constant
#% answer: 0.42
#% guisection: Landscape Evolution
#%end
#%option
#% key: sdensity
#% type: double
#% gisprompt: old,cell,raster
#% description: Soil density map or constant [T/m3] for conversion from mass to volume
#% answer: 1.2184
#% guisection: Landscape Evolution
#%end
#%option
#% key: kt
#% type: double
#% description: Stream transport efficiency variable (0.001 for a soft substrate, 0.0001 for a normal substrate, 0.00001 for a hard substrate, 0.000001 for a very hard substrate)
#% answer: 0.0001
#% options: 0.001,0.0001,0.00001,0.000001
#% guisection: Landscape Evolution
#%end
#%option
#% key: loadexp
#% type: double
#% description: Stream transport type variable (1.5 for mainly bedload transport, 2.5 for mainly suspended load transport)
#% answer: 1.5
#% options: 1.5,2.5
#% guisection: Landscape Evolution
#%end
#%option
#% key: manningn
#% type: string
#% gisprompt: old,cell,raster
#% description: Map or constant of the value of Manning's "N" value for channelized flow.
#% answer: 0.05
#% required : no
#% guisection: Landscape Evolution
#%end
#%option
#% key: kappa
#% type: double
#% description: Hillslope diffusion (Kappa) rate map or constant [m/kyr]
#% answer: 1
#% guisection: Landscape Evolution
#%end
#%option
#% key: rain
#% type: string
#% gisprompt: old,cell,raster
#% description: Precip totals for the average storm [mm] (or path to climate file of comma separated values of "rain,R,storms,stormlength", with a new line for each year of the simulation)
#% answer: 20.61
#% guisection: Landscape Evolution
#%end
#%option
#% key: r
#% type: string
#% description: Rainfall (R factor) constant (AVERAGE FOR WHOLE MAP AREA) (or path to climate file of comma separated values of "rain,R,storms,stormlength", with a new line for each year of the simulation)
#% answer: 4.54
#% guisection: Landscape Evolution
#%end
#%option
#% key: storms
#% type: string
#% description: Number of storms per year (integer) (or path to climate file of comma separated values of "rain,R,storms,stormlength", with a new line for each year of the simulation)
#% answer: 25
#% guisection: Landscape Evolution
#%end
#%option
#% key: stormlength
#% type: string
#% description: Average length of the storm [h] (or path to climate file of comma separated values of "rain,R,storms,stormlength", with a new line for each year of the simulation)
#% answer: 24.0
#% guisection: Landscape Evolution
#%end
#%option
#% key: speed
#% type: double
#% description: Average velocity of flowing water in the drainage [m/s]
#% answer: 1.4
#% guisection: Landscape Evolution
#%end
#%option
#% key: cutoff1
#% type: double
#% description: Flow accumulation breakpoint value for shift from diffusion to overland flow
#% answer: 0
#% guisection: Landscape Evolution
#%end
#%option
#% key: cutoff2
#% type: double
#% description: Flow accumulation breakpoint value for shift from overland flow to rill/gully flow (if value is the same as cutoff1, no sheetwash procesess will be modeled)
#% answer: 100
#% guisection: Landscape Evolution
#%end
#%option
#% key: cutoff3
#% type: double
#% description: Flow accumulation breakpoint value for shift from rill/gully flow to stream flow (if value is the same as cutoff2, no rill procesess will be modeled)
#% answer: 100
#% guisection: Landscape Evolution
#%end
#%option
#% key: smoothing
#% type: string
#% description: Amount of additional smoothing (answer "no" unless you notice large spikes in the erdep rate map)
#% answer: no
#% options: no,low,high
#% guisection: Landscape Evolution
#%end
#%flag
#% key: 1
#% description: -1 Calculate streams as 1D difference instead of 2D divergence
#% guisection: Landscape Evolution
#%end
#%flag
#% key: k
#% description: -k Keep ALL temporary maps (overides flags -drst). This will make A LOT of maps!
#% guisection: Landscape Evolution
#%end
#%flag
#% key: d
#% description: -d Don't output yearly soil depth maps
#% guisection: Landscape Evolution
#%end
#%flag
#% key: r
#% description: -r Don't output yearly maps of the erosion/deposition rates ("ED_rate" map, in vertical meters)
#% guisection: Landscape Evolution
#%end
#%flag
#% key: s
#% description: -s Keep all slope maps
#% guisection: Landscape Evolution
#%end
#%flag
#% key: t
#% description: -t Keep yearly maps of the Transport Capacity at each cell ("Qs" maps)
#% guisection: Landscape Evolution
#%end
#%flag
#% key: e
#% description: -e Keep yearly maps of the Excess Transport Capacity (divergence) at each cell ("DeltaQs" maps)
#% guisection: Landscape Evolution
#%end

import sys
import os

#CAN NUMPY BE USED FOR RANDOM GAUSS, REDUCING DEPENDENCIES?
import random


import numpy
import grass.script as grass

# New random-poisson babymaker
def babymaker(p, n): #p is the per capita birth rate, n is the population size
    babys = (numpy.random.poisson(p*100)/100.)*n
    return(int(babys))

# New random-poisson deathdealer
def deathdealer(p, n): #p is the per capita death rate, n is the population size
    deaths = (numpy.random.poisson(p*100)/100.)*n
    return(int(deaths))

# Main block of code starts here
def main():
    grass.message("Setting up Simulation........")

    # Setting up Land Use variables for use later on
    agcatch = options['agcatch']
    nsfieldsize = options['nsfieldsize']
    ewfieldsize = options['ewfieldsize']
    grazecatch = options['grazecatch']
    grazespatial = options['grazespatial']
    grazepatchy = options['grazepatchy']
    maxgrazeimpact = options['maxgrazeimpact']
    manurerate = options['manurerate']
    inlcov = options['inlcov']
    years = int(options['years'])
    farmval = options['farmval']
    maxlcov = options['maxlcov']
    p = options['prefx'] + "_"
    lc_rules = options['lc_rules']
    cfact_rules = options['cfact_rules']
    fodder_rules = options['fodder_rules']
    infert = options['infert']
    fireprob = options['fireprob']
    maxfert = options['maxfert']
    maxwheat = options['maxwheat']
    maxbarley = options['maxbarley']
    mingraze = options['mingraze']
    costsurf = options['costsurf']
    agmix = options['agmix']
    numpeople = float(options['numpeople'])
    birthrate = float(options['birthrate'])
    deathrate = float(options['birthrate'])
    starvthresh = float(options['starvthresh'])
    agentmem = int(options['agentmem'])
    animals = float(options['animals'])
    agratio = 1 - float(options['a_p_ratio'])
    pratio =  float(options['a_p_ratio'])
    indcerreq = float(options['cerealreq'])
    indfodreq = float(options['fodderreq'])
    aglabor = float(options['aglabor'])
    fieldlabor = float(options['fieldlabor'])
    cereal_pers = numpeople * agratio
    fodder_anim = animals * numpeople * pratio
    cerealreq = indcerreq * cereal_pers
    fodderreq = indfodreq * fodder_anim
    totlabor = numpeople * aglabor
    maxfields = int(round(totlabor / fieldlabor))

    # These are various rates with min and max values entered in the gui that we need to parse
    farmimpact = list(map(float, options['farmimpact'].split(',')))
    fertilrate = list(map(float, options['fertilrate'].split(',')))

    # Setting up Landscape Evol variables to write the r.landscape.evol command later
    elev = options["elev"]
    initbdrk = options["initbdrk"]

    # These values could be read in from a climate file, so check that, and act accordingly
    rain2 = []
    try:
        rain1 = float(options['rain'])
        for year in range(int(years)):
            rain2.append(rain1)
    except:
        with open(options['rain'], 'rU') as f:
            for line in f:
                rain2.append(line.split(",")[0])
        #check for text header and remove if present
        try:
            float(rain2[0])
        except:
            del rain2[0]
        #throw a fatal error if there aren't enough values in the column
        if len(rain2) != int(years):
            grass.fatal("Number of rows of rainfall data in your climate file\n do not match the number of iterations you wish to run.\n Please ensure that these numbers match and try again")
            sys.exit(1)
    R2 = []
    try:
        R1 = float(options['r'])
        for year in range(int(years)):
            R2.append(R1)
    except:
        with open(options['r'], 'rU') as f:
            for line in f:
                R2.append(line.split(",")[1])

        # Check for text header and remove if present
        try:
            float(R2[0])
        except:
            del R2[0]

        # Throw a fatal error if there aren't enough values in the column
        if len(R2) != int(years):
            grass.fatal("Number of rows of R-Factor data in your climate file\n do not match the number of iterations you wish to run.\n Please ensure that these numbers match and try again")
            sys.exit(1)
    storms2 = []
    try:
        storms1 = float(options['storms'])
        for year in range(int(years)):
            storms2.append(storms1)
    except:
        with open(options['storms'], 'rU') as f:
            for line in f:
                storms2.append(line.split(",")[2])

        # Check for text header and remove if present
        try:
            float(storms2[0])
        except:
            del storms2[0]
        # Throw a fatal error if there aren't enough values in the column
        if len(storms2) != int(years):
            grass.fatal("Number of rows of storm frequency data in your climate file\n do not match the number of iterations you wish to run.\n Please ensure that these numbers match and try again")
            sys.exit(1)
    stormlength2 = []
    try:
        stormlength1 = float(options['stormlength'])
        for year in range(int(years)):
            stormlength2.append(stormlength1)
    except:
        with open(options['stormlength'], 'rU') as f:
            for line in f:
                stormlength2.append(line.split(",")[3])

        # Check for text header and remove if present
        try:
            float(stormlength2[0])
        except:
            del stormlength2[0]

        # Throw a fatal error if there aren't enough values in the column
        if len(stormlength2) != int(years):
            grass.fatal("Number of rows of storm length data in your climate file\n do not match the number of iterations you wish to run.\n Please ensure that these numbers match and try again")
            sys.exit(1)

    # Get the process id to tag any temporary maps we make for easy clean up in the loop
    pid = os.getpid()

    # We need to separate out flags used by this script, and those meant to be
    # sent to r.landscape.evol. We will do this by popping them out of the
    # default "flags" dictionary, and making a new dictionary called "use_flags"
    use_flags = {}
    use_flags.update({'g': flags.pop('g'), 'f': flags.pop('f'), 'c': flags.pop('c'), 'p': flags.pop('p')})

    # Now assemble the flag string for r.landscape.evol'
    levol_flags = []
    for flag in flags:
        if flags[flag] is True:
            levol_flags.append(flag)

    # Check if maxlcov is a map or a number, and grab the actual max value for the stats file
    try:
        maxval = int(float(maxlcov))

    except:
        maxlcovdict = grass.parse_command('r.univar', flags = 'ge', map = maxlcov)
        maxval = int(float(maxlcovdict['max']))

    # Check if maxfert is a map or a number, and grab the actual max value for the stats file
    try:
        maxfertval = int(float(maxfert))
    except:
        maxfertdict = grass.parse_command('r.univar', flags = 'ge', map = maxfert)
        maxfertval = int(float(maxfertdict['max']))

    # Set up the stats files names
    env = grass.gisenv()
    statsdir = os.path.join(env['GISDBASE'], env['LOCATION_NAME'], env['MAPSET'])
    textout = statsdir + os.sep + p + '_landcover_temporal_matrix.txt'
    textout2 = statsdir + os.sep + p + '_fertility_temporal_matrix.txt'
    textout3 = statsdir + os.sep + p + '_yields_stats.txt'
    textout4 = statsdir + os.sep + p + '_landcover_and_fertility_stats.txt'
    statsout = statsdir + os.sep + p + '_erdep_stats.txt'

    # Figure out the number of cells per hectare and how many square meters
    # per cell to use as conversion factors for yields
    region = grass.region()
    cellperhectare = 10000 / (float(region['nsres']) * float(region['ewres']))

    # Do same for farm field size
    fieldsperhectare = 10000 / (float(nsfieldsize) * float(ewfieldsize))

    # Set up the agent memory
    droppedcells = 0

    # Set up the agent memory
    farmingmemory = []
    farmyieldmemory = []
    grazingmemory = []
    grazeyieldmemory = []

    grass.message('Simulation will run for %s iterations.\n\n............................STARTING SIMULATION...............................' % years)
    # Before we get going on the loop, write out some basic information about
    # the run. These can be used to remember what the settings were for this
    # particular run, as well as to provide some interpretation for the other
    # stats files that will be made.
    f = open(statsdir + os.sep + p + '_run_info.txt', 'a')
    f.write("Variables used in the model:\ncell resolution (grazing patch size),%s\nagcatch,%s\nnsfieldsize,%s\newfieldsize,%s\ngrazecatch,%s\ngrazespatial,%s\ngrazepatchy,%s\nmaxgrazeimpact,%s\nmanurerate,%s\ninlcov,%s\nyears,%s\nfarmval,%s\nmaxfert,%s\nmaxwheat,%s\nmaxbarley,%s\nagmix,%s\nagentmem,%s\nnumpeople,%s\nanimals,%s\ncalculated agricultural ratio,%s\ncalculated pastoral ratio,%s\ncalculated cereal required per person,%s\ncalculated fodder required per animal,%s\ncalculated total cereal required,%s\ncalculated total number of animals required,%s\ncalculated total fodder required,%s\n\nFarming stats in Kg wheat and/or barley seeds per farmplot.\nGrazing stats in Kg of digestable matter per grazing plot. Note that this may also include stubble grazing if enabled." % (region['nsres'],agcatch,nsfieldsize,ewfieldsize,grazecatch,grazespatial,grazepatchy,maxgrazeimpact,manurerate,inlcov,years,farmval,maxfert,maxwheat,maxbarley,agmix,agentmem,numpeople,animals,agratio,pratio,indcerreq,fodder_anim,indfodreq,cerealreq,fodderreq))
    f.close()

    # Set up loop
    for x in range(int(years)):
        o = x + 1
        m = x
        if numpeople == 0:
            grass.fatal("Everybody is dead. \nSimulation stopped at year %s." % m)

        # Grab the current climate vars from the lists
        rain = rain2[m]
        r = R2[m]
        storms = storms2[m]
        stormlength = stormlength2[m]

        # Figure out total precip (in meters) for the year for use in the veg
        # growth and farm yields formulae
        precip = 0.001 * (float(rain) * float(storms))
        grass.message('_____________________________\nSIMULATION YEAR: %s\n--------------------------' % o)

        # Make some map names
        fields        = "%sFarming_Impacts_Map%04d" % (p, o)
        outlcov       = "%sLandcover_Map%04d" % (p, o)
        outfert       = "%sSoil_Fertilty_Map%04d" % (p, o)
        outcfact      = "%sCfactor_Map%04d" % (p, o)
        grazeimpacts  = "%sGazing_Impacts_Map%04d" % (p, o)
        outxs         = "%sRainfall_Excess_Map%04d" % (p, o)
        oldsdepth     = "%sSoil_Depth_Map0001" % (p)
        natural_fires = "%sNatural_Fires_Map%04d" % (p, o)

        # Check if this is year one, use the starting landcover and soilfertily
        # and calculate soildepths
        if m == 0:
            oldlcov = inlcov
            oldfert = infert
            grass.mapcalc("${sdepth} = (${elev}-${bdrk})",
                            quiet = True,
                            sdepth = oldsdepth,
                            elev = elev,
                            bdrk = initbdrk)
        else:
            oldlcov = "%sLandcover_Map%04d" % (p, m)
            oldfert = "%sSoil_Fertilty_Map%04d" % (p, m)

        # Run farming impacts method
        # farmImpacts():
        # needs these variables: precip, sfertil, sdepth, maxwheat, maxbarley, fieldsperhectare, agmix, agcatch, farmyieldmemory, cerealstats2, fuzzydeficitmemory, agentmem, cerealreq, maxfields
        # produces these variables: tempfields, tempimpacta, tempwheatreturn, tempbarleyreturn, tempcerealreturn, cerealstats2, fuzzyyieldmemory, fuzzydeficitmemory, slicer, numfields, fieldpad

        # ***GENERATE FARM IMPACTS***
        # Create some temp map names
        tempfields = "%stemporary_fields_map" % pid
        tempimpacta = "%stemporary_farming_fertility_impact" % pid

        # Temporarily change region resolution to align to farm field size
        grass.use_temp_region()
        grass.run_command('g.region', quiet = True,nsres = nsfieldsize, ewres = ewfieldsize)

        # Generate the yields
        grass.message("Calculating potential farming yields.....")

        # Calculate the wheat yield map (kg/cell)
        tempwheatreturn = "%stemporary_wheat_yields_map" % pid
        e = '''{tempwheatreturn} = eval(x = if({precip} > 0, (0.51*log({precip}))+1.03, 0), \
                                         y = if({sfertil} > 0, (0.28*log({sfertil}))+0.87, 0), \
                                         z = if({sdepth} > 0, (0.19*log({sdepth}))+1, 0), \
                                         a = if(x <= 0 || z <= 0, 0, ((((x*y*z)/3)*{maxwheat})/{fieldsperhectare})), \
                                         if(a < 0, 0, a))'''
        twr = grass.mapcalc(e.format(  
                      tempwheatreturn = tempwheatreturn,
                      precip = precip,
                      sfertil = oldfert,
                      sdepth = oldsdepth,
                      maxwheat = maxwheat,
                      fieldsperhectare = fieldsperhectare),
                      quiet = True)

        # Calculate barley yield map (kg/cell)
        tempbarleyreturn = "%stemporary_barley_yields_map" % pid
        e = '''{tempbarleyreturn} = eval(x = if({precip} > 0, (0.48*log({precip}))+1.51, 0), \
                                          y = if({sfertil} > 0, (0.34*log({sfertil}))+1.09, 0), \
                                          z = if({sdepth} > 0, (0.18*log({sdepth}))+0.98, 0), \
                                          a = if(x <= 0 || z <= 0, 0, ((((x*y*z)/3)*{maxbarley})/{fieldsperhectare})), \
                                          if(a < 0, 0, a))'''
        tbr = grass.mapcalc(e.format(
                      tempbarleyreturn = tempbarleyreturn,
                      precip = precip,
                      sfertil = oldfert,
                      sdepth = oldsdepth,
                      maxbarley = maxbarley,
                      fieldsperhectare = fieldsperhectare),
                      quiet = True)


        # Create the desired cereal mix
        tempcerealreturn = "%stemporary_cereal_yields_map" %pid
        e = '''${tempcerealreturn} = if(isnull(${agcatch}), null(), (((1-${agmix})*${tempwheatreturn})+(${agmix}*${tempbarleyreturn})) )'''
        grass.mapcalc(e, quiet = True,
                      tempcerealreturn = tempcerealreturn,
                      agmix = agmix, tempwheatreturn = tempwheatreturn,
                      tempbarleyreturn = tempbarleyreturn,
                      agcatch = agcatch)

        grass.message("Figuring out the farming plan for this year...")

        # Gather some stats from yields maps in order to make an estimate of
        # number of farm plots...
        cerealstats2 = grass.parse_command('r.univar', flags = 'ge', map = tempcerealreturn)

        # Grab the agent's current memory of farming yields to see what they
        # think they need to do this year
        if len(farmyieldmemory) is 0:
            fuzzyyieldmemory = random.gauss(float(cerealstats2["mean"]), (float(cerealstats2['mean']) * 0.0333))
            fuzzydeficitmemory = -1
        else:
            if agentmem > (m - 1):
                slicer = m - 1
            else:
                slicer = agentmem
            grass.debug("slicer: %s" % slicer)
            fuzzyyieldmemory = numpy.mean(farmyieldmemory[slicer:])
            fuzzydeficitmemory = numpy.mean(farmingmemory[slicer:])

            grass.debug("farmyieldmemory: %s" % farmyieldmemory)
            grass.debug("fuzzyyieldmemory: %s" % fuzzyyieldmemory)
            grass.debug("farmingmemory: %s" % farmingmemory)
            grass.debug("fuzzydeficitmemory: %s" % fuzzydeficitmemory)

        # Figure out how many fields the agent thinks it needs based on current
        # average yield
        numfields = int(round(float(cerealreq) / fuzzyyieldmemory))
        grass.debug("total fields should be %s" % numfields)

        # Discover how many cells to add or subtract based on agent memory of
        # surplus or deficit
        fieldpad = int(round(fuzzydeficitmemory / fuzzyyieldmemory))
        grass.debug("fieldpad (sign reversed) %s" % fieldpad)

        # Add or remove the number of extra cells calculated from agent memory
        # surplus or deficit
        numfields = numfields - fieldpad
        grass.debug("did numfields change? %s" % numfields)

        # Then, make sure we don't exceed our catchment size or labor capacity
        # (and reduce number of fields if necessary)
        if numfields > int(round((float(cerealstats2['cells']) - float(cerealstats2["null_cells"])))):
            numfields = int(round((float(cerealstats2['cells']) - float(cerealstats2["null_cells"]))))
        if numfields > maxfields:
            numfields = maxfields
        grass.debug("did numfields hit the max and be curtailed? %s" % numfields)

        # Do landuse strategy method
        if m == 0:
            tenuredcells = numfields

        tenuredcells, droppedcells, newcells, tempfields = luStrategy(m, o, p, pid, tempfields, numfields, tenuredcells, droppedcells, tempcerealreturn)

        # Use r.surf.gaussian to cacluate fertily impacts in the farmed areas
        grass.run_command('r.surf.gauss', quiet = True,
                                          output = tempimpacta,
                                          mean = farmimpact[0],
                                          sigma = farmimpact[1])

        e = '''${fields} = if(isnull(${tempfields}), null(), ${tempimpacta})'''
        grass.mapcalc(e, quiet = True,
                      fields = fields,
                      tempfields = tempfields,
                      tempimpacta = tempimpacta)

        # Grab some yieled stats while region is still aligned to desired
        # field size. First make a temporary "zone" map for the farmed areas
        # in which to run r.univar
        tempfarmzone = "%stemporary_farming_zones_map" % pid
        e = '''${tempfarmzone}=if(isnull(${fields}), null(), ${tempcerealreturn})'''
        grass.mapcalc(e, quiet = True,
                      tempfarmzone = tempfarmzone,
                      fields = fields,
                      tempcerealreturn = tempcerealreturn)

        # Now use this zone map to grab some stats about the actual yields for
        # this year's farmed fields
        cerealstats = grass.parse_command('r.univar', flags = 'ge', percentile = '90', map = tempfarmzone)

        # Calculate some useful stats
        cerealdif    = float(cerealstats['sum']) - float(cerealreq)
        numfarmcells = int(float(cerealstats['cells']) - float(cerealstats['null_cells']))
        areafarmed   = numfarmcells * float(nsfieldsize) * float(ewfieldsize)

        # Update agent mempory with the farming surplus or deficit from this
        # year, fuzzing up the means a bit to simulate the vagaries of memory.
        # We do this by changing the actual values of these things by
        # randomizing them through a gaussian probability filter with mu of
        # the mean value and sigma of 0.0333. This means that the value they
        # actually remember can be up to +- %10 of the actual mean value
        # (eg. at the 3-sigma level of a gaussian distribution with sigma
        # of 0.0333), although they have a better change of remembering values
        # closer to the actual average. This more closely models how good
        # people are at "educated guesses" of central tendencies (i.e., it's
        # how people "guesstimate" the "average" value). This also ensures
        # some variation from year to year, regardless of the "optimum" solution.
        farmingmemory.append(random.gauss(float(cerealdif), (float(cerealdif) * 0.0333)))
        farmyieldmemory.append(random.gauss(float(cerealstats["mean"]), (float(cerealstats['mean']) * 0.0333)))

        # Find out the percentage of agcatch that was farmed this year.
        basepercent = 100 * (numfarmcells / (float(cerealstats2['cells']) - float(cerealstats2["null_cells"]) ) )
        if basepercent > 100:
            agpercent = 100.00
        else:
            agpercent = basepercent

        # Reset region to original resolution
        grass.del_temp_region()
        grass.message('We farmed %s fields, using %.2f percent of agcatch...' % (numfarmcells,agpercent))

        #GENERATE GRAZING IMPACTS
        grass.message("Calculating potential grazing yields")

        #generate basic impact values
        tempimpactg = "%stemporary_grazing_impact" % pid
        rrs = grass.start_command("r.random.surface", quiet = True,
                                              output = tempimpactg,
                                              distance = grazespatial,
                                              exponent = grazepatchy,
                                              high = maxgrazeimpact)

        # Calculate temporary grazing yield map in kg/ha
        tempgrazereturnha = "%stemporary_hectares_grazing_returns_map" % pid
        tempgrazereturn = "%stemporary_grazing_returns_map" % pid
        rr = grass.start_command('r.recode', quiet = True,
                                      flags = 'da',
                                      input = oldlcov,
                                      output = tempgrazereturnha,
                                      rules = fodder_rules)

        rrs.wait(), rr.wait()

        # Convert to kg / cell, and adjust to impacts
        e = '''${tempgrazereturn} = (${tempgrazereturnha}/${cellperhectare}) * ${tempimpactg}'''
        grass.mapcalc(e, quiet = True,
                      tempgrazereturn = tempgrazereturn,
                      tempgrazereturnha = tempgrazereturnha,
                      cellperhectare = cellperhectare,
                      tempimpactg = tempimpactg)

        grass.message('Figuring out grazing plans for this year....')
        # Do we graze on the stubble of agricultural fields? If so, how much
        # fodder to we think we will get?
        if use_flags['g'] is False:
            # Temporarily set region to match the field size again
            grass.use_temp_region()
            grass.run_command('g.region', quiet = True,nsres = nsfieldsize, ewres = ewfieldsize)

            # Set up a map with the right values of stubble fodder in it, and get them to the right units (fodder per farm field)
            stubfod1 = "%stemporary_stubblefodder_1" % pid
            stubfod2 = "%stemporary_stubblefodder_2" % pid
            stubfod3 = "%stemporary_stubblefodder_3" % pid

            # Make map of the basic landcover value for fields (grass stubbles)
            e = '''${stubfod1}=if(${tempfarmzone}, ${farmval}, null())'''
            grass.mapcalc(e, quiet = True,
                          stubfod1 = stubfod1,
                          farmval = farmval,
                          tempfarmzone = tempfarmzone)

            # Turn that map into baseline grazing yields/ha for that landcover value
            grass.run_command('r.recode', quiet = True,
                                          flags = 'da',
                                          input = stubfod1,
                                          output = stubfod2,
                                          rules = fodder_rules)

            # Match the variability in stubble yields to that in cereal returns, and convert to yields per field
            e = '''${stubfod3} = (${stubfod2} / ${fieldsperhectare}) * (${tempcerealreturn}/${maxcereals})'''
            grass.mapcalc(e, quiet = True,
                          stubfod3 = stubfod3,
                          stubfod2 = stubfod2,
                          fieldsperhectare = fieldsperhectare,
                          tempcerealreturn = tempcerealreturn,
                          maxcereals = cerealstats['max'])

            stubblestats = grass.parse_command('r.univar', flags = 'ge', percentile = '90', map = stubfod3)

            # Since we grazed stubble, let's' estimate how much stubbles we got
            # by padding the mean value to a randomly generated percentage that
            # is drawn from a gaussian probability distribution with mu of the
            # mean value and sigma of 0.0333. This means that the absolute
            # max/min pad can only be up to +- %10 of the mean value (eg. at
            # the 3-sigma level of a gaussian distribution with sigma
            # of 0.0333), and that pad values closer to 0% will be more likely
            # than pad values close to +- 10%. This more closely models how
            # good people are at "educated guesses" of central tendencies
            # (i.e., it's how people "guesstimate" the "average" value). This
            # also ensures some variation from year to year, regardless of the
            # "optimum" solution. Once we've done that, do we think there's
            # still some remaining fodder needs to be grazed from wild patches?
            # If so, how much?
            if (float(fodderreq) - ( float(stubblestats['mean']) * numfarmcells )) < 0:
                remainingfodder = 0
            else:
                remainingfodder = float(fodderreq) - ( random.gauss(float(stubblestats['mean']), (float(stubblestats['mean']) * 0.0333)) * numfarmcells )

            #reset region
            grass.del_temp_region()
        else:
            stubblestats = {"mean": '0', "sum": "0", "cells": "0", "stddev": "0", "min": "0", "first_quartile": "0", "median": "0", "third_quartile": "0", "max": "0"}
            remainingfodder = float(fodderreq)

        # Do we graze on the "fallowed" portions of the agricultural catchment?
        tempgrazecatch = "%stemporary_grazing_catchment_map" % pid
        if use_flags['f'] is True:
            e = '''${tempgrazecatch} = if(isnull(${grazecatch}), null(), if(isnull(${agcatch}), ${tempgrazereturn}, null()))'''
            grass.mapcalc(e, quiet = True,
                          tempgrazecatch = tempgrazecatch,
                          grazecatch = grazecatch,
                          agcatch = agcatch,
                          tempgrazereturn = tempgrazereturn)
        else:
            e = '''${tempgrazecatch}=if(isnull(${grazecatch}), null(), if(isnull(${fields}), ${tempgrazereturn}, null()))'''
            grass.mapcalc(e, quiet = True,
                          tempgrazecatch = tempgrazecatch,
                          grazecatch = grazecatch,
                          fields = fields,
                          tempgrazereturn = tempgrazereturn)

        # Now that we know where we are allowed to graze, how much of the
        # grazing catchment does the agent think it needs to meet its remaining
        # fodder requirements? First grab some general stats from the grazing
        # catchment.
        fodderstats = grass.parse_command('r.univar', flags = 'ge', percentile = '90', map = tempgrazecatch)

        # Use the agent's memory of past grazing yields and deficits to
        # determine what they think they need to do this year.
        if len(grazeyieldmemory) is 0:
            # If it's the first year, then just use the fuzzed average
            # potential yield from all cells in agcatch, and make the padded
            # amount 1
            fuzzygyieldmemory = random.gauss(float(fodderstats['mean']), (float(fodderstats['mean']) * 0.0333))
            fuzzygdeficitmemory = -1
        else:
            fuzzygyieldmemory = numpy.mean(grazeyieldmemory[slicer:])
            fuzzygdeficitmemory = numpy.mean(grazingmemory[slicer:])

        # Figure out how many grazing patches the agent thinks it needs based
        # on current average patch yield
        numfoddercells = int(round(float(remainingfodder) / fuzzygyieldmemory))
        grass.debug("total graze patches should be %s" % numfoddercells)

        # Discover how many cells to add or subtract based on agent memory of
        # surplus or deficit
        fodderpad = int(round(fuzzygdeficitmemory / fuzzygyieldmemory))
        grass.debug("fodderpad (sign reversed) %s" % fodderpad)

        # Add or remove the number of extra cells calculated from agent memory
        # surplus or deficit
        numfoddercells = numfoddercells - fodderpad
        grass.debug("did numfoddercells change? %s" % numfoddercells)

        # Check if we need more cells than are in the maximum grazing catchment,
        # and clip to that catchment if so
        totgrazecells = int(float(fodderstats['cells'])) - int(float(fodderstats['null_cells']))
        grass.debug("did we have to clip numfoddercells to the catchment size? %s" % numfoddercells)

        # Make the actual grazing impacts map
        if numfoddercells > totgrazecells:
            celltarget = totgrazecells
            e = '''${grazeimpacts}=if(isnull(${tempgrazecatch}), null(), if(${oldlcov} <= ${mingraze}, null(), ${tempimpactg}))'''
            grass.mapcalc(e, quiet = True,
                          grazeimpacts = grazeimpacts,
                          tempimpactg = tempimpactg,
                          tempgrazecatch = tempgrazecatch,
                          oldlcov = oldlcov,
                          mingraze = mingraze)

        elif numfoddercells == 0:
            grass.mapcalc("${grazeimpacts}=null()", quiet = True, grazeimpacts = grazeimpacts)
        else:
            celltarget = numfoddercells

            # Now clip the cost surface to the grazable area (including cells
            # with vegetation too low to graze on), and iterate through it to
            # figure out the actual grazing area to be used this year
            tempgrazecost = "%stemporary_grazing_cost_map" % pid

            e = '''${tempgrazecost}=if(isnull(${tempgrazecatch}), null(),if(${oldlcov} <= ${mingraze}, null(), ${costsurf}))'''
            grass.mapcalc(e, quiet = True,
                          tempgrazecatch = tempgrazecatch,
                          tempgrazecost = tempgrazecost,
                          costsurf = costsurf,
                          oldlcov = oldlcov,
                          mingraze = mingraze)

            catchstat = [float(x) for x in grass.read_command("r.stats", quiet = True, flags = "1n", input = tempgrazecost, separator="=", nsteps = "10000").splitlines()]
            target = 0
            cutoff = []
            for x in sorted(catchstat):
                target = target +  1
                cutoff.append(x)
                if target >= celltarget:
                    break
            try:
                # Make the actual grazing impacts map
                e = '''${grazeimpacts}=if(${tempgrazecost} > ${cutoff}, null(), ${tempimpactg})'''
                grass.mapcalc(e, quiet = True,
                              grazeimpacts = grazeimpacts,
                              tempimpactg = tempimpactg,
                              tempgrazecost = tempgrazecost,
                              cutoff = cutoff[-1])

            except:
                grass.fatal("Uh oh! Somethng wierd happened when figuring out this year\'s grazing catchment! Check your numbers and try again! Sorry!")
                sys.exit(1)

        # Now get some grazing yields stats
        # Check if stubble grazing got us everything we wanted, and act appropriately
        if numfoddercells == 0:
            grazestats = {"mean": '0', "sum": "0", "cells": "0", "stddev": "0", "min": "0", "first_quartile": "0", "median": "0", "third_quartile": "0", "max": "0"}
            totalfodder = float(stubblestats['sum'])
            grazepercent = 0
            fodderdif = totalfodder - float(fodderreq)
            areagrazed = 0
        else:
            # First make a temporary "zone" map for the grazed areas in which to run r.univar
            tempgrazezone = "%stemporary_grazing_zones_map" % pid

            e = '''${tempgrazezone}=if(isnull(${grazeimpacts}), null(), ${tempgrazereturn})'''
            grass.mapcalc(e, quiet = True,
                          tempgrazezone = tempgrazezone,
                          grazeimpacts = grazeimpacts,
                          tempgrazereturn = tempgrazereturn)

            # Now grab the univar stats with this zone file
            grazestats = grass.parse_command('r.univar', flags = 'ge', percentile = '90', map = tempgrazezone)
            numgrazecells = (float(grazestats['cells']) - float(grazestats["null_cells"]) )
            totalfodder = float(grazestats['sum']) + float(stubblestats['sum'])
            grazepercent = 100 * (numgrazecells / totgrazecells)
            fodderdif =  totalfodder - float(fodderreq)
            areagrazed = numgrazecells * (float(region['nsres']) * float(region['ewres']))

        # Update agent mempory with the grazing surplus or deficit from this
        # year, fuzzing up the means a bit to simulate the vagaries of memory.
        # We do this by changing the actual values of these things by
        # randomizing them through a gaussian probability filter with mu of
        # the mean value and sigma of 0.0333. This means that the value they
        # actually remember can be up to +- %10 of the actual mean value (eg.
        # at the 3-sigma level of a gaussian distribution with sigma of 0.0333),
        # although they have a better change of remembering values closer to
        # the actual average. This more closely models how good people are at
        # "educated guesses" of central tendencies (i.e., it's how people
        # "guesstimate" the "average" value). This also ensures some variation
        # from year to year, regardless of the "optimum" solution.
        grazingmemory.append(random.gauss(float(fodderdif), (float(fodderdif) * 0.0333)))
        grazeyieldmemory.append(random.gauss(float(grazestats['mean']), (float(grazestats['mean']) * 0.0333)))
        grass.message('We got %.2f kg of fodder from stubbles, and so we grazed %.2f percent of grazecatch this year.' % (float(stubblestats['sum']),grazepercent))

        # Figure out how many animals and people were fed
        animfed = (totalfodder / indfodreq)
        peoplefed = ((float(cerealstats['sum']) / indcerreq) + (animfed / animals))
        grass.message('We fed %i herd animals, and produced enough food to fully support %i people this year (current population: %i)...' %(animfed, peoplefed, numpeople))

        # If the -p flag was checked, update population levels based on returns.
        if use_flags['p'] is True:
            if peoplefed / numpeople < starvthresh:     #Check if they starved this year and just die deaths if so
                numpeople = numpeople - deathdealer(deathrate, numpeople)
                grass.message("Starved a bit this year, no births will occur. New population: %i" % numpeople)
            else: #otherwise, balance births and deaths, and adjust the population accordingly
                numpeople = numpeople + babymaker(birthrate, numpeople) - deathdealer(deathrate, numpeople)
                grass.message("Balancing births and deaths... New population: %i" % numpeople)
            # Update labor and yeild needs
            cereal_pers = numpeople * agratio
            fodder_anim = animals * numpeople * pratio
            cerealreq = indcerreq * cereal_pers
            fodderreq = indfodreq * fodder_anim
            totlabor = numpeople * aglabor
            maxfields = int(round(totlabor / fieldlabor))

        # Calculate natural (lightning-caused) fire ignition on the landscape
        # by parsing fire probability map into three with mapcalc:

#WHY NOT USE ORIGINAL PROBABILITIES???
        if len(fireprob) > 0:
            lowprobmap = "%stemp_fireprob_low" % pid
            medprobmap = "%stemp_fireprob_med" % pid
            hiprobmap = "%stemp_fireprob_hi" % pid
            # Hardcoding cutoffs for no, low, medium, high probability based on histogram of spanish fire probability map.
            e = b'''${lowprobmap} = if(${fireprob} <= 0.2, 1, null())'''
            lpm = grass.mapcalc_start(e, quiet = "True",
                          fireprob=fireprob,
                          lowprobmap=lowprobmap)

            e = b'''${medprobmap} = if(${fireprob} > 0.2 || ${fireprob} <= 0.6, 1, null())'''
            mpm = grass.mapcalc_start(e, quiet = True,
                          fireprob=fireprob,
                          medprobmap=medprobmap)

            e = b'''${hiprobmap}=if(${fireprob} > 0.6, 1, null())'''
            hpm = grass.mapcalc_start(e, quiet = True,
                          fireprob=fireprob,
                          hiprobmap=hiprobmap)

            lpm.wait(), mpm.wait(), hpm.wait()

            # Randomly sample each of these maps at different densities (find out actual densities from Grant):
            fires1 = "%sfires_low" % pid
            fires2 = "%sfires_med" % pid
            fires3 = "%sfires_hi" % pid

            lpp = grass.start_command('r.random', quiet = 'True', input=lowprobmap, raster=fires1, npoints="5%")
            mpp = grass.start_command('r.random', quiet = 'True', input=medprobmap, raster=fires2, npoints="10%")
            hpp = grass.start_command('r.random', quiet = 'True', input=hiprobmap, raster=fires3, npoints="15%")

            lpp.wait(), mpp.wait(), hpmpwait()

            # Patch those back to make final map of fire locations
            grass.run_command('r.patch', input="%s,%s,%s" % (fires1,fires2,fires3), output=natural_fires)
            # Grab some fire stats
            firestats = grass.parse_command('r.univar', flags = 'ge', percentile = '90', map = natural_fires)

        # Write the yield stats to the stats file
        grass.message('Writing some farming and grazing stats from this year....')
        f = open(textout3, 'a')
        if os.path.getsize(textout3) == 0:
            f.write("Year,Effective carrying capacity,Population,Percent of Agricultural Catchment Used,Number of Farm Fields,Number of Tenured Fields,Number of Dropped Fields,Number of New Fields,Total Farmed Area (m2),Agent Memory of Per Field Harvest Mean,Per Field Harvest Mean,Per Field Harvest Standard Deviation,Total Cereals Harvested,Total Cereals Required,Cereal Surplus/Deficit,Agent Memory of Cereal Surplus/Deficit,,Herd Animals Fed,Percent of Grazing Catchment Used,Total Grazed Area (m2),Agent Memory of Wild Grazing Patch Mean,Wild Grazing Patch Mean,Wild Grazing Patch Standard Deviation,Total Wild Fodder,Field Stubbles Mean,Field Stubbles Standard Deviation,Total Stubble Fodder,Total Fodder Consumed,Total Amount of Fodder Required,Fodder Surplus/Deficit,,,Minimum Cereals,First Quartile Cereals,Third Quartile Cereals,Maximum Cereals,,Minimum Wild Fodder,First Quartile Wild Fodder,Third Quartile Wild Fodder,Maximum Wild Fodder,,Minimum Stubble Fodder,Stubble Quartile Stubble Fodder,Third Quartile Stubble Fodder,Maximum Stubble Fodder") # the file is empty, so write the headers on the first line.
        f.write('\n%s' % o + ',' + str(peoplefed) + ',' + str(numpeople) + ',' + str(agpercent) + ',' + str(numfarmcells) + ',' + str(tenuredcells) + ',' + str(droppedcells) + ',' + str(newcells) + ',' + str(areafarmed) + ',' + str(fuzzyyieldmemory) + ',' + cerealstats['mean'] + ',' + cerealstats['stddev'] + ',' + cerealstats['sum'] + ',' + str(cerealreq) + ',' + str(cerealdif) + ',' + str(fuzzydeficitmemory) + ',,' + str(animfed) + ',' + str(grazepercent) + ',' + str(areagrazed) + ',' + str(fuzzygyieldmemory) + ',' + grazestats['mean'] + ',' + grazestats['stddev'] + ',' + grazestats['sum'] + ',' + stubblestats['mean'] + ',' + stubblestats['stddev'] + ',' + stubblestats['sum'] + ',' + str(totalfodder) + ',' + str(fodderreq) + ',' + str(fodderdif) + ',,,' + cerealstats['min'] + ',' + cerealstats['first_quartile'] + ',' + cerealstats['first_quartile'] + ',' + cerealstats['max'] + ',,' + grazestats['min'] + ',' + grazestats['first_quartile'] + ',' + grazestats['third_quartile'] + ',' + grazestats['max'] + ',,' + stubblestats['min'] + ',' + stubblestats['first_quartile'] + ',' + stubblestats['third_quartile'] + ',' + stubblestats['max']) # update this year's row with the data from this year's simulation

        # UPDATE LANDCOVER AND SOIL FERTILITY
        grass.message('Updating landcover and soil fertility with new impacts')

        # Update fertility
        tempfertil = "%stemporary_fertility_regain_map" % pid

        # Use r.surf.gaussian to cacluate fertily regain map
        grass.run_command('r.surf.gauss', quiet = True, output = tempfertil, mean = fertilrate[0], sigma = fertilrate[1])

        # Figure out what happened to fertility (see if stubble-grazing is enabled, and make sure to add some manure where grazing occured, scaled to the degree of graing that happened)
        if use_flags['g'] is False:
            e = '''${outfert} = eval(a = if(isnull(${grazeimpacts}) && isnull(${fields}), ${tempfertil}, ${tempfertil} + (${manurerate} * ${tempimpactg})), \
                                     b = if(isnull(${fields}), ${oldfert}, ${oldfert} - ${fields}), \
                                     c = if(b <= ${maxfert} - a, b + a, ${maxfert}), if(c < 0, 0, c))'''
            grass.mapcalc(e, quiet = True,
                          outfert = outfert,
                          oldfert = oldfert,
                          fields = fields,
                          tempimpactg = tempimpactg,
                          grazeimpacts = grazeimpacts,
                          manurerate = manurerate,
                          maxfert = maxfert,
                          tempfertil = tempfertil)

        else:
            e = '''${outfert} = eval(a = if(isnull(${grazeimpacts}), ${tempfertil}, ${tempfertil} + (${manurerate} * ${tempimpactg})), \
                                     b = if(isnull(${fields}), ${oldfert}, ${oldfert} - ${fields}), \
                                     if(b <= ${maxfert} - a, b + a, ${maxfert}))'''
            grass.mapcalc(e, quiet = True,
                          outfert = outfert,
                          oldfert = oldfert,
                          fields = fields,
                          tempimpactg =
                          tempimpactg,
                          grazeimpacts = grazeimpacts,
                          manurerate = manurerate,
                          maxfert = maxfert,
                          tempfertil = tempfertil)

        fertcolors = ['0 white', '20 grey', '40 yellow', '60 orange', '80 brown', '100 black']
        grass.write_command('r.colors', quiet = True, map = outfert, rules = "-", stdin='\n'.join(fertcolors))

        # Update landcover
        # Calculating rate of regrowth based on current soil fertility, spil depths, and precipitation. Recoding fertility (0 to 100%), depth (0 to >= 1m), and precip (0 to >= 1000mm) with a power regression curve from 0 to 1, then taking the mean of the two as the regrowth rate
        growthrate = "%stemporary_vegetation_regrowth_map" % pid

        e = '''${growthrate} = eval(x = if(${sdepth} <= 1.0, (-0.000118528 * (exp((100*${sdepth}),2.0))) + (0.0215056 * (100*${sdepth})) + 0.0237987, 1), \
                                    y = if(${precip} <= 1.0, ( -0.000118528 * (exp((100*${precip}),2.0))) + (0.0215056 * (100*${precip})) + 0.0237987, 1), \
                                    z = (-0.000118528 * (exp(${outfert},2.0))) + (0.0215056 * ${outfert}) + 0.0237987, \
                                    a = if(x <= 0 || z <= 0, 0, (x+y+z)/3), if(a < 0, 0, a) )'''
        grass.mapcalc(e, quiet = True,
                      growthrate = growthrate,
                      sdepth = oldsdepth,
                      outfert = outfert,
                      precip = precip)

        # Calculate this year's landcover impacts and regrowth
        e = '''${outlcov} = eval(a = if(${oldlcov} - ${grazeimpacts} + ${growthrate} >= 0, ${oldlcov} - ${grazeimpacts} + ${growthrate}, 0) , \
                                 b = if(isnull(${fields}), a, ${farmval}), \
                                 if(${oldlcov} < (${maxlcov} - ${growthrate}) && isnull(b), ${oldlcov} + ${growthrate}, if(isnull(b), ${maxlcov}, b) ))'''
        grass.mapcalc(e, quiet = True,
                      outlcov = outlcov,
                      oldlcov = oldlcov,
                      maxlcov = maxlcov,
                      growthrate = growthrate,
                      fields = fields,
                      farmval = farmval,
                      grazeimpacts = grazeimpacts)

        if len(fireprob) > 0:
            #If there was a fire, vegetation goes to 0 no matter what was there.
            e = '''${outlcov} = if(isnull(${natural_fires}), ${outlcov}, 0)'''
            grass.mapcalc(e, quiet = "True", overwrite = True,
                          outlcov = outlcov,
                          natural_fires = natural_fires)

        # Make a rainfall excess map to send to r.landcape.evol. This is a
        # logarithmic regression (R^2=0.99.) for the data
        # pairs: 0,90;3,85;8,70;13,60;19,45;38,30;50,20. These are the same
        # succession cutoffs that are used in the c-factor coding.
        e = '''${outxs} = 193.522 - (42.3272 * log(${lcov} + 10.9718))'''
        grass.mapcalc(e, quiet = True,
                      outxs = outxs,
                      lcov = outlcov)

        # If rules set exists, create reclassed landcover labels map
        try:
#SEEMS LIKE THERE SHOULD BE A BETTER WAY TO DO THIS

            temp_reclass = "%stemporary_reclassed_landcover" %pid
            grass.run_command('r.reclass', quiet = True,
                                           input = outlcov,
                                           output = temp_reclass,
                                           rules = lc_rules)

            grass.mapcalc('${out} = ${input}', quiet = True,
                                             overwrite = True,
                                             out = outlcov,
                                             input = temp_reclass)
        except:
            grass.warning("No landcover labling rules found at path \"%s\"\nOutput landcover map will not have text labels in queries" % lc_rules)

        lccolors = ['0 grey', '10 red', '20 orange', '30 brown', '40 yellow', '%s green' % maxval]
        grass.write_command('r.colors', quiet = True, map = outlcov, rules = "-", stdin='\n'.join(lccolors))

        # Collect and write landcover and fertiltiy temporal matrices
        grass.message('Collecting some landcover and fertility stats from this year....')
        f = open(textout, 'a')
        if os.path.getsize(textout) == 0:
            f.write("Temporal Matrix of Landcover\n\nYear," + ",".join(str(i) for i in range(maxval + 1)) + "\n")
        statdict = grass.parse_command('r.stats', quiet = True,  flags = 'ani', input = outlcov, separator = '=', nv ='*')
        f.write("%s," % o)
        for key in range(maxval + 1):
            try:
                f.write(statdict[str(key)] + "," )
            except:
                f.write("0,")
        f.write("\n")
        f.close()

        f = open(textout2, 'a')
        if os.path.getsize(textout2) == 0:
            f.write("Temporal Matrix of Soil Fertility\n\nYear," + ",".join(str(i) for i in range(maxfertval + 1)) + "\n")
        statdict = grass.parse_command('r.stats', quiet = True,  flags = 'ani', input = outfert, separator = '=', nv ='*')
        f.write("%s," % o)
        for key in range(maxfertval + 1):
            try:
                f.write(statdict[str(key)] + "," )
            except:
                f.write("0,")
        f.write("\n")
        f.close()

        # Collect and write univariate stats
        e = '''MASK = if(isnull(${grazecatch}), null(), 1)'''
        grass.mapcalc(e, quiet = True,
                      overwrite = True,
                      grazecatch = grazecatch)

        lcovstats = grass.parse_command('r.univar', flags = 'ge', percentile = '90', map = outlcov)

        grass.run_command('g.remove', quiet = True, flags = "f", type = "rast", name = "MASK")

        e = '''MASK = if(isnull(${agcatch}), null(), 1)'''
        grass.mapcalc(e, quiet = True,
                      overwrite = True,
                      agcatch = agcatch)

        fertstats = grass.parse_command('r.univar', flags = 'ge', percentile = '90', map = outfert)

        grass.run_command('g.remove', quiet = True, flags = "f", type = "rast", name = "MASK")

        f = open(textout4, 'a')
        if len(fireprob) > 0:
            if os.path.getsize(textout4) == 0:
                f.write("Landcover, Fire, and Soil Fertility Stats\nNote that Land cover stats are collected within the grazing catchment and fertility stats in the agricultural catchment (fertility) ONLY. Fire stats are collected across the whole map. \n\n,,Basic Stats,,,,Extended Stats\nYear,,Mean Landcover,Standard Deviation Landcover,Mean Soil Fertility,Standard Deviation Soil Fertility,,Minimum Landcover,First Quartile Landcover,Median Landcover,Third Quartile Landcover,Maximum Landcover,,Minimum Soil Fertility,First Quartile Soil Fertility,Median Soil Fertility,Third Quartile Soil Fertility,Maximum Soil Fertility")
            f.write('\n%s' % now + ',,' + lcovstats['mean'] + ',' + firestats['stddev'] + ',,' + firestats['mean'] + ',' + firestats['stddev'] + ',' + fertstats['mean'] + ',' + fertstats['stddev'] + ',,' + lcovstats['max'] + ',' + lcovstats['third_quartile'] + ',' + lcovstats['median'] + ',' + lcovstats['first_quartile'] + ',' + lcovstats['min'] + ',,' + fertstats['min'] + ',' + fertstats['first_quartile'] + ',' + fertstats['median'] + ',' + fertstats['third_quartile'] + ',' + fertstats['max'])
        else:
            if os.path.getsize(textout4) == 0:
                f.write("Landcover and Soil Fertility Stats\nNote that these stats are collected within the grazing catchment (landcover) and agricultural catchment (fertility) ONLY. Rest of the map is ignored.\n\n,,Basic Stats,,,,Extended Stats\nYear,,Mean Landcover,Standard Deviation Landcover,Mean Soil Fertility,Standard Deviation Soil Fertility,,Minimum Landcover,First Quartile Landcover,Median Landcover,Third Quartile Landcover,Maximum Landcover,,Minimum Soil Fertility,First Quartile Soil Fertility,Median Soil Fertility,Third Quartile Soil Fertility,Maximum Soil Fertility")
            f.write('\n%s' % o + ',,' + lcovstats['mean'] + ',' + lcovstats['stddev'] + ',' + fertstats['mean'] + ',' + fertstats['stddev'] + ',,' + lcovstats['max'] + ',' + lcovstats['third_quartile'] + ',' + lcovstats['median'] + ',' + lcovstats['first_quartile'] + ',' + lcovstats['min'] + ',,' + fertstats['min'] + ',' + fertstats['first_quartile'] + ',' + fertstats['median'] + ',' + fertstats['third_quartile'] + ',' + fertstats['max'])

        # Creating c-factor map
        grass.message('Creating C-factor map for r.landscape.evol')
        try:
            grass.run_command('r.recode', quiet = True, input = outlcov, output = outcfact, rules = cfact_rules)
        except:
            grass.fatal("NO CFACTOR RECLASS RULES WERE FOUND AT PATH \"%s\"\nPLEASE ENSURE THAT THE CFACTOR RECODE RULES EXIST AND ARE WRITTEN PROPERLY, AND THEN TRY AGAIN" % cfact_rules)
            sys.exit(1)

        cfcolors = ['0.1 grey', '0.05 red', '0.03 orange', '0.01 brown', '0.008 yellow', '0.005 green']
        grass.write_command('r.colors', quiet = True, map = outcfact, rules = "-", stdin='\n'.join(cfcolors))

        # Run r.landscape.evol with this years' cfactor map
        landEvolve(m, outcfact, outxs, r, rain, storms, stormlength, statsout, levol_flags)

        #clean up temporary maps
        #delete C-factor map, unless asked to save it
        if use_flags['c'] is False:
            grass.run_command("g.remove", quiet = True, flags = 'f', type = "rast", name = "%s,%s" %  (outcfact,outxs))
        else:
            pass
        grass.run_command('g.remove', quiet = True, flags = 'f', type = "rast", pattern = '%s*' % pid)
        grass.message('Completed year %s of the simulation' % o)

    return(grass.message(".........................SIMULATION COMPLETE...........................\nCheck in the current mapset for farming/grazing yields, landcover, fertility, and erosion/depostion stats files from this run."))


#GIVE VARIABLE tenuretype A DIFFERENT NAME LIKE USESTRATEGY OR SOMETHING?

def luStrategy(m, o, p, pid, tempfields, numfields, tenuredcells, droppedcells, tempcerealreturn):
    # Check for tenure, and do the appropriate type of tenure if asked
    tenuretype = options["tenuretype"]
    tenuredrop = options["tenuredrop"]
    agcatch    = options["agcatch"]

    if m == 0:
        grass.run_command('r.random', quiet = True, input = agcatch, npoints = numfields, raster = tempfields)
        grass.message('First year, so %s fields randomly assigned' % numfields)
        droppedcells = 0
        newcells = 0
    else:
        # Make some map names
        oldfields = "%sFarming_Impacts_Map%04d" % (p, m)
        tenuredfields = "%sTenured_Fields_Map%04d" % (p, o)
        tempcomparefields = "%stemporary_Old_Fields_yield_map" % pid
        tempagcatch = "%stemporary_agricultural_catchment_map" % pid
        grass.message('Performing yearly land tenure evaluation')

        # Make a map of the current potential yields from the old fields
        e = '''${tempcomparefields} = if(isnull(${oldfields}), null(), ${tempcerealreturn} )'''
        grass.mapcalc(e, quiet = True,
                      tempcomparefields = tempcomparefields,
                      oldfields = oldfields,
                      tempcerealreturn = tempcerealreturn)

        # Grab stats from the old fields
        oldfieldstats = grass.parse_command('r.univar', flags = 'ge', map = tempcomparefields)

    if tenuretype == "Maximize":
        grass.message("Land Tenure is ON, with MAXIMIZING strategy")

        # Check for first year, and zero out tenure if so
        if m == 0:
            tenuredfields = "%sTenured_Fields_Map%04d" % (p, o)
            grass.run_command('g.copy', quiet = True, raster = "%s,%s" % (tempfields,tenuredfields))
        else:
            # Make some map names
            oldtenure = "%sTenured_Fields_Map%04d" % (p, m)

            # # TODO: temporarily update the agricultural catchment by withholding last year's fields. All other cells in the catchment will be fair game to be chosen for the new fields.
            e = '''${tempagcatch} = if(isnull(${agcatch}), null(), if(isnull(${oldfields}), ${agcatch}, null() ))'''
            grass.mapcalc(e, quiet = True,
                          tempagcatch = tempagcatch,
                          agcatch = agcatch,
                          oldfields = oldfields)

            newcells = numfields-tenuredcells #find out the difference between what we have and what we need
            if newcells <= 0: #negative number, so we drop any underperforming fields)
                # Check the comparison metric and drop underperforming
                # fields compared to average yield...
                if tenuredrop == 0: #drop threshold is 0, so compare to mean yield of all fields
                    e = '''${tenuredfields} = if(${tempcomparefields} < (${meanyield}), null(), 1)'''
                    grass.mapcalc(e, quiet = True,
                                  tenuredfields=tenuredfields,
                                  tempcomparefields = tempcomparefields,
                                  meanyield = oldfieldstats['mean'])

                else: # Drop threshold is above zero, so use it to compare
                      # to the maximum yeild.
                    e = '''${tenuredfields} = if(${tempcomparefields} < ${maxyield}-(${maxyield}*${tenuredrop}), null(), 1)'''
                    grass.mapcalc(e, quiet = True,
                                  tenuredfields=tenuredfields,
                                  tempcomparefields = tempcomparefields,
                                  maxyield = oldfieldstats['max'],
                                  tenuredrop = tenuredrop)

                # Pull stats out to see what we did (how many old fields
                # kept, how many dropped, and how many new ones we need
                # this year
                tenuredstats = grass.parse_command('r.univar', flags = 'ge', map = tenuredfields)
                tenuredcells = int(float(tenuredstats['cells']) - float(tenuredstats['null_cells']))
                droppedcells = int(float(oldfieldstats['cells']) - float(oldfieldstats['null_cells'])) - tenuredcells
                tempfields = tenuredfields
                grass.message("Keeping %s fields in tenure list, dropping %s underperforming fields" % (tenuredcells, droppedcells))

            else: #positive number, so add fields
                # Copy last year's fields forward as tenured
                e = '''${tenuredfields} = if(isnull(${oldfields}), null(), 1)'''
                grass.mapcalc(e, quiet = True,
                              oldfields = oldfields,
                              tenuredfields = tenuredfields)

                tenuredstats = grass.parse_command('r.univar', flags = 'ge', map = oldtenure)
                tenuredcells = int(float(tenuredstats['cells']) - float(tenuredstats['null_cells']))

                # Now run r.random to get the required number of additional fields
                tempfields1 = "%stemporary_extra_fields_map" % pid
                grass.run_command('r.random', quiet = True, input = tempagcatch, npoints = newcells, raster = tempfields1)

                # Patch the new fields into the old fields
                grass.run_command('r.patch', quiet = True, input = "%s,%s" % (tempfields1,oldtenure), output = tempfields)
                grass.message("Keeping %s fields in tenure list, adding %s new fields" % (tenuredcells, newcells))

    elif tenuretype == "Satisfice":
        grass.message("Land Tenure is ON, with SATSFICING strategy")

        # Make map of tenured fields for this year
        e = '''${tenuredfields}=if(isnull(${oldfields}), null(), 1)'''
        grass.mapcalc(e, quiet = True,
                      tenuredfields=tenuredfields,
                      oldfields = oldfields)

        # Temporarily update the agricultural catchment by withholding
        # tenured cells. All other cells in the catchment will be fair game
        # to be chosen for the new fields.
        e = '''${tempagcatch} = if(isnull(${agcatch}), null(), if(isnull(${tenuredfields}), ${agcatch}, null() ))'''
        grass.mapcalc(e, quiet = True,
                      tempagcatch = tempagcatch,
                      agcatch = agcatch,
                      tenuredfields = tenuredfields)

        # Pull stats out to see what we did (how many old fields kept, how
        # many dropped, and how many new ones we need this year
        tenuredstats = grass.parse_command('r.univar', flags = 'ge', map = tenuredfields)
        tenuredcells = int(float(tenuredstats['cells']) - float(tenuredstats['null_cells']))
        droppedcells = 0
        newcells = numfields-tenuredcells #find out the difference between what we have and what we need
        if newcells <= 0: #negative number, so we need to drop some fields.
            # Now run r.random to randomly select fields to drop
            tempfields1 = "%stemporary_dropped_fields_map" % pid
            grass.run_command('r.random', quiet = True, input = tenuredfields, npoints = 1-newcells, raster = tempfields1)

            # Remove the new fields from the tenured fields map
            grass.mapcalc("${tempfields}=if(isnull(${tenuredfields}), null(), if(isnull(${tempfields1}), 1, null()))", quiet = True, tempfields = tempfields, tempfields1 = tempfields1, tenuredfields = tenuredfields)
            grass.message("Dropping %s excess fields" % (1-newcells))

        else: #positive number, so add fields
            # Now run r.random to get the required number of additional fields
            tempfields1 = "%stemporary_extra_fields_map" % pid
            grass.run_command('r.random', quiet = True, input = tempagcatch, npoints = newcells, raster = tempfields1)

            # Patch the new fields into the old fields
            grass.run_command('r.patch', quiet = True, input = "%s,%s" % (tempfields1,tenuredfields), output = tempfields)
            grass.message("Adding %s new fields" % (newcells))
    else:
        grass.message("Land Tenure is OFF")
        tenuredcells = 0
        droppedcells = 0
        newcells = 0

        # Now run r.random to get the required number of fields
        grass.run_command('r.random', quiet = True, input = agcatch, npoints = numfields, raster = tempfields)

    return tenuredcells, droppedcells, newcells, tempfields

def landEvolve(m, outcfact, outxs, r, rain, storms, stormlength, statsout, levol_flags):
        p = options['prefx'] + "_"
        elev = options["elev"]
        initbdrk = options["initbdrk"]
        k = options["k"]
        sdensity = options["sdensity"]
        kappa = options["kappa"]
        manningn = options["manningn"]
        cutoff1 = options["cutoff1"]
        cutoff2 = options["cutoff2"]
        cutoff3 = options["cutoff3"]
        speed = options["speed"]
        kt = options["kt"]
        loadexp = options["loadexp"]
        smoothing = options["smoothing"]

        grass.message('Running landscape evolution for this year....')

        #check if this is year one, and use the starting dem if so
        if m == 0:
            inelev = elev
        else:
            inelev = "%sElevation_Map0001" % (p)

        try:
            cwd = os.getcwd()
            grass.run_command(os.path.join(cwd, 'r.landscape.evol2.py'), quiet = True, number = 1, prefx = options["prefx"], c = outcfact, elev = inelev, initbdrk = initbdrk, outdem = "Elevation_Map", outsoil = "Soil_Depth_Map", r = r, k = k, sdensity = sdensity, kappa = kappa, manningn = manningn, flowcontrib = outxs, cutoff1 = cutoff1, cutoff2 = cutoff2, cutoff3 = cutoff3, rain = rain, storms = storms, stormlength = stormlength, speed = speed, kt = kt, loadexp = loadexp, smoothing = smoothing, statsout = statsout, flags = ''.join(levol_flags))
        except:
            grass.fatal("Something is wrong with the values you sent to r.landscape.evol. Did you forget something? Check the values and try again...\nSimulation terminated with an error at time step %s" % o)
            sys.exit(1)


#Here is where the code in "main" actually gets executed. This way of programming is neccessary for the way g.parser needs to run.
if __name__ == "__main__":
    options, flags = grass.parser()
    main()
    # exit(0)
