# Foragers to Farmers (F2F) Agent Based Model

Michael Storozum, Elske van der Vaart, Tim Dorscheidt, Nicolas Gauthier

*The original model was developed by Elske van der Vaart, Bart de Boer, Albert Hankel, Bart Verheij (2006) in the Proceedings of the Ninth International Conference on the Simulation of Adaptive Behavior SAB '06, 750-762, later extended by Tim Dorscheidt (2012)*

The following document is the ODD for a replication of the model named ABscape, described in the Proceedings of the Ninth International Conference on the Simulation of Adaptive Behavior (van der Vaart et al. 2006). The model description follows the ODD protocol for describing individual and agent based models and consists of seven elements. The first three elements provide an overview of the model, the fourth element explains general concepts underlying the model's design, and the remaining three elements provide details. Additionally, details of the software implementation are presented.

## Contents

| 1. Purpose 2 |
| --- |
| 2. Entities, state variables and scales 2 |
| 2.1 Globals, agents, and patches 2 |
| 2.2 Agent Behavioral Rules 3 |
| 3. Process overview and scheduling 5 |
| 4. Model design concepts 7 |
| 5. Initialization 8 |
| 6. Inputs 10 |
| 6.1 Parameter values 10 |
| 7. Model implementation 10 |
| 8. References 11 |

## 1. Purpose

This model is represents an effort to replicate one of the first attempts to develop an agent based model of agricultural origins using principles and equations drawn from human behavioral ecology. We have taken one theory of habitat choice (Ideal Free Distribution) and applied it to human behavioral adaptations to differences in resource quality of different habitats.

## 2. Entities, state variables and scales

### 2.1 Globals, agents, and patches

*Globals.* There are over forty global variables in this model that serve various purposes. Please refer to the appendix at the end of the section for details on each variable. The majority of the global variables are derived from the human behavioral ecology literature to provide an empirical of the amount of time, energy, and growth each different agent (bands, prey, cereal, and farms) experiences per tick.

*Agents.* There are four agents in this simulation, bands of hunter gathers, prey animals, wild cereals, and farms (see Tables 1 and 2). The bands are mobile, whereas the prey animals, wild cereals, and farms are static, acting essentially as patches. Therefore, we will cover their function in the patches section.

The band agents in our simulation represent small bands of hunter-gatherers. Every band starts as a group of 20 people. Every time step, each of those 20 people has an 0.02 (2%) chance of reproducing, which is supposedly roughly characteristic of actual hunter-gatherers (Winterhalder et al. 1988). Once a band is made up of 40 individuals, it splits in two, each again representing 20 people. Every time step, the bands must forage 2000 kilocalories (Cal) for each of their group members, for each day of the year. Maximum foraging time is fixed at 14 hours per day. If there is shortfall, group size is scaled down to the number of people adequately fed. Foraging, however, also has costs; 4 Cal per minute (*cs*) spent searching for prey or cereal, and 6 Cal per minute (*ch*) spent catching or harvesting them (Winterhalder et al. 1988).

*Patches.* The scape consists of 21x21 patches, with each patch representing 300 square kilometers. The edges of the world are true edges as the world does not wrap. Based on estimates found in Cohen (1997), foragers can cover around 10 kilometers a day and still return to their base camp. Using this as a radius of action for each band, we calculate that bands have a home range of approximately 300 square kilometers (Winterhalder et al. 1988). This scape is divided into three habitats that are 7x21 patches each, termed the *'lush'*, *'medium'* and *'desert'* habitats, ordered from left to right in the scape and differentiated only by their carrying capacities for different food resources. Each of these different habitats has an upper limit for the carrying capacity for each of the different agent types.

### 2.2 Agent Behavioral Rules

In this section, we define the rules that guide the band agent behavior. The ideal free distribution is a model of habitat choice, which assumes that individuals populate habitats according to their marginal quality. The human agents thus need to have a sense of what makes a patch suitable, which depends on their dietary preferences. Also relevant is the range in which agents can evaluate patches, and what the costs and benefits are of food production.

The bands of hunter-gatherers have two dietary options, prey and cereal, which populate each patch. Each agent prefers prey, cereal, and then when resources are depleted, they will start farming.

The prey has characteristics inspired by large ungulates; the cereal is loosely based on wild barley. Here, energy value *(ei)* is the calories provided by a single prey or kilo of cereal; handle time *(hi)* is the total time required to catch, clean and cook a prey once spotted, or harvest, thresh and prepare a kilo of cereal gathered once located; carrying capacity *(Ci)* is the maximum prey or cereal population that can be supported by a square kilometer of patch and growth rate *(ri)* specifies the intrinsic rate of increase of each, where the index *i* specifies prey *p* or cereal *c*.

The prey values are calculated from anthropological data found in Winterhalder et al. (1988); the cereal characteristics represent ballpark figures, chosen as conscientiously as possible using data from (Flannery 1969, 1973, Harlan 1966).

Both prey and cereal grow according to Equation (1) taken from Winterhalder et al. 1988,

$$p_{i}(t+1) = p_{i}(t) \cdot \frac{C_{i} \cdot e^{r_{i}}}{C_{i} \cdot (1 - s_{i} \cdot t \cdot (1 - e^{r_{i}}))}$$
### *Equation 1*

where *pi(t)* is the population size of food type *i* at time step *t*, *Ci* is the maximum carrying capacity for food type *i* and *ri* is its intrinsic rate of increase. The equation is applied per patch. This results in cereal and prey slowly growing towards their carrying capacities, then stabilizing.

In principle, there is no influence of cereal and prey densities between patches, unless either cereal or prey completely disappears from a patch. In that case, each of its eight neighboring patches that does still have a viable population of the resource in question has a 10% chance of repopulating the depleted patch each year. A 'viable population' is either 100 prey or 400 kilos of cereal; these are also the initial population sizes of each for a repopulated patch.

*Search Times.* The catch times of prey and cereal are fixed; the search times for each depend on population density within a patch (Winterhalder et al. 1988). The rarer a food source has become, the longer it takes to locate. It is also dependent on the speed at which agents search (*ss*), and their search radius (*sr*) as they do so (i.e. 'How far can they see?'). Search times are then calculated using Equation (2),

$$s_{i}=\frac{1}{\left(s_{s}*s_{r}*2*d_{i}\right)}$$

*Equation 2*

where *si* is the search time for food type *i* and *di* its current population density.

*Net Acquisition Rates.* Now that we have specified the time it takes to catch (*hi*) and find (*si*) each type of food source, their respective energy values (*vp* and *vc*) and the energy costs incurred in obtaining them (*ch* and *cs*), we can calculate the 'net acquisition rates' (NAR) for each; that is, how much energy an agent gains for each hour spent hunting for prey or gathering cereal. The higher the net acquisition rate, the more efficient foraging for that food type is. The net acquisition rate of food source *i* at time *t* is then equal to the values in Table 3, as calculated per habitat. Equation 3 defines how NAR are calculated.

$$N A R_{i}={\frac{e_{i}}{(s_{i}+h_{i})}}-{\frac{s_{i}}{(s_{i}+h_{i})}}*c_{s}-{\frac{h_{i}}{(s_{i}+h_{i})}}*c_{h}$$

*Equation 3*

*Suitability & Dietary Preferences*. A patch's suitability may be measured by 'the production of young or rate of food intake' of the initial occupant (Winterhalder and Kennett 2006). Our agents rank patches by prey density first, cereal density second, reflecting the large percentage of meat found in most foragers' diets (Cordain et al. 2000), and the greater prestige associated with hunting over gathering as it is observed in most hunter-gatherer cultures. Once a patch has been selected, agents hunt prey and gather cereal in proportion to their net acquisition rates; as prey becomes scarcer relative to cereal, it is consumed less (see Equation (4)). Consumption of a food source stops if its net acquisition rate drops below zero.

$$p e r c e n t a e g o f f o o d s o u r c e i n d i e t={\frac{N A R_{i}}{\sum_{A l l f o d s o u r c e s j}N A R_{j}}}$$

#### *Equation 4*

*Range.* Every time step, each band starts in one patch, and may choose to move to another, which is always the most suitable patch it has knowledge of. This represents a small group of hunter-gatherers moving its base camp once a year. But which patches are considered to be 'in range'? Realistically, one might assume that these hunter-gatherers only have some sense of the area just outside their home range, and hence can only evaluate their own patch and the eight surrounding ones. However, one of the ideal free distribution's explicit assumptions is that '…all individuals have the information to select and the ability to settle in the most suitable habitat available' (McClure et al. 2006). This would be best modeled by each agent having perfect knowledge of the suitability of each other patch in the scape. In our

experiments, we try both options. Costs of moving are not considered, as ideal free distribution model assumes that those costs are '…negligible, when compared to the benefits of optimizing long-term habitat choice' (Kennett and Winterhalder 2006).

*Food Production.* Given that our simulation is intended to provide insights into behavioral ecology approaches to agricultural transitions, we must model some form of food production. Using Flannery 1969 and 1973 as sources, some educated guesswork allows us to derive the additional kilos a square hectare of cultivated cereal might yield (*ck + ,* where *ck* is the wild harvest), as well as the time it takes to produce a kilo of cereal by farming (*tf)* (Equations (5) & (6)), where *A* is the number of hectares of cereal that can be tended by working an hour daily. This is excluding harvest time, which is considered to be identical to that of wild cereal, as given by Table 1.

$$c_{k}^{+}=0.25*(1000-c_{k})(i n k i l o s/h e c t a r e)$$

#### *Equation 5*

$$t_{f}=\frac{1}{\left(h*\left(c_{k}+c_{k}^{+}\right)*365\right)}(i n h o u r s p e r k i l o)$$

#### *Equation 6*

If we assume that it takes approximately half an hour a day to tend a hectare of cereal, and that both tending and harvesting cereal are strenuous activities (Flannery 1973), costing 6 Cals of energy/minute (*ch*), we can then derive net acquisition rates for farming cereal in the three different habitats, as demonstrated by Table 3. This means that the efficiency of farming is independent of population density. The area which is suitable for agriculture is bounded, however, at 10% of each patch (Flannery 1969). Food production is only practiced if its net acquisition rate becomes higher than that of foraging for cereal; it then enters the diet in accordance with Equation (4). Agents can thus forage exclusively, farm exclusively, or practice some mixture of both.

## 3. Process overview and scheduling

There are three different experiments that the user can run. Experiment 1 runs the model with only hunting, Experiment 2 runs the model with hunting and gathering, and Experiment 3 runs the model with hunting, gathering, and farming. We will describe the models' process and scheduling for all modes of consumption (Experiment 3) below, as the former experiments run according to the same principles experiment 3. Each experiment runs based on different switches being turned on or off at the setup phase, either enabling or disabling hunting, gathering, or farming.

Most simply put, the model is divided into a setup phase, where all the variables are initialized, followed by a go phase, which includes the procreate, move, and

growCerealsPreysFarms function. Figures 1 and 2 show UMLs describing each function and how they interact with one another. Below is a description of the processes and scheduling.

First the procreate function determines for each individual in a band if they will procreate or not based on a random number. This increases the number of births and individuals. If the number of individuals is larger than the variable individuals at start, then the band fissions into a new band.

Second, following the procreate function, the band starts the move function. The move function determines which patch the band will move to by comparing the resource availability of the band's current patch to any other patches that are within the movement radius. As part of the move function, includes the eatanddie function, which determine how much food the band acquires from hunting, gathering, and farming. Based on the amount of food that each band acquires during this phase, individuals will either die off, or the band will survive to the next tick.

Last, the growCerealsPreysFarms function replenishes the depleted resources for each patch. Once the wild cereals have been reduced to zero in a select patch, the population then starts to farm the area, enabling all three modes of food production.

![](_page_5_Figure_4.jpeg)

*Figure 1. Scheduling process for the model.* 

![](_page_6_Figure_0.jpeg)

*Figure 2. Scheduling process that details how each band makes decisions on the best patch quality.*

# 4. Model design concepts

The basic design concept from this model is derived from the theory of ideal free distribution, where populations will distribute themselves relative to the richness of habitat carrying capacity. Borrowing from the human behavioral ecological literature' deterministic equations that describe the population growth and resource exploitation, we systematically transposed these variables into an agent based framework.

Essentially, by comparing the suitability curves (see Figure 3) of different habitats with respect to changes in population density, the ideal free distribution model can make predictions about human settlement patterns over both time and space. By adding suitability curves for farming, the model can also predict people's subsistence strategies as well as where they will adopt them and when they will switch to different modes of food production.

To capture the essential aspects of the ideal free distribution theory, the quality of our habitats must change with population density, and the agents must be able to make informed choices about which habitat is currently most suitable. Winterhalder et al.'s [^13] mathematical

model of optimal foraging theory, which considers 'the interaction of human population, diet selection, and resource depletion', provides a realistic quantification of both these aspects.

![](_page_7_Figure_1.jpeg)

*Figure 3. A) Suitability of example habitats relative to population density and subsistence method, numbered densities refer to descriptions in text [after 11, and 12]. B) Simplified 9x9 model scape, with three bands of 20 agents shown .*

## 5. Initialization

Nearly all of the variables are initialized in the setup phase of the model execution. The details for each global and turtle variable initialized at the setup phase of the model are explained in Tables 4 and 5.

A number of variables can be parameterized using the slider or the switches. Consequently, we will briefly describe each slider and switch variable below. Figures 4 and 5 show the initialization state of each variable.

Birth-chance is the chance that an individual will give birth to another individual on each time step. The default is set at 10.

Individuals at start determines the size of each band – with 20 being the default.

Learning factor determines how efficient each band becomes at gathering food over time as they reside in one individual patch. The higher the learning factor the more efficient each band is at collecting food resources.

Degredationfactor determines how quickly the patches are degrading over time as a result of population density. The higher the degredationfactor the faster the resources deplete over time.

Movementradius determines how many patches each band can move in a single tick.

doIhunt turns hunting on or off

doIgather turns farming on or off

doIfarm turns farming on or off

rain? Turns rain on or off

Settlevariation determines the variation in rainfall per patch.

![](_page_8_Figure_2.jpeg)

*Figure 4. The starting initialization variables*

![](_page_8_Figure_4.jpeg)

*Figure 5. The starting initialization parameters. Details the set-parameters function and the global variables that are defined.* 

# 6. Inputs

There is only inputs into the model, rainfall.

Rainfall can be turned on or off. If rainfall is ON, a text file can be read that contains data for the Palmer Drought Sensitivity Index. Currently, rainfall has no direct connection between the growth rate, but this can be added at a later date.

### 6.1 Parameter values

See the appendix and Tables 4 and 5 in particular.

## 7. Model implementation

The model was originally implemented in Java and has been reimplemented in here to work in NetLogo 6.40.

## 8. References

Cohen, M.N. (1977). The Food Crisis in Prehistory. Yale University Press, New Haven

Cordain, L., Miller, J.B., Eaton, S.B., Mann, N., Holt, S.H.A., Speth, J.D. (2000) Plant-Animal Subsistence Ratios and Macronutrient Energy Estimations in Worldwide Hunter-Gatherer Diets. American Journal of Clinical Nutrition 71: 682-692. https://doi.org/10.1093/ajcn/71.3.682

Flannery, K.V. (1969). Origins and Ecological Effects of Early Domestication in Iran and the Near East. In: Ucko, P.J., Dimbleby, G.W. The Domestication and Exploitation of Plants and Animals, pp. 73-100. Duckworth, London.

Flannery, K.V. (1973). The Origins of Agriculture. Annual Review of Anthropology 2: 271- 310. https://doi.org/10.1146/annurev.an.02.100173.001415

Harlan, J.R., Zohary, D. (1966). Distribution of Wild Wheats and Barley. Science 153: 1075- 1080. https://doi.org/10.1126/science.153.3740.1074

Kennett, D.J., Winterhalder, B. (eds.). (2006). Behavioral Ecology and the Transition to agriculture. University of California Press, Berkeley Los Angeles London

McClure, S.B., Jochim, M.A., Barton, C.M. (2006). Human Behavioral Ecology, Domestic Animals, and Land Use during the Transition to Agriculture in Valencia, Easter Spain. In Kennett, D.J., Winterhalder, B. (eds) Behavioral Ecology and the Transition to Agriculture. University of California Press, Berkeley Los Angeles London 197-216

van der Vaart, E., de Boer, B., Hankel, A. and Verheij, B., 2006. Agents adopting agriculture: Modeling the agricultural transition. In *From Animals to Animats 9: 9th International Conference on Simulation of Adaptive Behavior, SAB 2006, Rome, Italy, September 25-29, 2006. Proceedings 9* (pp. 750-761). Springer Berlin Heidelberg. https://doi.org/10.1007/11840541_62

Winterhalder, B., Baillargeon, W., Cappelletto, F., Daniel, I.R., Prescott, C. (1988). The Population Ecology of Hunter-Gatherers and Their Prey. Journal of Anthropological Archaeology 7: 289-328. https://doi.org/10.1016/0278-4165(88)90001-3

Winterhalder, B., Kennett, D.J. (2006). Behavioral Ecology and the Transition from Hunting and Gathering to Agriculture. In Kennett, D.J., Winterhalder, B. (eds.) Behavioral Ecology and the Transition to Agriculture, pp. 265-288. University of California Press, Berkeley Los Angeles London.

## 9. Appendix – Tables

### *Table 1. Characteristics of Prey and Cereals*

| Type | Energy value |  | Handle time | Carrying |  |  | Carrying |  |  | Carrying |  |  | Growth rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  | (ei) | (hi) | Capacity | Ci | (Lush) | Capacity | Ci | (Medium) | Capacity | Ci | (Desert) | (ri) |
| Prey (p) | 13800 |  | 235 | 8 |  |  | 5.4 |  |  | 2.5 |  |  | 0.7 |
| Cereal (c) | 3390 |  | 120 | 600 |  |  | 400 |  |  | 200 |  |  | 1 |

#### *Table 2. Agent characteristics.*

| Characteristic | Value |
| --- | --- |
| Group size | 20 - 40 people |
| Min energy | 2000 calories |
| Max forage time | 14 hours |
| Growth rate | 0.02 per year per person |
| Search cost (Cs) | 4 cals per minute |
| Catch cost (Cc) | 6 cals per minute |
| Search speed (Ss) | 0.5 km per hr |
| Search radius (sr) | 0.0175 km |

| Variable name | Definition |
| --- | --- |
| ei | energy value |
| hi | handle time |
| Ci | Carrying capacity |
| ri | growth rate |
| i | index (prey or cereal) |
| p | prey |
| c | cereal |
| ss | search speed |
| sr | search radius |
| si | search time for food type i and di |
| di | current population density of food type |
| ck | wild harvest |
| + ck | additional kilos a square hectare of cultivated cereal might harvest |
| tf | time to produce a kilo of cereal by farming |
| A | number of hectares of cereal that can be tended by working an hour daily |

*Table 3. Variables in each equation and their definition*

|  | NAR 'Lush' Habitat (cals per | NAR 'Medium' Habitat | NAR 'Desert' Habitat (cals |
| --- | --- | --- | --- |
|  | hr) | (cals per hr) | per hr) |
| Prey (p) | 965 | 674 | 281 |
| Cereal (c) | 1298 | 1256 | 792 |
| Farming (f) | 677 | 605 | 481 |

*Table 4. Net Acquisition Rates for each habitat* 

### *Table 5. List and meaning of each global variable*

| Name | Variable type and units | Meaning | Starting Value |
| --- | --- | --- | --- |
| flag | Dynamic | Variable to switch on and off | FALSE |
| rain-data | Static | rainfall data |  |
| crain |  | Counter for rainfall scenario |  |
| cnt | Dynamic | Counter | 0 |
| doIFarm | Dynamic, boolean | Enables farming | FALSE |
| showFarm | Dynamic, boolean | Shows farming on the visual display | FALSE |
| startFarm | Dynamic, boolean | Start farming behavior | FALSE |
| maxPopulation | Static |  | 20 |
| sqKM | Static | Square km for each patch | 300 |
| scale | Static | Scales each cell | 4.5 |
| staticZeroNar | Static | Zeros out NAR |  |
| migratedCount | Static | Counts migrations | 0 |
| searchSpeed | Static | Kilometers per hour for an individual | 0.5 |
| searchRadius | Static | Kilometers per hour for an individual | 0.0175 |

| catchCost | Static | kilocalories per hour | 6 *60 |
| --- | --- | --- | --- |
| searchCost | Static | kilocalories per hour | 4 * 60 |
| energyRequirement | Static | kilocalories per day | 2000 |
| rePopChance | Static | Chance to repopulate a patch | 0.1 |
| minNumtoMigrate | Static | Minimum number of individuals necessary to migrate | 100 |
| minKilosToSpread | Static | Minimum Kilos of cereal to spread | 400 |
| preyEnergy | Static | Kilocalories per prey caught | 13800 |
| preyCatchTime | Static | hours per prey caught | 3.916667 |
| preyGrowthRate | Static | individuals per year | 0.3 |
| preyMaxNARAtPopulation | Static | Max NAR at full population | 200 |
| cerealEnergy | Static | kilocalories per kilo gathered | 3390 |
| cerealHarvestTime | Static | in hours per kilo gathered | 2 |
| cerealGrowthRate | Static | how fast cereals grow | 0.06 |
| cerealMaxNARAtPopulation | Static | Max NAR at full population | 400 |
| cerealMaxKilos | Static | in kilo's per hectare of cereal | 600 |
| cerealMinKilos | Static | in kilo's per hectare of cereal | 0 |
| cerealMaxHectaresPerKM | Static | percent per kilometer | 1 |
| cerealMinHectaresPerKM | Static | percent per kilometer | 1 |
| maxFarmHectares | Static | The maximum amount of hectares farmable | 3000 |
| maxCerealKilosPerHectare | Static | The maximum amount of kilos per hectare | 600 |
| hectaresPerHour | Static | how many hectare are farmable per hour | 2 |
| farmMaxNARAtPopulation | Static | Maximum NAR at full population | 800 |
| reproductionChance | Slider | Slider |  |
| maxForageTime | Static | Total amount of time allowable for foraging, hours | 14 |
| totalMigrated |  |  | null |
| map? |  |  | FALSE |
| land? |  |  | TRUE |

| Name | Agent | Meaning | Value (lush) | Value (medium) | Value (desert) |
| --- | --- | --- | --- | --- | --- |
|  | type | Richness of |  |  |  |
| habitat | prey | ecology (1 is richest, 2 | 1 | 2 | 3 |
|  |  | medium, 3 |  |  |  |
|  |  | lowest) |  |  |  |
| preyPop | prey | Total prey population | 8 * sqKM | 5.4 * sqKM | 2.6 * sqKM |
| maxPop | prey | maximum population by | 8 * sqKM | 5.4 * sqKM | 2.6 * sqKM |
|  |  | habitat |  |  |  |
| preyNar | prey | maximum NAR by | calculatePreyNAR | calculatePreyNAR | calculatePreyNAR |
|  |  | habitat |  |  |  |
| tLeft | prey | Amount of time left to |  |  |  |
|  |  | hunt |  |  |  |
| preyHuntTime | prey | Amount of time to hunt | preySearchTime + | preySearchTime + | preySearchTime + |
|  |  |  | preyCatchTime | preyCatchTime | preyCatchTime |
|  |  | prey |  |  |  |
| preySearchTime | prey | Time need to | 1 / (searchSpeed * searchRadius | 1 / (searchSpeed * searchRadius | 1 / (searchSpeed * searchRadius |
|  |  | search for prey | * 2 * preyDensity) | * 2 * preyDensity) | * 2 * preyDensity) |
| preyDensity | prey | Density of prey | (preyPop / sqKM) |  |  |
|  |  | in patch |  | (preyPop / sqKM) | (preyPop / sqKM) |
| growth | prey | Reproduction e rate | ^ preyGrowthRate | e ^ preyGrowthRate | e ^ preyGrowthRate |
| cerealPop | cereals | Total cereal population | 600 * sqKM | 402 * sqKM | 198 * sqKM |

*Table 6. List and meaning of each turtle variable.* 

| farmPop | cereals | Total farm | null |  |  |
| --- | --- | --- | --- | --- | --- |
|  |  | population |  |  |  |
| maxFarm | cereals | Maximum farm | null |  |  |
|  |  | population |  |  |  |
| maxPop | cereals | Maximum cereal | 600 * sqKM | 402 * sqKM | 198 * sqKM |
|  |  | population |  |  |  |
| cerealNar | cereals | Cereal NAR | calculateCerealNAR | calculateCerealNAR | calculateCerealNAR |
| tLeft | cereals | time left needed to |  |  |  |
|  |  | forage |  |  |  |
| cerealSearchTime | cereals | Time needed to search for | (1 / (searchSpeed * searchRadius * 2 * ((cerealPop) / sqKM))) | (1 / (searchSpeed * searchRadius * 2 * ((cerealPop) / sqKM))) | (1 / (searchSpeed * searchRadius * 2 * ((cerealPop) / sqKM))) |
|  |  | cereal |  |  |  |
| cerealGatherTime | cereals | Time needed to | (cerealSearchTime + | (cerealSearchTime + | (cerealSearchTime + |
|  |  | gather cereal | cerealHarvestTime) | cerealHarvestTime) | cerealHarvestTime) |
| growth | cereals | Cereal reproduction | e ^ cerealGrowthRate | e ^ cerealGrowthRate | e ^ cerealGrowthRate |
|  |  | rate |  |  |  |
|  |  | Maximum | ((0.25 * (1000 - cerealGradient * maxCerealKilosPerHectare) + | ((0.25 * (1000 - cerealGradient * maxCerealKilosPerHectare) + | ((0.25 * (1000 - cerealGradient * maxCerealKilosPerHectare) + |
| maxFarm | farms | amount of farms | (cerealGradient * maxCerealKilosPerHectare)) * maxFarmHectares) | (cerealGradient * maxCerealKilosPerHectare)) * maxFarmHectares) | (cerealGradient * maxCerealKilosPerHectare)) * maxFarmHectares) |
|  |  | Spread rate of | 1 | 0.7 | 0.33 |
| cerealGradient | farms | cereals |  |  |  |

| cerealKilos | farms | Kilos of cereal | ((cerealGradient * (cerealMaxKilos - | ((cerealGradient * (cerealMaxKilos - | ((cerealGradient * (cerealMaxKilos - |
| --- | --- | --- | --- | --- | --- |
|  |  | per patch | cerealMinKilos)) + | cerealMinKilos)) + | cerealMinKilos)) + |
|  |  |  | cerealMinKilos); | cerealMinKilos); | cerealMinKilos); |
| extraCerealKilos | farms |  | (0.25 * (1000 - cerealKilos)) | (0.25 * (1000 - cerealKilos)) | (0.25 * (1000 - cerealKilos)) |
| cerealFarmTime | farms | Amount of time + needed to farm | ((1 / (hectaresPerHour * (cerealKilos extraCerealKilos))) * 365 + | ((1 / (hectaresPerHour * (cerealKilos + extraCerealKilos))) * 365 + | ((1 / (hectaresPerHour * (cerealKilos + extraCerealKilos))) * 365 + |
|  |  |  | cerealHarvestTime); | cerealHarvestTime); | cerealHarvestTime); |
|  |  | Density of | (((maxFarm * (cerealEnergy - cerealFarmTime * 6 * 60)) / | (((maxFarm * (cerealEnergy - cerealFarmTime * 6 * 60)) / | (((maxFarm * (cerealEnergy - cerealFarmTime * 6 * 60)) / |
| maxFarmersDensity | farms | farmers | (energyRequirement * 365)) / (sqKM | (energyRequirement * 365)) / (sqKM | (energyRequirement * 365)) / (sqKM |
|  |  | * | scale)) | * scale)) | * scale)) |
| farmNar | farms | Farm NAR | calculateFarmNar | calculateFarmNar | calculateFarmNar |
| farmPop | farms | Populations of 0 |  |  |  |
|  |  | farms |  |  |  |
| tLeft | farms | Time left for farming |  |  |  |
|  |  | Adaptive |  |  |  |
| technology | farms | capacity |  |  |  |
| rain | farms | Rainfall |  |  |  |
| individuals | bands | Individuals in bands | 20 |  |  |
| births | bands | Number of 0 |  |  |  |
|  |  | births |  |  |  |
| deaths | bands | Number of 0 |  |  |  |
|  |  | deaths |  |  |  |
| timeLeft | bands | Time left in day |  |  |  |

| energyHunted | bands | Amount of energy acquired | 0 |
| --- | --- | --- | --- |
|  |  | through hunting |  |
| energyGathered | bands | Amount of energy acquired | 0 |
|  |  | through |  |
|  |  | gathering |  |
| energyFarmed | bands | Amount of energy acquired through farming | 0 |
| timeHunted | bands | Time spent | 0 |
|  |  | hunting |  |
| timeGathered | bands | Time spent gathering | 0 |
| timeFarmed | bands | Time spent | 0 |
|  |  | farming |  |
| duration | bands | Number of ticks survived |  |
| patch_habitat | patches | Habitat patches |  |
| patch_land? | patches | Patch is land or not |  |

