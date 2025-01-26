# Model Manual

Daria Soboleva1,2

1Department of Economics, Duke University, Durham, NC 27708, USA 2Department of Mathematics, Universidad Carlos III de Madrid, Legan´es, Madrid 28911, Spain Email: daria.soboleva@duke.edu

July 31, 2024

## 1 Overview

The present model was created and used for the study titled "Agent-Based Insight into Eco-Choices: Simulating the Fast Fashion Shift." The model is implemented in the multi-agent programmable environment NetLogo 6.3.0.

The model is designed to simulate the behavior and decision-making processes of individuals (agents) in a social network. It focuses on how agents interact with their peers, social media, and government campaigns, specifically regarding their likelihood to purchase fast fashion.

The agents are individual consumers and are initialized in the beginning of the simulation. Each agent has certain static attributes, such as their sex and age, and those that change over the time of the simulation, such as concerns for the environment.

## 2 Structure

In this section, we detail the structure and scheduling of the model, as well as the three mechanisms of influence. The model consists of two steps: initialization of agents and the main loop.

### 2.1 Initialization

In this model, agents represent individual consumers who are characterized by certain attributes. These attributes were selected based on the results of the linear regression analysis, which is detailed in the study associated with this model. The resulting linear function is given by Eq. (1) and is the decision-making model each agent uses to estimate their probability to purchase from a fast fashion brand. Each variable used in it is described in Table 1, and the values of the linear regression analysis can be found in Table 2.

$$A_{p}=b_{0}+b_{1}\cdot A_{wx}+b_{2}\cdot A_{age}+b_{3}\cdot A_{env}+b_{4}\cdot A_{exp}+b_{5}\cdot A_{wco}+b_{6}\cdot A_{know}+b_{7}\cdot A_{trust}+b_{8}\cdot A_{access}+b_{9}\cdot A_{freq},\tag{1}$$

The values of these attributes can be read from a csv file or can be generated randomly. Each agent is initialized with the following attributes:

- Sex;
- Age;
- Environmental concerns;
- Working conditions awareness;
- Shopping frequency;
- Education on the topic of sustainable fashion;
- Normative expectations;
- Trust in sustainable companies;
- Access to sustainable fashion.

| Coefficient name | Value |
| --- | --- |
| Ap | Probability to buy fast fashion |
| Asex | Sex |
| Aage | Age |
| Aenv | Environmental concerns |
| Aexp | Normative expectations |
| Awca | Working conditions awareness |
| Aknow | Education on sustainable fashion |
| Atrust | Trust in companies |
| Aaccess | Access to sustainable brands |
| Af req | Shopping frequency |

Table 1: Variables for Eq. (1).

| Coefficient name | Value | Predictor variable |
| --- | --- | --- |
| b0 | 0.7450 | constant |
| b1 | -0.0101 | Sex |
| b2 | 0.0200 | Age |
| b3 | -0.0179 | Environmental concerns |
| b4 | -0.0488 | Normative expectations |
| b5 | -0.1783 | Working conditions awareness |
| b6 | -0.1414 | Education sustainable fashion |
| b7 | 0.0320 | Trust in companies |
| b8 | 0.0360 | Access to sustainable brands |
| b9 | 0.2181 | Shopping frequency |

Table 2: Coefficients of the linear regression

Hence, each agent is initialized with the following attributes:

• Sex;

- Age;
- Environmental concerns;
- Working conditions awareness;
- Shopping frequency;
- Education on the topic of sustainable fashion;
- Normative expectations;
- Trust in sustainable companies;
- Access to sustainable fashion.

Aside from these, each agent is randomly assigned three additional static variables that represent their levels of susceptibility. Each of these are within the range of [0.1, 0.9], where 0.1 indicates low susceptibility and 0.9 - high susceptibility:

- 1. Peer influence susceptibility, Spp. This variable determines how easily an agent's opinion is influenced by other agents in its neighborhood. A higher susceptibility value indicates that the agent is less influential on others. Conversely, if an agent has significant influence over its peers, its susceptibility to their influence will be lower.
- 2. Social media susceptibility, Ssm. This value denotes the degree to which an agent is susceptible to social media and its influence. In this simulation, we assume that all agents utilize some form of social media on a daily basis. The level of susceptibility can also be seen as proportional to the frequency of usage of social media.
- 3. Government influence susceptibility, Sgov. This variable determines the extent to which an agent is influenced by government initiatives and interventions, such as campaigns and education efforts. Different levels of susceptibility are primarily associated with political affiliations: agents with higher susceptibility represent individuals whose political identity aligns with the governing party, to varying degrees. The opposite is true for agents with low government susceptibility, although these can also represent agents with apolitical stances.

### 2.2 Influence mechanisms

There are three key components to this model: peer interaction, social media influence, and government interventions. All three can influence three agents' attributes: environmental concerns, working conditions awareness, and education on the topic of sustainable fashion. Additionally, the government can influence agents' trust in companies claims regarding sustainability. In this section, we describe each for of influencing present in the model.

### 2.2.1 Peer influence. Non-polarized agentset

The first kind of agentset is titles "non-polarized" and corresponds to a set of individuals whose opinion on topics tends to homogenize over time because these topics are not perceived as controversial or polarizing ones. In both non polarized and polarized agentset, agents are programmed to interact with a subset of the agents in their neighborhood during each time step. Every agent is set to have 5 close friends, which forms their inner circle, and 10 acquaintances, which forms their outer circle. Although in real-life individuals tend to have more connections, we base our choice on the size of the agentset to avoid overconnectedness, and this can be adjusted by the user. The close friends are all connected, while the acquaintances are randomly selected and do not necessarily connect to each other. Hence, each agent has a total of 15 connections, and we allow agents to interact with 10 other agents daily (by default, but this is changeable). To introduce some variability, we allow agents to interact with 10 ± a friends, where a ∈ [1, 4]. In this model, we assume that an agent is equally likely to interact with their close friends as with their acquaintances. Additionally, we assume that each interaction with a friend, whether best or close, has an equal effect on the agent's perception of their opinion.

Once each agent's neighborhood is determined, the agent's updated opinion after each interaction is given by Eq. (2).

$$A_{t,i}=(1-S_{pp}(A_{i}))\cdot A_{t-1,i}+\frac{S_{pp}(A_{i})}{\sum\limits_{A_{j}=1}^{N}}\cdot\sum\limits_{A_{j}=1}^{A_{j}\in\text{pers}(A_{i})}\left[\frac{1}{3}A_{t-1,j}+\frac{2}{3}B_{t-1,j}\right],\tag{2}$$

where At,i stands for agent's updated opinion on a topic, Spp(Ai) represents agent's susceptibility towards others, At−1,i represents their opinion at the previous time step, and At−1,j and Bt−1,j represent peers' opinion and behavior at a previous time step, respectively. Each agent can only be influenced by those in its neighborhood whose susceptibility is lower than that of the agent. This represent the phenomenon seen in real-life interactions, where lower susceptibility tends to correlate with higher influentiality, and vice versa. This variable also allows us to incorporate another important social phenomenon: inexorable individuals, which are not easily persuaded, moved, or affected by normative expectations. Additionally, both peers' behavior and attitudes are included in this equation (At−1,j and Bt−1,j , respectively). This decision was based on the observation that individuals tend to be influenced twice as much by conformity with peers' behavior as by normative expectations. In other words, what one's peers do matters more than how one thinks they expected other to behave.

### 2.2.2 Peer influence. Polarized agentset

The second kind of agentset we explored is titled "polarized." We want to explore peer influence in a scenario where the population is polarized and does not homogenize their views over time, but instead clusters around multiple opinions. We know that consensus is rarely achieved in realworld scenarios regarding polarized topics because individuals' initial internal opinions, unlike their expressed opinions, remain unchanged by social interaction. In certain societies and countries, fast fashion and its relation to the environment is a polarized topic, and we want to account for such development.

The equation used for social interactions in a polarized society will be similar to that for a nonpolarized society. However, the difference lies in the introduction of a tolerance threshold (denoted by τ ∈ [0.05, 0.50]), which represents how tolerant agents are toward opinions that deviate from theirs by more or less than the threshold. If the threshold is set to m, then opinions within a range of ±m from an agent's opinion will have a homogenizing effect. However, opinions beyond this threshold will have an opposite effect, pushing the agent's opinion toward the opposite end of the spectrum. For instance, if an agent's opinion is 0.5 and their friend's opinion is 0.9, with a tolerance level of m = 0.2, the interaction with that friend will contribute to the opinion change of 1 − 0.9 = 0.1, pulling the agent toward the opposite opinion of that of their neighbors. In summary, a lower threshold indicates less tolerance towards differing opinions. When an agent encounters an opinion that exceeds their tolerance threshold, the interaction becomes polarizing rather than unifying.

### 2.2.3 Social media influence.

Social media is treated as a single external entity. While various social media platforms exist, we simplify this complexity by considering social media as a unified external influence. It is important to clarify that from now on, when exposure to or engagement with social media is mentioned, it pertains solely to exposure on the topics of interest (environment, working conditions, sustainability, etc.) and does not refer to all social media usage.

In real life, social media platforms adapt to each user, tailoring content based on their preexisting preferences and inclinations. Content one sees is content they already consume or are likely to consume. In our model, we implement such mechanisms by incorporating a feedback loop between the agent's opinion and their social media platform. It is recognized that social media tends to increase polarization by creating "echo chambers" that limit exposure to information contradicting preexisting beliefs, and this is particularly the case for politicized topics. Moreover, social media can be biased towards pro-fast fashion or anti-fast fashion, which is something we consider in this model. Our choice to add a bias term rests on the fact that social media is found to both promote consumption, but can also be a powerful tool that can be used to promote sustainable habits. As a result, we derive a function that takes an agent's current opinion as an input an returns an "influence" opinion to the agent. This feedback loop is given by Eq. (3).

$$SM\left(A_{t-1}\right)=b\cdot\left(A_{t-1}\right)^{3}+\frac{-3\cdot b}{2}\left(A_{t-1}\right)^{2}+\frac{3\cdot b}{4}\left(A_{t-1}\right)+\left(\frac{1}{2}-\frac{b}{8}\right)+\beta,\tag{3}$$

were b = 50·Ssm, Ssm stands for agent's susceptibility towards social media, and β ∈ [−0.30, 0.30] is the bias. Once we have obtained the social media influence level from the function above, we can find the agent's opinion after using social media, which is given by:

$$A_{t}=(1-S_{sm})\cdot g(A_{t-1},SM)\cdot A_{t-1}+S_{sm}\cdot f(A_{t-1},SM)\cdot SM,\tag{4}$$

where At−1 represents agent's opinion at the previous time step, At is the updated opinion, Ssm stands for social media susceptibility of the agent, and SM is the opinion that social media obtained from the feedback loop. This function also incorporates each agent's susceptibility. Fig.(1) illustrates three variations of the social media feedback loop function, each reflecting different levels of susceptibility. In Fig. (1a), the susceptibility is set at Ssm = 0.2, indicating a low susceptibility, which results in a wider function. This means the content shown to the agent is similar to what they currently view, with minimal deviation. Fig. (1b) depicts a susceptibility of Ssm = 0.5, leading to a steeper function and a greater divergence from the agent's existing content. Finally, Fig. (1c) shows a susceptibility of Ssm = 0.8, resulting in the steepest function of the three, meaning the content presented is significantly more extreme compared to what the agent's current view. In any case, if the output exceeds 1, it is manually capped at 0.95 to prevent extreme values. Similarly, if the output is negative, it is adjusted to 0.05 to avoid values outside the defined range.

Moreover, the function differs based on the value of β, and this adjustment is made for all agents. In Fig. (2), we see the same feedback loop function for Ssm = 0.5, but different levels of social media biases: anti-sustainability in Fig (2a), neutral in Fig. (2b), and pro-sustainability in Fig. (2a).

Next, Eq. (4) ensures that an agent's opinion changes gradually and cannot be drastically affected in a single time step. Let us delve deeper into Eq. (4). Typically, a linear equation is used to adjust an agent's opinion based on an influence, and we plot an example of such in all upcoming figures for comparison. However, we devised a more sophisticated equation to ensure that an agent's opinion

![](_page_5_Figure_0.jpeg)

Figure 1: Social media feedback loop function from Eq. (3) for β = 0 and different Ssm values.

![](_page_5_Figure_2.jpeg)

Figure 2: Social media feedback loop function from Eq. (3) for Ssm = 0.5 and different bias values.

cannot change drastically in just one step. In Eq.(4), we make use of function f and g, which are defined in Eq. (5) and Eq. (6), respectively.

$$f(A_{t-1},SM)=e^{-(1-S_{sm})\cdot|A_{t-1}-SM|}\tag{5}$$

$$g(A_{t-1},SM)=e^{S_{sm}\cdot|A_{t-1}-SM|}\tag{6}$$

Consider an agent with a susceptibility to social media of 0.5. The two inputs that are changing are the agent's current opinion and the social media "influence" direction, calculated one step prior using the function described in Eq. (3). Therefore, we have two inputs. To represent this in a 2D graph, we set the agent's opinion as a parameter, set at At−1 = 0.0, 0.5, 1.0 and the x-axis represents the output of the social media function, indicating the opinion it promotes. The y-axis represents the agent's updated opinion. Fig. (3) illustrates three functions for different values of At−1, and all figures contain a linear function, which is commonly used in such scenarios. Our function of choice assures that agent's opinion cannot be changed drastically in one time step, which cannot be guaranteed using a linear function.

Let us begin by examining Fig. (3a), where the agent's opinion set at 0.5. We can see that, no matter what opinion is promoted by social media, agent's opinion will not change as drastically as in case of the red line. Next, let us look at Fig. (3b), where agent's current opinion is at At−1 = 0. Note that with the linear function, the agent's opinion can change from 0 to 0.4 in just one time step, which is evidently too drastic. However, with the blue function, this is not the case, ensuring a smoother and slower transition. The further away from the original opinion - the smaller the derivative value of the blue line.

![](_page_6_Figure_0.jpeg)

Figure 3: Social media influence function Eq. (4) for Ssm = 0.5 and different inputs of feedback

Similarly, Fig. (3c) illustrates the case where the agent's opinion is set at At−1 = 1. Here, the blue line depicts the potential return, while the red line serves as a reference. In all three cases, the blue line represents the values that the agent's opinion will take based on the input of social media influence. Notice that the derivative of the blue function decreases the further away we get from the intersection point, representing the smoother transition of opinion.

Now, let's observe how this function changes as the susceptibility level varies. In Fig. (4), we plot two cases: Fig. (4a), where the agent's susceptibility is Ssm = 0.0, and Fig. (4b), where it is is Ssm = 1.0. When the susceptibility level is zero, the input becomes irrelevant; social media will not influence the agent's opinion, thus returning the same value as At−1, which acts as a parameter for the plot. Similarly, for a susceptibility of 1, the function becomes a linear equation, as the agent is willing to undergo drastic opinion changes in a single step.

![](_page_6_Figure_4.jpeg)

Figure 4: Social media influence function Eq. (4) for different levels of susceptibility.

### 2.2.4 Government interventions.

The government, or state, is considered a single external entity in this model, with one primary goal: to influence the population's opinions and concerns regarding topics of interest (environment, working conditions, sustainability, trust in companies.) Unlike social media, the government does not tailor campaigns to individual agents based on their current views. Instead, it shares the same information with the entire population.

In this model, the government is designed as a "smart" entity aiming for re-election. This means that it promotes opinions similar to the average opinion of the population, which it uses as an input to the government feedback loop, shown in Eq. (7).

$$GOV(A(tot)_{t-1})=\zeta\cdot A(tot)_{t-1},\tag{7}$$

where A(tot)t−1 stands for the average view of the entire population, and ζ is a parameter set by the user that falls within the range of [0.5, 1.5], where ζ = 0.5 signifies a strong anti-sustainability stance, ζ = 1 represents neutrality, and ζ = 1.5 indicates strong pro-sustainability views. After the state's "opinion" is determined by Eq. (7), it is disseminated to agents. The formula representing the change in an agent's opinion after "interacting" with governmental influence is given by Eq. (8).

$$A_{t}=(1-S_{gov})\cdot g(A_{t-1},GOV)\cdot A_{t-1}+S_{gov}\cdot f(A_{t-1},GOV)\cdot GOV,\tag{8}$$

where GOV is the promoted opinion calculated with Eq. (7), Sgov is agent's susceptibility to government's interventions, and At−1 is the opinion of an agent at time t − 1. The functions g and f are exactly the same as described above for social media, and Eq. (8) is identical to Eq. (4). Similar to social media, we aimed to prevent drastic changes in agents' opinions and thus chose a more sophisticated function that allowed for a slower evolution of their viewpoints. Additionally, we implement a function that aims to mimic the diminishing impact of repeated exposure, a phenomenon known as "campaign fatigue." This will affect agents' susceptibility to government, Sgov, in a manner represented by Eq. (9).

$$S_{gov,t}=S_{gov,t-1}\cdot\exp{(-0.00125\cdot T)},\tag{9}$$

where Sgov,t−1 is agent's susceptibility at previous time step, Sgov,t is that same agent's susceptibility at current time step, and T is the number of weeks (which consist of 7 time steps) that have past since the beginning of the simulation.

### 2.3 Loop

### 2.3.1 Time management

At every time step, also referred to as "tick," three events occur, managed by an interaction management function: one interaction with a specific number of friends, one instance of using social media, and one potential interaction with government campaigns. While the first two events occur deterministically once every time step, the occurrence of government campaigns is randomized and may or may not take place in an agent's day.

Furthermore, social media interaction occurs only once per day for simplicity, but it yields qualitatively satisfactory results. Increased usage of social media by some individuals is factored into the calculations through susceptibility towards social media: the more an individual uses social media, the more susceptible they are to its influence.

### 2.3.2 Simulation

Once the simulation starts, the main loop begins running until a set limit of ticks is reached, which can be controlled by the user and is set to 500 ticks in all the models presented in this thesis. The main purpose of this loop is to call the interaction management function and update the visual for the user. The interaction management function consists of initiating one of the three interactions of the time step for the agent. At the end of each time step, each agent's probability to purchase fast fashion is evaluated given the updates in their views and habits.

### 2.3.3 Pseudocode

We include a pseudocode to represent in a simplistic manner what the overall structure of the code is. In the next sections, we delve into each of the steps involved in it and justify their settings.

```
Overview of the model structure
```
- 1. Initialize agents and build visualization (setup).
- 2. Go (for 500 ticks):
	- (a) Random campaign is selected.
	- (b) For each agent:
		- i. Peer interaction.
		- ii. Social media interaction.
		- iii. Maybe: interaction with state's campaign.
	- (c) Update individual attributes based on changes.

## 3 Usage

In this section, I will detail how the model is used. We begin by looking at the setting that are available to the user, how to read the output and save it. Fig. (5) illustrates the interface and each set of tools is marked to simplify the explanation.

I begin by going over each of the sections in the interface and the parameters associated with it. I recommend that these settings are adjusted before setting up the model and running it, although the user might make changes during the simulation. In each of the following items, the cursive indicates the name of the paramters, while their values are in quotes, unless these are numeric parameters.

- 1. There are two sliders available: one associated with the number of agents to be initialized (num agents) and the other with the length of the simulation (num ticks). Note that, if agents are initialized from a csv file, the value of num agents cannot exceed the number of agents available in the csv file.
- 2. Data? stands for the source of data used to initialize the agents. If "random" is chosen, all agents will be initialized randomly. If "file" is chosen, you will have to provide a file from which the model will read the data. Please make sure that the order of variables coincides with that of how the code reads it, which is in the following order: serial number, sex, age, environmental concerns, shopping frequency, probability to buy fast fashion, weight of normative expectations,

![](_page_9_Picture_0.jpeg)

Figure 5: Interface of the model

working condition awareness, education on the topic of sustainable fashion, trust in companies, and access to sustainable fashion.

- 3. There two choosers available that refer to the layout of the black plot (number 10). The Colours? choosers has two options, both coloring agents based on their probability to purchase fast fashion: "pff" colors those agents whose probability is high (above 0.7) in red, those with low probability (below 0.4) with lime, and everyone else with yellow; the "apff" colors agents the other way around (those with high probability are set to lime and those with low - to red). That is dependent on whether the user is interested in increasing the probability to purchase fast fashion or decreasing it, given that the model can be used for both. The other chooser layout? refers to whether the links between agents can be seen ("Circle") or are hidden ("Simple"). If the user wants to be able to click of agents and read their attributes, I highly recommend using the "Simple" option.
- 4. This chooser Influence? refers to what influence mechanisms the user wants to study. There are four options. Three of them isolate each mechanism, "Peer influence", "Social media", "Government". "Everything" refers to all three mechanisms being implemented.
- 5. Government interventions: this section of the interface refers to all the settings associated with the state. zeta.gov (ζ) refers to the position the government will be promoting. Recall that it is the same for all agents, and it ranges from ζ = 0.5 (highly anti-sustainability) to ζ = 1.5 (highly pro-sustainability), with ζ = 1 being the neutral position. Campaign.type refers to the style of campaign, which can be "random" or "cyclic". If "cyclic" is chosen, the user can also choose the length of each cycle with the slider length.cycle. If the user chooses "Campaign.type=None", this would imply that the government does not launch any campaigns and is effectively not influencing the agents. The user can choose to implement taxation with tax.type chooser, where "None" stands for no taxes, "Fixed" stands for a fixed tax rate, and "Progressive" stands for a progressing tax rate. In case one of the two latter options is chosen, the user can also choose a taxation.rate.
- 6. There are several options for the user associated with the polarization of the agentset. With society?, the user can choose whether the agentset will be polarized or not. If "Polarized" is chosen, sigma.sm will be used to set the tolerance level, earlier referred to as τ . Additionally, the user can choose, using the behavior.polarization chooser, if the behavior of agents will also have a polarizing effect, or if this only applies to their opinions.
- 7. There are a few settings of social media that the user can set. The first one, tau.tolerance (τ ), refers to what agents are exposed to the social media, specifically to the topics of relevance. This slider ranges from 0.05 t 0.5, and it is related to the levels of concerns necessary for an agent to have in order to be exposed to information related to the topic of interest. For instance, if we choose 0.05, that means that only those agents whose concerns are 0.95 or above and 0.05 or below will be shown content related to those concerns. Similarly, if 0.25 is chosen, then agents with concerns above 0.75 and below 0.25 will be exposed to this content. Once this slider is set to 0.5, everyone is exposed to the content. The other parameters to set is the beta.sm.bias, which represents the bias of social media content and impacts all agents. If it is set to negative values, social media shows user content related to fast fashion consumption and anti-sustainability. On the contrary, if positive values are selected, users see content related to sustainability and anti-fast fashion. The zero value represents neutrality.
- 8. The user can modify how agents interact with several parameters. First, delta.comm (δ) refers to the levels of concern agents should have in order to begin sharing their opinion with their

peers. It works similarly to the polarization.threshold of social media, in a sense that the agent has to have concerns above 1 − δ or below δ in order to bring the topics of concern to the peer pressure function. Hence, if it is set to 0.5, every agent will share their opinion with other agents. The other three parameters refer to the number of agents each agent interacts with. Outside.friends.num refers to the number of acquaintances, friends.group.size to the number of close friends, and num.friends.interact refers to the number of agents each agent interacts with daily, with some variability. This last parameters depends on the other two and cannot exceed their sum.

- 9. The user has four choices for the black plot x with the plot.x.axis chooser. This can be one of the four attributes that can be influenced through the mechanisms of influence: environmental concerns, working conditions concerns, education on the topic of sustainable fashion, and trust in companies. The black plot is a 2D plot that represents compares the changes in one of the four attributes chosen above (on the x-axis) and the probability to purchase fast fashion on the y-axis.
- 10. The first white plot will show the user the changes in average attributes of interest over the time of the simulation. These values are saved to a text file every five time steps for analysis.
- 11. The second white plot will show the user the changes in variability in attributes of interest over the time of the simulation. These values are saved to a text file every five time steps for analysis.

### 3.1 List of parameters

In this section, I summarize all the parameters that might be of interest to the user and that they can manipulate before and during the simulations. These parameters are explained in more detail above.

| Peer pressure | Range/Possible values |
| --- | --- |
| delta.comm (δ) | [0.05, 0.5] |
| outside.num.friends | [10, 30]∗ |
| friend.group.size | [5, 15]∗ |
| num.friends.interact | ∗ [5, outside.num.friends + friend.group.size] |
| Polarization of agents |  |
| society? | Yes (polarized), No (non polarized) |
| tau.tolerance (τ ) | [0.05, 0.5] |
| behavior.polarization | Yes, No |
| Social media |  |
| sigma.sm (σ) | [0.05, 0.5] |
| beta.sm.bias (β) | [−0.30, 0.30]∗ |
| Government |  |
| zeta.gov (ζ) | [0.5, 1.5]∗ |
| campaign.type | None, Random, Cyclic |
| length.cycle | [10, 30]∗ |
| tax.type | None, Progressive, Fixed |
| taxation.rate | [0, 25]∗ |

Table 3: Parameters

In Table 3, those values marked with an asterisk (∗) are the ones that the user can edit without changing and interfering with the model's settings and functions. The other parameters should not be changed unless changes in the code are made.

## 4 License

Copyright 2024 Daria Soboleva.

This code was developed and used for a paper titles "Agent-Based Insight into Eco-Choices: Simulating the Fast Fashion shift," an the preprint can be found on https://arxiv.org/pdf/2407.18814.

This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 License. To view a copy of this license, visit https://creativecommons.org/licenses/by-nc-sa/3.0/ or send a letter to Creative Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.

## 5 Contact

For any additional information on the model or suggestions, please contact Daria Soboleva via daria.soboleva@duke.edu

