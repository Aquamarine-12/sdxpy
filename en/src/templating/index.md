---
title: "A Static Site Generator"
syllabus:
-   Static site generators create HTML pages from templates, directives, and data.
-   A static site generator must have the same core features as a programming language.
-   Programs can use the Visitor pattern to separate traversal of a data structure from operations on its elements.
-   HTML documents are usually represented in memory as trees using the Document Object Model (DOM).
-   The style of code that programmers find easiest to read changes as they become more experienced.
---

Every program needs documentation in order to be usable,
and the best place to put that documentation is on the web.
Writing and updating pages by hand is time-consuming and error-prone,
particularly when many parts are the same,
so most documentation sites use some kind of
[%i "static site generator" %][%g static_site_generator "static site generator" %][%/i%]
to create web pages from templates.

At the heart of every static site generator is a page templating system.
Thousands of these have been written in the last thirty years
in every popular programming language,
and a language called [%i "PHP" %][PHP][php][%/i%] was created primarily for this purpose.
Most of these systems use one of three designs
([%f templating-options %]):

1.  Mix commands in an existing language such as JavaScript with the HTML or Markdown
    using some kind of marker to indicate which parts are commands
    and which parts are to be taken as-is.
    This approach is taken by [%i "EJS" %][EJS][ejs][%/i%].

2.  Create a mini-language with its own commands like [%i "Jekyll" %][Jekyll][jekyll][%/i%].
    Mini-languages are appealing because they are smaller and safer than general-purpose languages,
    but eventually they acquire most of the features of a general-purpose language.
    Again, some kind of marker must be used to show
    which parts of the page are code and which are ordinary text.

3.  Put directives in specially-named attributes in the HTML.
    This approach has been the least popular,
    but since pages are valid HTML,
    it eliminates the need for a special parser.

[% figure
   slug="templating-options"
   img="templating_options.svg"
   alt="Three options for page templates"
   caption="Three different ways to implement page templating."
%]

This chapter builds a simple page templating system using the third strategy.
We will process each page independently by parsing the HTML
and walking the [%i "DOM" %]DOM[%/i%] to find nodes with special attributes.
Our program will execute the instructions in those nodes
to implement loops and if/else statements;
other nodes will be copied as-is to create text.

## Syntax {: #templating-syntax}

Let's start by deciding what "done" looks like.
Suppose we want to turn an array of strings into an HTML list.
Our page will look like this:

[% inc file="loop.ht" %]

The attribute `z-loop` tells the tool to repeat the contents of that node;
the loop variable and the collection being looped over are separated by a colon.
The `span` with the attribute `z-var`
tells the tool to fill in the node with the value of the variable.
When our tool processes this page,
the output will be standard HTML without any traces of how it was created:

[% inc file="loop.out" %]

<div class="callout" markdown="1">

### Human-readable vs. machine-readable

Mini-languages for page templating can quickly become unreadable.
We have already started down that road
by putting the loop variable and loop target in a single attribute
and splitting that attribute to get them out.
Doing this makes loops easy for people to type,
but hides important information from standard HTML processing tools:
they can't know that this particular attribute of these particular elements
contains multiple values
or that those values should be extracted by splitting a string on a colon.
We could instead use two attributes like this:

```html
<ul z-loop="names" z-loop-var="item">
```

but we have decided to save ourselves a little typing.
And strictly speaking
we should call our attributes `data-something` instead of `z-something`
to conform with [%i "HTML5 specification" %][the HTML5 specification][html5-data-attributes][%/i%],
but by the time we're finished processing our templates,
there shouldn't be any `z-*` attributes left to confuse a browser.

</div>

The next step is to define the [%g api "API" %] for filling in templates.
Our tool needs the template itself,
somewhere to write its output,
and some variables to use in the expansion.
These variables might come from a configuration file,
from a YAML header in the file itself,
or from some mix of the two;
for the moment,
we will just pass them into the expansion function as an object:

[% inc file="example_call.py" %]

## Managing Variables {: #templating-values}

As soon as we have variables we need a way to track their values.
We also need to maintain multiple sets of variables
so that (for example) variables used inside a loop
don't conflict with ones used outside it.
As in [%x interpreter %],
we will use a stack of environments,
each of which is a dictionary.

Our stack-handling class `Env` has methods  to push and pop new stack frames
and find a variable given its name.
If the variable can't be found,
`Env.find` returns `None` instead of throwing an exception
([%f templating-stack %]).

[% inc file="env.py" %]

[% figure
   slug="templating-stack"
   img="templating_stack.svg"
   alt="Variable stack"
   caption="Using a stack to manage variables."
%]

## Visiting Nodes {: #templating-nodes}

HTML pages have a nested structure,
so we will process them using
the [%i "Visitor pattern" "design pattern!Visitor" %][%g visitor_pattern "Visitor" %][%/i%] design pattern.
`Visitor`'s constructor takes the root node of the DOM tree as an argument and saves it.
When we call `Visitor.walk` without a value,
it starts recursing from that saved root;
if `.walk` is given a value (as it is during recursive calls),
it uses that instead.

[% inc file="visitor.py" %]

`Visitor` defines two [%g abstract_method "abstract methods" %] `open` and `close`
that are called when we first arrive at a node and when we are finished with it
([%f templating-visitor %]).
Any class derived from `Visitor` must define these two methods.
{: .continue}

[% figure
   slug="templating-visitor"
   img="templating_visitor.svg"
   alt="The Visitor pattern"
   caption="Using the Visitor pattern to evaluate a page template."
%]

The `Expander` class is specialization of `Visitor`
that uses an `Env` to keep track of variables.
It imports handlers for each type of special node—we will write those in a moment—and
uses them to process each type of node:

1.  If the node is plain text, copy it to the output.

1.  If there is a handler for the node,
    call the handler's `open` or `close` method.

1.  Otherwise, open or close a regular tag.

[% inc file="expander.py" omit="skip" %]

To check if there is a handler for a particular node
and get it if there is
we just look at the node's attributes:

[% inc file="expander.py" keep="handlers" %]

Finally, we need a few helper methods to show tags and generate output:

[% inc file="expander.py" keep="helpers" %]

Notice that this class adds strings to an array and joins them all right at the end
rather than concatenating strings repeatedly.
Doing this is more efficient;
it also helps with debugging,
since each string in the array corresponds to a single method call.
{: .continue}

## Implementing Handlers {: #templating-handlers}

At this point
we have built a lot of infrastructure but haven't actually processed any special nodes.
To do that,
let's write a handler that copies a constant number into the output:

[% inc file="z_num.py" %]

The `z_num` expander is a class,
but we don't plan to create instances of it.
Instead,
it's just a way to manage a pair of related `open` and `close` functions,
which we declare as [%i "static method" %][%g static_method "static methods" %][%/i%].
When we enter a node like `<span z-num="123"/>`
this handler asks the expander to show an opening tag
followed by the value of the `z-num` attribute.
When we exit the node,
the handler asks the expander to close the tag.
The handler doesn't know whether things are printed immediately,
added to an output list,
or something else;
it just knows that whoever called it implements the low-level operations it needs.

So much for constants; what about variables?

[% inc file="z_var.py" %]

This code is almost the same as the previous example.
The only difference is that instead of copying the attribute's value
directly to the output,
we use it as a key to look up a value.
{: .continue}

These two pairs of handlers look plausible, but do they work?
To find out,
we can build a program that loads variable definitions from a JSON file,
reads an HTML template using the [Beautiful Soup][beautiful_soup] library,
and does the expansion:

[% inc file="template.py" %]

We added new variables for our test cases one by one
as we were writing this chapter.
To avoid repeating text repeatedly,
here's the entire set:

[% inc file="vars.json" %]

Our first test:
is static text copied over as-is?

[% inc pat="static_text.*" fill="ht out" %]

Good.
Now, does the expander handle constants?

[% inc pat="single_constant.*" fill="ht out" %]

What about a single variable?
{: .continue}

[% inc pat="single_variable.*" fill="ht out" %]

What about a page containing multiple variables?
There's no reason it should fail if the single-variable case works,
but we should still check—again,
software isn't done until it has been tested.

[% inc pat="multiple_variables.*" fill="ht out" %]

## Control Flow {: #templating-flow}

Our tool supports conditional expressions and loops.
Since it doesn't handle Boolean expressions like `and` and `or`,
implementing a conditional is as simple as looking up a variable
and then expanding the node if Python thinks the value is [%g truthy "truthy" %]:

[% inc file="z_if.py" %]

Let's test it:

[% inc pat="conditional.*" fill="ht out" %]

<div class="callout" markdown="1">

### Spot the Bug

This implementation of `if` contains a subtle bug.
The `open` and `close` functions both check the value of the control variable.
If something inside the body of the `if` changes that value,
the result could be an opening tag without a matching closing tag or vice versa.
We haven't implemented an assignment operator,
so right now there's no way for that to happen,
but it's a plausible thing for us to add later,
and tracking down a bug in old code that is revealed by new code
is always a headache.

</div>

Finally we have loops.
For these,
we need to get the array we're looping over from the environment
and do something for each of its elements.
That "something" is:

1.  Create a new stack frame holding the current value of the loop variable.

1.  Expand all of the node's children with that stack frame in place.

1.  Pop the stack frame to get rid of the temporary variable.

[% inc file="z_loop.py" %]

Once again,
it's not done until we test it:

[% inc pat="loop.*" fill="ht out" %]

## How We Got Here {: #templating-learning}

We have just implemented another simple programming language.
It can't do arithmetic,
but if we wanted to add tags like:

```js
<span z-math="+"><span z-var="width"/><span z-num="1"//>
```

we could.
It's unlikely anyone would use the result—typing all of that
is so much clumsier than typing `width+1` that people wouldn't use it
unless they had no other choice—but the basic design is there.
{: .continue}

We didn't invent any of this from scratch,
any more than we invented the simple interpreter in [% x interpreter %].
Instead,
we did what you are doing now:
we read what other programmers had written
and tried to make sense of the key ideas.

The problem is that "making sense" depends on who we are.
When we use a low-level language,
we incur the [%i "cognitive load" %][%g cognitive_load "cognitive load" %][%/i%]
of assembling micro-steps into something more meaningful.
When we use a high-level language,
on the other hand,
we incur a similar load translating functions of functions of functions
into actual operations on actual data.

More experienced programmers are more capable at both ends of the curve,
but that's not the only thing that changes.
If a novice's comprehension curve looks like the lower one in [%f templating-comprehension %],
then an expert's looks like the upper one.
Experts don't just understand more at all levels of abstraction;
their *preferred* level has also shifted
so they find \\(\sqrt{x^2 + y^2}\\) easier to read
than the medieval expression
"the side of the square whose area is the sum of the areas of the two squares
whose sides are given by the first part and the second part".

[% figure
   slug="templating-comprehension"
   img="templating_comprehension.svg"
   alt="Comprehension curves"
   caption="Novice and expert comprehension curves."
%]

This curve means that for any given task,
the code that is quickest for a novice to comprehend
will almost certainly be different from the code that
an expert can understand most quickly.
In an ideal world our tools would automatically re-represent programs at different levels
just as we could change the colors used for syntax highlighting.
But today's tools don't do that,
and any IDE smart enough to translate between comprehension levels automatically
would also be smart enough to write the code without our help.

[% figure
   slug="templating-concept-map"
   img="templating_concept_map.svg"
   alt="Concept map for HTML templating"
   caption="HTML templating concept map."
%]

## Exercises {: #templating-exercises}

### Tracing execution {: .exercise}

Add a directive `<span z-trace="variable"/>`
that prints the current value of a variable for debugging.

### Unit tests {: .exercise}

Write unit tests for template expansion using [pytest][pytest].

### Sub-keys {: .exercise}

Modify the template expander so that a variable name like `person.name`
looks up the `"name"` value in a dictionary called `"person"`
in the current environment.

### Literal text {: .exercise}

Add a directive `<div z-literal="true">…</div>` that copies the enclosed text as-is
without interpreting or expanding any contained directives.
(A directive like this would be needed when writing documentation for the template expander.)

### Including other files {: .exercise}

1.  Add a directive `<div z-include="filename.html"/>` that includes another file
    in the file being processed.

2.  Should included files be processed and the result copied into the including file,
    or should the text be copied in and then processed?
    What difference does it make to the way variables are evaluated?

### HTML snippets {: .exercise}

Add a directive `<div z-snippet="variable">…</div>` that saves some text in a variable
so that it can be displayed later.
For example:

```html
<html>
  <body>
    <div z-snippet="prefix"><strong>Important:</strong></div>
    <p>Expect three items</p>
    <ul>
      <li z-loop="item:names">
        <span z-var="prefix"><span z-var="item"/>
      </li>
    </ul>
  </body>
</html>
```

would printed the word "Important:" in bold before each item in the list.
{: .continue}

### YAML headers {: .exercise}

Modify the template expander to handle variables defined in a YAML header in the page being processed.
For example, if the page is:

```html
---
name: "Dorothy Johnson Vaughan"
---
<html>
  <body>
    <p><span z-var="name"/></p>
  </body>
</html>
```

will create a paragraph containing the given name.
{: .continue}

### Expanding all files {: .exercise}

Write a program `expand_all.py` that takes two directory names as command-line arguments
and builds a website in the second directory by expanding all of the HTML files found in the first
or in sub-directories of the first.

### Counting loops {: .exercise}

Add a directive `<div z-index="indexName" z-limit="limitName">…</div>`
that loops from zero to the value in the variable `limitName`,
putting the current iteration index in `indexName`.

### Boolean expression {: .exercise}

Design and implement a way to express the Boolean operators `and` and `or`.
