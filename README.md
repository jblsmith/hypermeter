# Modelling odd meters
*2018 HAMR project on discovering and handling situations that lead to downbeat errors*

## Goal
Detect time signature changes

- "Lucy in the Sky with Diamonds" (The Beatles): the song alternates between verses in 3/4 time and choruses in 4/4.
  - Bar lengths: 3, 3, 3, 3, ..., 3, 3, 4, 4, ... 4, 4, 3, 3, ..., 3, 3, 4, 4, ...
- "Hey Ya!" (Outkast): the time signature is 4/4, but in every 6-bar phrase, the 4th bar is cut short.
  - Bar lengths: [4, 4, 4, 2, 4, 4], [4, 4, 4, 2, 4, 4], [4, 4, 4, 2, 4, 4], ...
- "The Stars" (Jukebox the Ghost): time signature is 4/4, but there are two beats missing in the entire song.
  - Bar lengths: 4, 4, 4, 4, 4, ..., 4, 4, 3, 4, 4, ..., 4, 4, 3, 4, 4, ..., 4, 4, 4.

These unusual situations are likely to lead to beat- or downbeat-tracking errors.

These types of situations are not rare; in a corpus of 180 Beatles songs,
56 annotations have measures of non-uniform length.

## Problem

It's easy to track a typical beat sequence:
```
     1  2  3  4  1  2  3  4  1  2  3  4  1  2  3  4  ...    <- true beats
    [1  2  3  4][1  2  3  4][1  2  3  4][1  2  3  4] ...    <- downbeat groupings
```

Naive beat tracking on a unusual beat sequence leads to "phase" errors:
```  
     1  2  3  4  1  2  3  4  1  2  3  1  2  3  4  1  2  3  4  1  ...    <- true beats
    [1  2  3  4][1  2  3  4][1  2  3  1][2  3  4  1][2  3  4  1] ...    <- naive downbeat groupings
    [1  2  3  4][1  2  3  4][1  2  3][1  2  3  4][1  2  3  4][1  ...    <- true downbeat groupings
```

## Method 1

Insert DDF image here, to demonstrate interesting change

Hypothesis: when comparing the downbeat detection function (DDF) of Madmom (or whatever feature) will be more similar 

Motivating example: suppose there is a song in 4/4, with a single beat missing --- a single measure in 3.
  - A b c d A b c d A b c d A b c A b c d A b c d 

If you group the downbeats correctly, you should find that every measure resembles every other measure:
  - [A b c d] [A b c d] [A b c d] [A b c] [A b c d] [A b c d]
  - Every [Abcd] is similar to every other [Abcd], and they will sort of look like [Abc] too.

But if you group the downbeats and don't detect the strange bar, your bars will get out of phase:
  - [A b c d] [A b c d] [A b c d] [A b c A] [b c d A] [b c d A] [b c d A]
  - The [Abcd] sections resemble each other
  - The [bcdA] sections resemble each other
  - But [Abcd] doesn't resemble [bcdA]

We can build a representation that t


X = [1234]
Y = [2341]
Z = [3412]

Naive approach one:
  X     X     X   X    Y    Y Y Y Z Z Z 
[1234][1234][...][2341][2341]

Approach two:
Y Y Y Y Z Z Z Z W W W W X X X X
  
  
  
Label abcd=abcd
bcda=bcda
abcda = bcda - 1


  - **1**234**1**234**1**234**1**234**1**234**1**234**1**234**1**23**1**234**1**234**1**234**1**234

Step 1: do naive downbeat tracking with all possible phase offsets:

I.e.:
[....][....][....][....][....]
.[....][....][....][....][....]
..[....][....][....][....][....]
...[....][....][....][....][....]
....[....][....][....][....][....]
```  
     1  2  3  4  1  2  3  4  1  2  3  1  2  3  4  1  2  3  4  1  ...    <- true beats
    [1  2  3  4][1  2  3  4][1  2  3  1][2  3  4  1][2  3  4  1] ...    <- 
    [1  2  3  4][1  2  3  4][1  2  3][1  2  3  4][1  2  3  4][1  ...    <- true downbeat groupings
```

## Method 2

We start from the same DDF, and try to directly infer the temporal positions of downbeats, through peak picking based on thresholds and particular rules.

This idea has been only experimented on particular pieces of music so far, and will be explained on those particular examples.

### Hey Ya

We select the peaks of amplitude higher than 0.33. We get a first estimation of downbeats. This shows that we have series of two 4-beat bars, one 6-beat bar, and two other 4-beat bars, this repeated again and again.

The problem is that sometimes, instead of finding the 6-beat bar, we find a succession of 4-beat and 2-beat bars. This shows the limitation of a global thresholding (set to 0.33 above).

The strategy then is to try to find heuristics, as general as possible, that could help detecting that 6-beat bars and 4-beat bar followed by 2-beat bars can be considered as the same thing.

The proposed heuristic is: let’s suppose we have a succession of N-beat bars, followed by a single M-beat (with M<N), and then followed by a another sequence of bars, then the smaller bar is fused to one of the two neighbour bars. We select the neighbour bar where the DDF value in between is the lower, indicating that the separation between the two bars is the most ambiguous.

(We compute the difference between successive downbeats, expressed in number of beats. For this, we need the temporal beat grid: we suppose constant tempo and find the inter beat duration as the temporal distance between the two first peaks found in the detection function (using a peak picking with no absolute threshold but a contrast threshold of 0.01).)

Using this heuristics, we obtain a clearer structure of the song.

### Love Is All

The threshold for peak picking is set to 0.2.

Without the heuristics, we get the desired structure.

The heuristics provokes an incorrect fusion at the transition between 4-beat and 3-beat bars.

## Facts about music
- time signature changes are cool
- lots of songs have time signature changes, not just obscure art rock songs!


1. unusual isolated measures (The Stars)
2. time signature change (LSD)
3. Unusual (Hey Ya)


