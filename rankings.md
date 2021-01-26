# Initial Player Rankings

If you're interested in the details of the projection models, follow <a href="https://williamjackarnesen.github.io/nba-player-projections/methodology" title="Methodology">this link</a>.

## Wins above Replacement

![currentwar](https://github.com/williamjackarnesen/nba-player-projections/raw/main/images/current_war.png)

Some technical details about this metric: as explained before, our model outputs a projected points-added from a player being on the court. To convert this into a probability of winning, we take the cumulative distribution function of all margins of victory to see the probability that adding that number of points would flip the possible result. For example, 52% of games are decided by less than a ten point margin. Thus, adding 10 points to a random team adds 26 percentage points to the probability of victory (you must divide by two since there is already a 50% chance the randomly selected team was the winning team already and thus the added points are meaningless). This metric has the added feature of rewarding consistent performance over outlier stellar performances. After all, if a player was to add a (ludicrously large) 60 net points, that team has clearly already won. Adding 40 net points or 60 points is largely a moot point. Thus a player who adds 60 net points in one game and 0 points in five games has about 0.5 WAR. In contrast, a player who adds 10 net points in six games would have just north of 1.5 WAR.

![playerskill](https://github.com/williamjackarnesen/nba-player-projections/raw/main/images/player_skill.png)

The above chart shows expected net points added per minute a player is on the court. Clearly these numbers are similar to but not identical to the wins added metric from above. Some players (like Karl-Anthony Towns) rank highly in skill (#11) but not in performance (#99) by virtue of playing few minutes. In contrast, the algorithm thinks that other players are just under-performing and will probably improve over the course of the season. 

We have included the most-improved and most-regressed players thus far (the metric is projected wins added more or less than theirs projections at season's start--excluding rookies). The different length of lists reflects natural breakpoints to avoid including/excluding players with near-identical scores.

![playergain](https://github.com/williamjackarnesen/nba-player-projections/raw/main/images/Player_Gain.png)

![playerloss](https://github.com/williamjackarnesen/nba-player-projections/raw/main/images/Player_Loss.png)

