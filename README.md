# Tennis Elo Simulations

Make predition on the outcome of a tennis tournament based on players surface specific [Elo](https://en.wikipedia.org/wiki/Elo_rating_system) ranking.
By providing a draw/bracket and the latest Elo ranking the simulator performs Monte-Carlo run of the tournament the estimate the likelihood of each player tournament progression.

*Currently the Elo rating are extracted from [TennisAbstract](http://www.tennisabstract.com/blog/).*

## TODO

- [ ] Update Elo after tournament
- [ ] Remove 'bye' players from results
- [ ] Get surface from tournament draw instead of input

## Source of insperation

The main inspiration and original code comes from the work of [Jeff Sackmann](http://www.jeffsackmann.com/).
He maintains a whole website with a [tennis statistics](http://www.tennisabstract.com/) and [blog](http://www.tennisabstract.com/blog/).
Some of his early code which was used as base for this work is also available on his [GitHub](https://github.com/JeffSackmann).

## License

This work is license under *GPLv3* to be compatible with the origanl work which is licensed under *CC BY-NC-SA 4.0*.