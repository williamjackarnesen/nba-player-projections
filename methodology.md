## Welcome to the NBA Player Projection Model

Welcome to the inaugural edition of the NBA Model, where we use simple machine-learning techniques to project NBA performance for the 2020-21 season. In this post, we will cover the basics of the model.


## 1.0 How does it work?


### 1.1 Encoding player abilities

All player projection models require assigning to each player some vector of abilities. Don’t let the math terms deter you: even the most casual of analyses uses these vectors, even if they don’t use the term. ESPN’s Real-Plus Minus, for instance, assigns each player with a two-dimension vector with their Offensive RPM and their Defensive RPM. The traditional box score of associating a player with points, rebounds, assists, blocks etc. is just a vector with more entries.

We want to capture as much information about a player as we can, so we take in 19 pieces of information from each box score: minutes played, two-point field goals made, two-point field goals attempted, three pointers made and attempted, free throws, free throws attempted, assists, rebounds, blocks, etc. We also include Team Defensive Rating (how many points does your opponent score per 100 possessions when you are on the court) to match the intution that traditional defensive metrics (rebounds, blocks and steals) capture only a tiny fraction of a player's real defensive impact. 

Unfortunately, describing a player with a nineteen-dimensional vector has a few well-documented downsides. First, you risk ¬over-fitting, a.k.a. matching your data extremely well but having terrible predictive value. To take a trivial example, suppose you flipped a coin once a day every day for five years and you wanted to predict the results of tomorrow’s coin toss. With enough data, you could probably find some spurious correlations that say it’s slightly more likely to be heads on Tuesday and Friday, and slightly more likely to be tails on days Tesla stock rises. But those correlations are obviously bogus. Given a million variables, you’d probably find one that seems to match up well by sheer random chance. But if you used those to predict future results, you’d do worse than someone who just picked perfectly randomly every time. So we want to reduce the amount of parameters we are taking in.

Second, we want to increase parameter sharing. While a similar concept to over-fitting, maximizing parameter sharing is about trying to avoid missing the forest for the trees. You want to capture the overall gist of the player more than focusing on individual features. For example, if one player has a bad on-off plus-minus and another player with a quite similar profile has a good one, we probably think both players are similarly talented and those variations just have to do with luck or teammates. With large embeddings (numerical descriptions), notions of similarity are less obvious (e.g. if two players are similar in ten stats but very different in ten others, we might naively think they’re wildly different players if we didn’t know that those final ten stats were highly correlated or perhaps irrelevant to winning). As such, it is harder to generalize players with ultra-long embeddings.

As a result, we choose to reduce our nineteen parameters down to a mere four. It’s worth noting that these four numbers defies simple categorization. There is no literal “scoring number” or “defensive number”. Instead, these numbers are more of a black-box that capture the gist of a player, even if they aren’t the most interpretable to the naked eye.

## 1.2 Determining the player encodings

We want to teach the model to learn these numerical values. But to do so, we need a training target, i.e. what are these encodings trying to capture. There are a lot of possible candidates, but we decided on on-off plus-minus. Plus-minus refers to the difference between how much your team scored and how much your opponent scored while you were on the court, while on-off plus-minus to the difference between the plus-minus for the minutes you are on the court and the plus-minus when you are off the court. We standardize the plus-minus on a per-minute rate to capture the fact that starters will spend a lot more minutes on the court than off and we exclude anyone with less than ten minutes played for fear that the sample size is too small.

## 1.2.1 Choosing a training target

On-off plus-minus carries a few strategic advantages. In particular, it allows you to isolate for a player’s individual contribution as distinct from the rest of your team. For example, if you targeted amount mere plus-minus, a good score could equally reflect individual talent as well as the talent of one's teammates. Suppose a team won by 50 points. During the 24 minutes a given player was on the court, the team outscored their opponent by 10, but during the 24 they were on the bench, they won by a net of 40. Plus-minus alone would suugest that the player was excellent, but clearly the team did better when they were on the bench! Likewise, we don’t want to penalize players who had negative net negatives because their team is bad. In addition, the stat allows us to capture some hidden characteristics, such as how you help others score. Some players may shoot at low volumes, but because of their shooting prowess, they may be helping other players score by improving a team’s spacing. Focusing on team outcomes thus helps you capture that nuance.

Some may argue that this target penalizes players with an excellent bench. For example, a good player may have a mediocre on-off plus-minus because their replacement is also quite good. However, this criticism misunderstands how the process works. This model assigns you to a good score if you have the statistical profile of someone who likely has a good on-off plus-minus. Thus even if the particulars of a given team mute your stats, that wouldn’t harm you in these metrics.

## 1.2.2 Training the model

Now that we know what we’re optimizing for, we need to build up this network. In simple terms, this two-layer network does the following steps:

1. Reduces the 20 inputs from the box score down to four elements
2. Map Reduce those four elements down to a predicted on-off plus-minus

At first, the computer will randomly generate a series of four numbers and pass it to predict the on-off plus-minus for a given player in a given game. Obviously, this prediction will be terrible at first. The model will then update in the direction of the error as it takes in game after game. As more games come in, the update direction will get smaller and smaller, until the updates become imperceptible and the data has ‘converged’.

So now we need to update our estimates of the player’s skills. Suppose LeBron James has a vector of [0 0 0 0] and his newest game was a performance of [3 4 -2 7] (these are arbitrary numbers—in reality, since we normalized our input data, the numbers are much smaller). The update function will thus update his vector to be closer towards his nearest performance by increasing his first two numbers, slightly lowering his third number, and substantially increasing his fourth. Obviously, we don’t want to move too aggressively towards to new value, as a few great games from a scrub would hardly make him a star no more than a few rough games from James Harden would make him a scrub. Instead, we chose to weight each new one by 1/3√(games played) based on the idea that we should probably update our estimates of a young player more dramatically with each new game than someone with a long resumé. A second-year player with 100 games under his belt would thus have completely replaced his rating in about 30 games, whereas a veteran with 500 games under his belt would replace his over the course of a full season.




