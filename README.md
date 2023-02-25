# Shannon's Bird Cage

A connection game, also known as Bridg-It, or the Shannon Switching Game.

## Introduction

Quoting from "Hex: The Full Story" by Ryan B. Hayward (p119):

> The Shannon switching game is played on a graph with two special nodes. One player is Cut, the other Short. On her turn, Cut breaks (or erases) any unmarked link. On his turn, Short marks any unbroken link. The game ends either when the two special nodes are joined by a path of marked links - so Short wins - or the special nodes have been separated into different components - so Cut wins.

Bird Cage is the Shannon Switching Game played on a graph that looks like a bird cage. The two special nodes are marked 0 and Q.

![Bird Cage circuit start](birdcage_move0.png)

It is drawn as an electrical circuit, since Shannon built a machine using resistors to play Bird Cage.

Imagine that Cut removes the resistor at top left, then Short replaces the resistor at top centre with a wire. The resulting position is then

![Bird Cage circuit move 2](birdcage_move2.png)

Play continues until there is a short circuit (Short wins), or the circuit is such that zero current flows (Cut wins).

## Shannon's Heuristic

Shannon's machine plays as Cut, and simply selects the resistor that has the largest current flow. (Equivalently, since all the resistors are the same, select the resistor with the largest voltage drop across it.)

His machine was for the M=4 version of the game, which is 4 links wide. (Rather than 3 shown above.)

This simple heuristic plays a good game. According to Shannon (reported by Martin Gardner in "More Mathematical Puzzles and Diversions"):

> Out of hundreds of games played, the machine has had only two losses when it had the first move, and they may have been due to circuit failure or improper playing of the game.

However, it is possible to always beat the machine (M=3 or 4), as shown by Thomas Fisher in "Bridg-It – Beating Shannon’s Analog Heuristic".

## Software implementation

TODO

## Hardware implementation

In a real implementation a couple of practical changes are needed.

First, a resistor should be added in series to the whole circuit, to avoid a real short circuit in the event of Short winning.

Second, it's possible that a part of the circuit can become isolated from both the ground and positive power supply, which means that all nodes in it have a floating voltage. Since voltage differences are used to determine the next move, we use pull-up resistors to ensure that spurious voltage differences are not recorded. By using pull-up resistors with much larger resistance than the ones used in the main circuit, we avoid changing the behaviour of the
heuristic in any significant way. (In a real circuit, small differences in resistor values mean that the machine may not play identically to the theoretical version, but this is rare, and it usually doesn't make much difference.)

## Build

```shell
conda create --name birdcage python=3.9
conda activate birdcage
pip install -r requirements.txt
```
