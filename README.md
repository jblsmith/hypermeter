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

## Method





## Facts about music
- time signature changes are cool
- lots of songs have time signature changes, not just obscure art rock songs!


1. unusual isolated measures (The Stars)
2. time signature change (LSD)
3. Unusual (Hey Ya)




