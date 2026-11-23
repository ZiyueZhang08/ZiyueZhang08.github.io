---
title: Learning Without Pulling: How Auxiliary Information Changes Sequential Decision-Making
date: 2026-11-22
tags: [Paper Notes]
summary: Reading notes on adaptive sequential experiments with unknown information arrival processes, plus my own thoughts on information coverage versus information volume.
---

*Reading Notes on Adaptive Sequential Experiments with Unknown Information Arrival Processes*

### Part I — Paper Review

The classical Multi-Armed Bandit studies the Exploration–Exploitation Trade-off. A decision-maker repeatedly chooses among several arms with unknown rewards: on one hand she wants to exploit the option that currently looks best, and on the other she must explore actively to gather information that improves future decisions. Traditional stochastic bandits usually assume that a reward observation about an arm is obtained only by pulling that arm. In practice, information is not always generated this way. Take e-commerce recommendation as an example: even if the platform never recommends a product, some users may still reach it through a search engine and buy it. Such behavior is not caused by the current recommendation decision, yet it may carry important information about the product's payoff. The starting point of this paper is to bring this kind of naturally arriving Auxiliary Information into the classical bandit framework.

The authors let $h_{k,t}$ denote the number of auxiliary observations about arm $k$ that arrive between two decision epochs, and let $H$ describe the full information arrival trajectory. These observations are assumed to be linked to the true expected reward through a mapping $\phi_k$:

$$
\mathbb E[\phi_k(Y_{k,t,m})]=\mu_k.
$$

Unlike ordinary rewards, auxiliary information may arrive even when the corresponding arm is not pulled. The authors first consider the case where the mapping is known, and ask what performance sequential decision-making can theoretically achieve under an unknown and arbitrary exogenous information arrival trajectory.

The paper first establishes a minimax regret lower bound that depends on the information arrival trajectory. Its core mathematical structure contains the term

$$
\log\left(
\sum_{t=1}^{T}
\exp\left(-c\sum_{s=1}^{t}h_{k,s}\right)
\right).
$$

The most interesting aspect of this structure is that the difficulty of the problem is determined not only by how much auxiliary information is eventually obtained, but also by *when* it arrives. Information that arrives earlier removes more uncertainty from more subsequent decisions. When the auxiliary information is sufficiently informative and arrives sufficiently often, cumulative regret can even improve from the classical logarithmic order to a bounded level.

Having pinned down the theoretical lower bound, the authors ask whether one can design an algorithm that does not need to predict the future information arrival process. For UCB1, they incorporate auxiliary observations into both the reward estimate and the effective sample size; for Thompson Sampling, they use auxiliary information to update the sampling distribution. The result is aUCB1 and aTS. Theorems 2–3 show that, with a known mapping, both algorithms adapt to the unknown information arrival trajectory and attain a regret growth rate that matches the corresponding lower bound. The key finding is that an algorithm does not need to forecast future information flows: by continually updating its own uncertainty, it adjusts its exploration intensity naturally.

All of this, however, rests on a strong premise: that we know how to convert auxiliary information into true rewards. In reality, the mapping may be inaccurate. The authors therefore go on to study Unknown Mappings, mainly under a linear relationship:

$$
\mu_k=\alpha_k y_k.
$$

Even with infinitely many auxiliary observations, if $\alpha_k$ is unknown, the true payoff may remain unidentifiable. Through counterexamples, different performance regimes, and information-theoretic lower bounds, the authors characterize when auxiliary information can reduce active exploration under an unknown mapping. When it is known that $\alpha_k\leq\bar\alpha$, we still have

$$
\mu_k\leq\bar\alpha y_k.
$$

This means that even if we cannot estimate an arm's reward accurately, as long as we can show that the arm cannot exceed the best arm even under the most optimistic conditions, we can explore it less.

Building on this idea, the authors propose 2-UCBs. The algorithm constructs two upper confidence bounds for the same unknown parameter: one that depends only on direct rewards, and another that is an optimistic bound combining direct rewards with auxiliary data. It then uses

$$
U_{k,t}=\min\left\{
U_{k,t}^{direct},
U_{k,t}^{aux}
\right\}.
$$

I think this is the most memorable algorithmic insight of the paper: use two different information sources to place valid statistical constraints on the same unknown parameter, and act optimistically with the tighter one. It does not require recovering the unknown mapping exactly. Instead, it exploits a credible upper bound on the mapping, so that auxiliary data helps whenever it can provide a valid constraint, while the direct UCB prevents overly optimistic auxiliary estimates from misleading the algorithm. Theorem 6 gives the corresponding near-optimal performance guarantee.

Finally, the authors build semi-synthetic experiments from media-website data to examine how the informativeness of auxiliary information and mapping misspecification affect decision performance. Having read the whole paper, I find it a very representative example of an OR research paradigm: identify an information structure that traditional models overlook in a real problem, study how this change affects the theoretical performance limits, and then design algorithms with matching guarantees. Its contribution goes beyond extending UCB or Thompson Sampling; more importantly, it re-characterizes how the information-generating mechanism shapes exploration and learning.

### Part II — My Perspectives

Reading this paper made me realize that we usually think of information acquisition as a question of quantity: more observations, larger samples, more accurate estimates. But if we unfold how information is actually acquired in the real world, it looks more like a highly sparse matrix than a steadily growing data sequence.

Consider a recommendation system. What we truly want to know is not just the overall purchase rate of a product, but the latent payoff of different products for different user groups in different contexts. If we put products in the rows and user groups in the columns, each cell represents an expected payoff we would like to learn. In reality, we can observe only a tiny fraction of them. Rewards from active recommendations fill in some cells, while auxiliary data from organic search, user reviews, or other channels provide indirect information about others. More precisely, these auxiliary observations do not necessarily fill the target reward matrix directly; rather, they impose constraints on some of its cells through an unknown mapping. We are actually facing two different information-acquisition mechanisms, and a latent payoff structure that is far from fully observed.

From this perspective, active exploration and passive observation can be seen as two relatively independent axes. A decision problem may have abundant experimental data but almost no external information; it may have massive passive observations but no direct rewards; it may have both in abundance, or both in scarcity. But there is a question deeper than the amount of information: **even if the information on both axes keeps growing, there is no guarantee that our coverage of the latent payoff matrix becomes more complete.** The observations may keep concentrating in regions that are already well understood, while other regions remain untouched.

For example, a platform may have millions of user-behavior records, but most come from a small number of popular products and active users. For inactive users, new products, or rare user–product combinations, we may still have almost no reliable observations. The platform holds more and more data, yet does not necessarily know more about these blind spots. More importantly, these blind spots are not necessarily randomly distributed. Active experiments tend to be allocated to products that currently look promising, and organic traffic is usually concentrated on products that already have some visibility. This means that two seemingly different information-acquisition mechanisms may produce highly overlapping data in the same regions and leave gaps in the same regions. What we end up with is an information system with a huge sample size but potentially severe structural missingness.

This brings to mind a distinction: **Information Volume and Information Coverage are not the same thing.** If ten thousand observations all come from the same kind of user, they can let us estimate that group's behavior very accurately, but they cannot automatically tell us how other groups will respond. Even if the two observation mechanisms are statistically independent in their noise, they may be measuring the same direction of the latent payoff structure. Conversely, a single observation from a previously uncovered population adds only one sample, but it may reveal a dimension that could not be identified from the existing data. The value of information therefore cannot be measured only by sample size or variance reduction; we must also consider what the new information adds relative to what we already have.

The linear-algebra language makes this clearer. Suppose the unknown parameter we care about is a vector $\theta$, and the active and passive observations can be approximated respectively as

$$
X=A\theta+\epsilon_D,\qquad
Y=B\theta+\epsilon_P.
$$

Here $A$ and $B$ describe which linear combinations of the latent parameter each of the two observation mechanisms can see. Even if we increase the number of observations without limit, if $A$ and $B$ keep measuring the same parameter directions, the system can retain unidentifiable degrees of freedom. In the idealized linear, noiseless setting, this unidentifiable structure is captured by the common null space:

$$
\mathcal N=\ker(A)\cap\ker(B).
$$

If there is a nonzero direction $v\in\mathcal N$, then $\theta$ and $\theta+v$ may generate exactly the same two kinds of observations. No matter how many samples each source accumulates, we cannot tell them apart from these observations alone. What really deserves attention is no longer just how much data each source has, but whether the two observation mechanisms, taken together, eliminate the unidentifiable directions that matter for the decision at hand.

The Unknown Mapping example in the paper is in fact the most compact version of this unidentifiability: in Example 2, two environments with different true rewards can produce exactly the same auxiliary-information distribution, so no amount of auxiliary data can distinguish them. (The matrices and null space above are my own extension, not part of the paper's model.) **Data scarcity is sometimes not a statistical problem, but a problem of the observation mechanism being unable to distinguish certain states of the world.**

Of course, we do not need to eliminate every unidentifiable direction. If two worlds consistent with the data both say that A is better than B, this uncertainty does not affect the action; unidentifiability matters only when the two worlds give different answers about the optimal action. So the question can be posed directly: **in a highly sparse observation system, which observations should we add in order to remove the decision-relevant unidentifiability as quickly as possible?**

The difficulty is that real observation systems tilt themselves in one direction. A recommender keeps recommending products that already perform well, so those products keep gaining new reward data; search traffic also follows exposure and popularity. Products that are not recommended receive less direct feedback and less indirect information together. **An algorithm may become more and more accurate in the regions it is already familiar with, yet, having never truly observed the others, mistakenly believe it understands the whole decision space.** (Gur and Momeni assume that the arrival of auxiliary information is exogenous; this kind of Endogenous Information Arrival, where actions influence future observations, is exactly the extension the authors point to in their discussion of future research.)

In today's AI training, this is no longer just an efficiency issue, but an ethical one. Training data for large models comes mostly from the internet, and internet text is heavily concentrated in a few mainstream languages and mainstream groups. Languages and viewpoints with many users keep producing new data, so the model performs better on them, more people use it, and still more data is produced, forming a data flywheel. Minority languages and minority viewpoints go the opposite way: little data, poor model performance, fewer users, and even less data, until they gradually become islands of data. The model's overall loss goes down and its benchmark scores go up, yet its understanding of these groups may have barely improved. And these voices are not unimportant just because there are few of them: the knowledge carried in a language with few speakers, or the firsthand experience of a minority group, is exactly what mainstream data cannot replace.

In terms of the framework above, data that naturally arises on the internet is passive observation. Its distribution is determined by population size, economic conditions, and the degree of digitization, so it is inherently skewed toward the mainstream. If we merely wait for passive data to grow, the islands will only become more isolated. What is needed is the active-experiment side: deliberately acquiring data that will not arrive on its own, for instance by collaborating with minority-language communities to collect corpora, building dedicated evaluations for the groups on which the model performs poorly, or giving scarce but distinctive data higher weight during training. The goal is not to give every group the same amount of data, but to fill in the directions that the model currently cannot see at all and that affect how it treats a group of people. This is consistent with the earlier line of thought: the value of information lies not in how much there is, but in what it fills in.

Following this logic, I ended up with a question that differs from the original paper but arises naturally from it: can we treat the information-acquisition process of an intelligent system as an object to be optimized? The system does not need to fill in every cell of the latent payoff matrix, nor estimate every unknown parameter precisely; what it needs is a set of observations, as small as possible, that is still sufficient to distinguish the key decisions. Passive information keeps arriving and continually changes the set of feasible worlds, while active experiments have the chance, when necessary, to obtain the critical evidence that existing information cannot provide. The real optimization objective is not to maximize the total amount of information, but to reduce, under limited cost, those unknowns that could change the optimal action. Such an observation structure can be highly sparse, but it must cover the key directions that determine which actions are better. It has some conceptual connections to model compression, sparse representation, and experimental design, except that what is being compressed here is not the data itself but the knowledge required for effective decisions.

So, looking back at this paper, I think the most important lesson of Auxiliary Information may be not just how many active pulls it can save, but that it makes us question the assumptions that traditional learning models make about how information is acquired. In the real world, we do not face a world that can be freely and completely observed, but a sparse information structure formed jointly by different observation mechanisms, selection bias, unknown mappings, and historical decisions. How to make decisions within such an incomplete structure is more fundamental than how to use more data.

---

**Paper:** Yonatan Gur and Ahmadreza Momeni, *Adaptive Sequential Experiments with Unknown Information Arrival Processes*. [arXiv:1907.00107](https://arxiv.org/abs/1907.00107)

*Note: This article was translated from Chinese by AI, and the language was polished with AI assistance.*
