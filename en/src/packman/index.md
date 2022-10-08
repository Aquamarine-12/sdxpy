---
title: "A Package Manager"
syllabus:
- FIXME
---

## Exhaustive Search {: #packman-exhaustive}

-   Specify package dependencies

[% inc file="triple.py" %]

-   Generate possibilities and then see which ones fit constraints

[% inc file="exhaustive.py" keep="main" %]

-   Generate possibilities with recursive enumeration

[% inc file="exhaustive.py" keep="possible" %]

-   Check for compatibility

[% inc file="exhaustive.py" keep="compatible" %]

-   18 possibilities reduce to 3 valid combinations

[% inc file="exhaustive.out" %]

## Incremental Search {: #packman-incremental}

-   Can we thin out possibilities as we go?
    -   Reverse the search order to make a point later

[% inc file="incremental.py" keep="main" %]

-   Check compatibility so far as we go

[% inc file="incremental.py" keep="find" %]

-   Search in the order keys are given

[% inc pat="incremental.*" fill="sh out" %]

-   Search in reverse order

[% inc pat="incremental_reverse.*" fill="sh out" %]

## Exercises {: #packman-exercises}

FIXME
