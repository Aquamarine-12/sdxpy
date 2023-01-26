---
title: "A Package Manager"
todo: true
syllabus:
-   Software packages often have multiple versions, which are usually identified by multi-part semantic version numbers.
-   A package manager must find a mutually-compatible set of dependencies in order to install a package.
-   Finding a compatible set of packages is equivalent to searching a multi-dimensional space.
-   The work required to find a compatible set of packages can grow exponentially with the number of packages.
-   Eliminating partially-formed combinations of packages can reduce the work required to find a compatible set.
-   An automated theorem prover can determine if a set of logical propositions can be made consistent with each other.
-   Most package managers use some kind of theorem prover to find compatible sets of packages to install.
---

There is no point building software if you can't install it.
Inspired by the [%i "Comprehensive TeX Archive Network" %]Comprehensive TeX Archive Network[%/i%]
([CTAN][ctan]),
most languages have an online archive from which developers can download packages.
[Michael Reim's][reim_michael] [history of Unix packaging][unix_packaging]

Each package typically has a name and one or more versions;
each version may have a list of dependencies,
and the package may specify a version or range of versions for each dependency.
Installing the files in a package
is mostly a matter of copying them to the right places.
Before then,
though,
we need to figure out exactly what versions of different packages to install
in order to create a consistent setup.
If A and B require different versions of C,
it might not be possible to use A and B together.

Installing every package's dependencies separately isn't an option:
if A uses one version of C and B uses another in the same program,
the results are going to be inconsistent at best.
This chapter therefore explores how to find a workable installation or prove that there isn't one.
It is based in part on [this tutorial][package_manager_tutorial]
by [%i "Nison, Maël" %][Maël Nison][nison_mael][%/i%]
and on [Andreas Zeller's][zeller_andreas]
lecture on [academic prototyping][academic_prototyping].

## Semantic Versioning {: #packman-semver}

Most software projects use
[%i "semantic versioning" %][%g semantic_versioning "semantic versioning" %][%/i%]
for software releases.
Each version is three integers X.Y.Z,
where X is the major version,
Y is the minor version,
and Z is the [%i "patch" "semantic versioning!patch" %][%g patch "patch" %][%/i%].
(The [full specification][semver_spec] allows for more fields,
but we will ignore them in this tutorial.)

A package's authors increment its major version number
when a change to the package breaks
[%i "backward compatibility" %][%g backward_compatible "backward compatibility" %][%/i%].
For example,
if the new version adds a required parameter to a function,
then code built for the old version will fail or behave unpredictably with the new one.
The minor version number is incremented when new functionality won't break any existing code,
and the patch number is changed for bug fixes that don't add any new features.

The notation for specifying ranges of versions looks like arithmetic:
`>=1.2.3` means "any version from 1.2.3 onward",
`<4` means "any version before 4.anything",
and `1.0-3.1` means "any version in the specified range (including patches)".
Note that version 2.1 is greater than version 1.99:
no matter how large a minor version number becomes,
it never spills over into the major version number.

It isn't hard to write a few simple comparisons for semantic version identifiers,
but getting all the cases right is almost as tricky as handling dates and times correctly.
Our examples therefore number versions with plain integers;
we recommend the [semantic-version][py_semver] package
for working with the real thing.

## Exhaustive Search {: #packman-exhaustive}

To avoid messing around with parsers,
we store the [%i "manifest (of package)" "package manifest" %][%g manifest "manifest" %][%/i%]
of available packages as JSON:

[% inc file="triple.json" %]

<div class="callout" markdown="1">

### Comments

If you ever design a data format,
please include a standard way for people to add comments,
because they will always want to.
YAML has this,
but JSON and CSV don't.

</div>

Imagine that each package we need is an axis on a multi-dimensional grid
([%f packman-allowable %]).
Each point on the grid is a possible combination of package versions.
We can exclude regions of this grid using the constraints on the package versions;
whatever points are left when we're done represent legal combinations.

[% figure
   slug="packman-allowable"
   img="packman_allowable.svg"
   alt="Allowable versions"
   caption="Finding allowable combinations of package versions."
%]

How much work is it to check all of these possibilities?
Our example has 3×3×2=18 combinations.
If we were to add another package to the mix with 2 versions,
the [%i "search space" %][%g search_space "search space" %][%/i%] would double;
add another,
and it would double again.
This behavior is called a [%i "combinatorial explosion" %][%g combinatorial_explosion "combinatorial explosion" %][%/i%],
and it means that brute force solutions are impractical
even for small problems.
We will implement it as a starting point
(and to give us something to test more complicated solutions against),
but then we will need to find a more efficient approach.

<div class="callout" markdown="1">

### Reproducibility

There may not be a strong reason to prefer one mutually-compatible set of packages over another,
but a package manager should resolve the ambiguity the same way every time.
It might not be what everyone wants,
but at least they will be unhappy for the same reasons everywhere.
This is why `pip list` (and similar commands for other package managers)
produce a listing of the exact versions of packages that have been installed:
a spec written by a developer that lists allowed ranges of versions specifies what we *want*,
while the listing created by the package manager specifies exactly what we *got*.
If we want to reproduce someone else's setup for debugging purposes,
we should install what is described in the latter file.

</div>

Our brute-force program generates all possible combinations of package versions,
then eliminates ones that aren't compatible with the manifest.
Its main body is just those steps in order
with a few `print` statements to show the results:

[% inc file="exhaustive.py" keep="main" %]

To generate the possibilities,
we create a list of the available versions of each package,
then use Python's [itertools][py_itertools] module
to generate the [%g cross_product "cross product" %]
that contains all possible combinations of items
([%f packman-product %]):

[% inc file="exhaustive.py" keep="possible" %]

[% figure
   slug="packman-product"
   img="packman_product.svg"
   alt="Generating a cross-product"
   caption="Generating all possible combinations of items."
%]

To check a candidate against the manifest,
we compare every entry X against every other entry Y:

1.  If X and Y are the same package, we keep looking.
    We need this rule because we're comparing every entry against every entry,
    which means we're comparing package versions to themselves.
    We could avoid this redundant check by writing a slightly smarter loop,
    but there's no point optimizing a horribly inefficient algorithm.

2.  If package X's requirements say nothing about package Y,
    we keep searching.
    This rule handles the case of X not caring about Y,
    but it's also the reason we need to compare all against all,
    since Y might care about X.

3.  Finally, if X does depend on Y,
    but this particular version of X doesn't list this particular version of Y
    as a dependency,
    we can rule out this combination.

4.  If we haven't ruled out a candidate after doing all these checks,
    we add it to the list of allowed configurations.

The code that implements these rules is:

[% inc file="exhaustive.py" keep="compatible" %]

Sure enough,
it finds 3 valid combinations among our 18 possibilities:

[% inc file="exhaustive.out" %]

## Generating Possibilities Manually {: #packman-manual}

Our brute-force code uses `itertools.product`
to generate all possible combinations of several lists of items.
To see how it works,
and to lay the ground for a more efficient algorithm,
let's write `make_possibilities` to use a function of our own:

[% inc file="manual.py" keep="start" %]

The first half creates the same list of lists as before,
where each sub-list is the available versions of a single package.
It then creates an empty [%g accumulator "accumulator" %]
to collect all the combinations
and calls a recursive function called `_make_possible` to fill it in.
{: .continue}

Each call to `_make_possible` handles one package's worth of work
([%f packman-recursive %]).
If the package is X,
the function loops over the available versions of X,
adds that version to the combination in progress,
and calls itself with the remaining lists of versions.
If there aren't any more lists to loop over,
the recursive calls must have included exactly one version of each package,
so the combination is appended to the accumulator.

[% inc file="manual.py" keep="make" %]

[% figure
   slug="packman-recursive"
   img="packman_recursive.svg"
   alt="Generating a cross-product recursively"
   caption="Generating all possible combinations of items recursively."
%]

`_make_possible` uses recursion instead of nested loops
because we don't know how many loops to write.
If we knew the manifest only contained three packages,
we would write a triply-nested loop to generate combinations,
but if there were four,
we would need a quadruply-nested loop,
and so on.
This [%i "Recursive Enumeration pattern" %][%g recursive_enumeration_pattern "Recursive Enumeration" %][%/i%]
design pattern
uses one recursive function call per loop
so that we automatically get exactly as many loops as we need.

## Incremental Search {: #packman-incremental}

Generating an exponentiality of combinations
and then throwing most of them away
is not an efficient way to search.
Instead,
we can modify the recursive generator
to stop if a partially-generated combination of packages isn't legal.
Combining generation and checking made the code more complicated,
but as we'll see,
it leads to some significant improvements.

The main function for our modified program
is similar to its predecessor.
After loading the manifest,
we generate a list of all the packages' names.
Unlike our earlier code,
the entries in this list don't include versions
because we're going to be checking those as we go:

[% inc file="incremental.py" keep="main" %]

Notice that if the user provides a command-line argument,
we reverse the list of packages before starting our search.
Doing this will allow us to see how ordering affects efficiency.
{: .continue}

Our `find` function now has five parameters:

1.  The manifest that tells us what's compatible with what.

2.  The names of the packages we've haven't considered yet.

3.  An accumulator to hold all the valid combinations we've found so far.

4.  The partially-completed combination we're going to extend next.

5.  A count of the number of combinations we've considered so far,
    which we will use as a measure of efficiency.

[% inc file="incremental.py" keep="find" %]

The algorithm combines the generation and checking we've already written:

1.  If there are no packages left to consider—i.e.,
    if `remaining` is an empty list—then
    what we've built so far in `current` must be valid,
    so we append it to `accumulator`.

2.  Otherwise,
    we put the next package to consider in `head`
    and all the remaining packages in `tail`.
    We then check each version of the `head` package in turn.
    If adding it to the current collection of packages
    wouldn't cause a problem,
    we continue searching with that version in place.

How much work does incremental checking save us?
Using the same test case as before,
we only create 11 candidates instead of 18,
so we've reduced our search by about a third:

[% inc pat="incremental.*" fill="sh out" %]

If we reverse the order in which we search,
though,
we only generate half as many candidates as before:
{: .continue}

[% inc pat="incremental_reverse.*" fill="sh out" %]

## Using a Theorem Prover {: #packman-smt}

Cutting the amount of work we have to do is good:
can we do better?
The answer is yes,
but the algorithms involved quickly become complicated,
as does the jargon.
To show how real package managers tackle this,
we will solve our example problem using the [Z3 theorem prover][z3].

Installing packages and proving theorems
may not seem to have a lot to do with each other,
but an automated theorem prover's purpose is
to determine if a set of logical propositions can be consistent with each other,
and that's exactly what we need.
To start,
let's import a few things from the `z3` module
and then create three Boolean variables:

[% inc file="z3_setup.py" %]

Our three variables don't have values yet—they're not
either true or false.
Instead,
each one represent all the possible states a Boolean could be in.
If we had asked `z3` to create one of its special integers,
it would have given us something that initially encompassed
all possible integer values.

Instead of assigning values to `A`, `B`, and `C`,
we can specify constraints on them,
then ask `z3` whether it's possible to find a set of values,
or [%g model "model" %],
that satisfies all those constraints at once.
In the example below,
we're asking whether it's possible for `A` to equal `B`
and `B` to equal `C` at the same time.
The answer is "yes",
and the solution the solver finds is to make them all `False`:

[% inc pat="z3_equal.*" fill="py out" %]

What if we say that `A` and `B` must be equal,
but `B` and `C` must be unequal?
In this case,
the solver finds a solution in which `A` and `B` are `True`
but `C` is `False`:

[% inc file="z3_part_equal.py" keep="solve" %]
[% inc file="z3_part_equal.out" %]

Finally,
what if we require `A` to equal `B` and `B` to equal `C`
but `A` and `C` to be unequal?
No assignment of values to the three variables
can satisfy all three constraints at once,
and the solver duly tells us that:

[% inc file="z3_unequal.py" keep="solve" %]
[% inc file="z3_unequal.out" %]

Theorem provers like Z3 and [PicoSAT][picosat]are powerful tools.
We can,
for example,
use them to generate test cases.
Suppose we have a function that classifies triangles as equilateral,
scalene,
or isosceles.
We can set up some integer variables:

[% inc file="equilateral.py" keep="setup" %]

and then ask it to create an equilateral triangle
based solely on the definition:
{: .continue}

[% inc file="equilateral.py" keep="equilateral" %]
[% inc file="equilateral.out" %]

The same technique can generate a test case for scalene triangles:

[% inc file="scalene.py" keep="scalene" %]
[% inc file="scalene.out" %]

and isosceles triangles:
{: .continue}

[% inc file="isosceles.py" keep="isosceles" %]
[% inc file="isosceles.out" %]

Let's return to package management.
We can represent the package versions from our running example like this:

[% inc file="z3_triple.py" keep="setup" %]

We then tell the solver that we want one of the available version of package A:

[% inc file="z3_triple.py" keep="top" %]

We also tell it that the three version of package A are mutually exclusive:

[% inc file="z3_triple.py" keep="exclusive" %]

We need equivalent statements for packages B and C;
we'll explore in the exercises
how to generate all of these from a package manifest.
{: .continue}

Finally,
we add the inter-package dependencies
and search for a result:

[% inc file="z3_triple.py" keep="depends" %]
[% inc file="z3_triple.out" %]

The output tells us that the combination of A.3, B.3, and C.2
will satisfy our constraints.
{: .continue}

We saw earlier,
though,
that there are three solutions to our constraints.
One way to find the others is to ask the solver
to solve the problem again
with the initial solution ruled out.
We can repeat the process many times,
adding "not the latest solution" to the constraints each time
until the problem becomes unsolvable:

[% inc file="z3_complete.py" keep="all" %]
[% inc file="z3_complete.out" %]

## Summary {: #packman-summary}

[% figure
   slug="packman-concept-map"
   img="packman_concept_map.svg"
   alt="Concept map for package manager."
   caption="Concepts for package manager."
%]

## Exercises {: #packman-exercises}

### Comparing semantic versions {: .exercise}

Write a function that takes an array of semantic version specifiers
and sorts them in ascending order.
Remember that `2.1` is greater than `1.99`.

### Parsing semantic versions {: .exercise}

Using the techniques of [%x matching %],
write a parser for a subset of the [semantic versioning specification][semver_spec].

### Using scoring functions {: .exercise}

Many different combinations of package versions can be mutually compatible.
One way to decide which actual combination to install
is to create a [%g scoring_function "scoring function" %]
that measures how good or bad a particular combination is.
For example,
a function could measure the "distance" between two versions as:

-   100 times the difference in major version numbers;

-   10 times the difference in minor version numbers
    if the major numbers agree;
    and

-   the difference in the patch numbers
    if both major and minor numbers agree.

1.  Implement this function
    and use it to measure the total distance between
    the set of packages found by the solver
    and the set containing the most recent version of each package.

2.  Explain why this doesn't actually solve the original problem.

### Regular releases {: .exercise}

Some packages release new versions on a regular cycle,
e.g.,
Version 2021.1 is released on March 1 of 2021,
Version 2021.2 is released on September 1 of that year,
version 2022.1 is released on March 1 of the following year,
and so on.

1.  How does this make package management easier?

2.  How does it make it more difficult?

### Searching least first {: .exercise}

Rewrite the constraint solver so that it searches packages
by looking at those with the fewest available versions first.
Does this reduce the amount of work done for the small examples in this chapter?
Does it reduce the amount of work done for larger examples?

### Using exclusions {: .exercise}

1.  Modify the constraint solver so that
    it uses a list of package exclusions instead of a list of package requirements,
    i.e.,
    its input tells it that version 1.2 of package Red
    can *not* work with versions 3.1 and 3.2 of package Green
    (which implies that Red 1.2 can work with any other versions of Green).

2.  Explain why package managers aren't built this way.

### Generating constraints {: .exercise}

Write a function that reads a JSON manifest describing package compatibilities
and generates the constraints needed by the Z3 theorem prover.

### Buildability {: .exercise}

1.  Convert the build dependencies from one of the examples in [%x builder %]
    to a set of constraints for Z3
    and use the solution to find a legal build order.

2.  Modify the constraints to introduce a [%g circular_dependency "circular dependency" %]
    and check that the solver correctly determines
    that there is no legal build order.
