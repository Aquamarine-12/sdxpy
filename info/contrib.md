## Formatting {: #contrib-formatting}

This material uses [Ark][ark] with some custom extensions in `./lib/mccole/extensions`.
Please run `make` in the root directory to get a list of available commands,
several of which on scripts in the `./lib/mccole/bin/` directory.

### Chapters and Appendices

1.  Each chapter or appendix has a unique slug such as `topic`.
    Its text lives in <code>./src/<em>topic</em>/index.md</code>,
    and there is an entry for it in the `chapters` or `appendices` dictionary
    in Ark's configuration file `./config.py`.
    The order of entries in these two dictionaries
    determines the order of the chapters and appendices.

1.  The `index.md` files do *not* have YAML headers;
    their titles are taken from `./config.py`.

1.  Each section within a page must use a heading like this:

    ```markdown
    ## Some Title {: #topic-sometitle}
    ```

    This creates an `h2`-level heading with the HTML ID `topic-sometitle`.
    Use the page's slug instead of `topic`
    and hyphenate the words in the ID.

1.  To create a cross-reference to a chapter or appendix write:

    ```markdown
    [%x topic %]
    ```

    where `topic` is the slug of the chapter being referred to.
    This shortcode is converted to `Chapter N` or `Appendix N`
    or the equivalent in other languages.
    Please only refer to chapters or appendices, not to sections.

### Slides

1.  Each chapter directory also has a `slides.html` file
    containing slides formatted with [remark][remark].
    Each `slides.html` file must have a YAML header
    containing `template: slides` to specify the correct template.
    While the `index.md` file becomes `./docs/topic/index.html`,
    the `slides.html` file becomes `./docs/topic/slides/index.html`.

### External Links

1.  The table of external links lives in `./info/links.yml`.
    Please add entries as needed,
    or add translations of URLs to existing entries using
    a two-letter language code as a key.

1.  To refer to an external link write:

    ```markdown
    [body text][link_key]
    ```

Please do *not* add links directly with `[text](http://some.url)`:
keeping the links in `./info/links.yml` ensures consistency
and makes it easier to create a table of external links.

### Code Inclusions

1.  To include an entire file as a code sample write:

    ```markdown
    [% inc file="some_name.py" %]
    ```

    The file must be in or below the directory containing the Markdown file.

1.  To include only part of a file write:

    ```markdown
    [% inc file="some_name.py" keep="some_key" %]
    ```

    and put matching tags in the file like this:

    ```markdown
    # [some_key]
    …lines of code…
    # [/some_key]
    ```

1.  To *omit* part of a file, use:

    ```markdown
    [% inc file="some_name.py" omit="some_key" %]
    ```

    If both the `keep` and `omit` keys are present, the former takes precedence,
    i.e., the `keep` section is included and the `omit` section within it omitted.

1.  To include several files (such as a program and its output) write:

    ```markdown
    [% inc pat="some_stem.*" fill="py out" %]
    ```

    This includes `some_stem.py` and `some_stem.out` in that order.

### Figures

1.  Put the image file in the same directory as the chapter or appendix
    and use this to include it:

    ```markdown
    [% figure
       slug="topic-some-key"
       img="some_file.svg"
       caption="Short sentence-case caption."
       alt="Long text describing the figure for the benefit of visually impaired readers."
    %]
    ```

    Please use underscores in filenames rather than hyphens:
    Python source files' names have to be underscored so that they can be imported,
    so all other filenames are also underscored for consistency.
    (Internal keys are hyphenated to avoid problems with LaTeX during PDF generation.)

1.  To refer to a figure write:

    ```markdown
    [%f topic-some-key %]
    ```

    This is converted to `Figure N.K`.

1.  Use [diagrams.net][diagrams] to create SVG diagrams
    using the "sketch" style and a 12-point Verdana font for all text.
    (`make fonts` will report diagrams that use other fonts.)

1.  Please avoid screenshots or other pixellated images:
    making them display correctly in print is difficult.

### Tables

The Markdown processor used by [Ark][ark] doesn't support attributes on tables,
so we must do something a bit clumsy.

1.  To create a table write:

    ```markdown
    <div class="table" id="topic-someword" caption="Short sentence-case caption." markdown="1">
    | Left | Middle | Right |
    | ---- | ------ | ----- |
    | blue | orange | green |
    | mars | saturn | venus |
    </div>
    ```

1.  To refer to a table write:

    ```markdown
    [%t topic-some-key %]
    ```

    This is converted to `Table N.K`.

### Bibliography

1.  The BibTeX bibliography lives in `./info/bibliography.bib`.
    Please add entries as needed;
    you may find <https://doi2bib.org> useful for creating entries.
    Please format keys as `Author1234`,
    where `Author` is the first author's family name
    and `1234` is the year of publication.
    (Use `Author1234a`, `Author1234b`, etc. to resolve conflicts.)

1.  To cite bibliography entries write:

    ```markdown
    [%b key1 key2 key3 %]
    ```

### Glossary

1.  The glossary lives in `./info/glossary.yml` and uses [Glosario][glosario] format.

1.  When translating the glossary,
    please add definitions and acronyms under a two-letter language key
    rather than duplicating entries.
    Please do *not* translate entries' `key` values.

1.  To cite glossary entries write:

    ```markdown
    [%g some_key "text for document" %]
    ```

### Index

1.  To create a simple index entry write:

    ```markdown
    [%i "index text" %]
    ```

    This puts `index text` in both the document and the index.

1.  If the indexing text and the body text are different, use:

    ```markdown
    [%i "index text" "body text" %]
    ```

1.  Finally, either kind of index entry may optionally include a `url` key
    to wrap the body text in a hyperlink:

    ```markdown
    [%i "index text" url=some_link %]
    ```

    `some_link` must be a key in the `./info/links.yml` links file.

### Minor Formatting

1.  To continue a paragraph after a code sample write:

    ```
    text of paragraph
    which can span multiple lines
    {: .continue}
    ```

    This has no effect on the appearance of the HTML,
    but prevents unwanted paragraph indentation in the PDF version.

1.  To create a callout box, use:

    ```
    <div class="callout" markdown="1">

    ### Title of Callout

    text of callout

    </div>
    ```

    Use "Sentence Case" for the callout's title,
    and put blank lines before and after the opening and closing `<div>` markers.
    You *must* include `markdown="1"` in the opening `<div>` tag
    to ensure that Markdown inside the callout is processed.

## Building the HTML

1.  Pages use the template in `./lib/mccole/templates/node.ibis`,
    which includes snippets from the same directory.

1.  Our CSS is in `./lib/mccole/resources/mccole.css`.
    We also use `./lib/mccole/resources/tango.css` for styling code fragments.
    We do *not* rely on any JavaScript in our pages.

1.  To produce HTML, run `make build` in the root directory,
    which updates the files in <code>./docs</code>.
    You can also run `make serve` to preview files locally.

## Building the PDF

We use LaTeX to build the PDF version of this book.
You will need to install these packages with `tlmgr`
or some other LaTeX package manager:

-   `babel-english`
-   `babel-greek`
-   `cbfonts`
-   `enumitem`
-   `greek-fontenc`
-   `keystroke`
-   `listings`
-   `textgreek`
-   `tocbibind`

## Other Commands

Use <code>make <em>target</em></code> to run a command.

| command | action |
| ------------- | ------ |
| style | check source code style |
| --- | --- |
| commands | show available commands |
| build | rebuild site without running server |
| serve | build site and run server |
| pdf | create PDF version of material |
| --- | --- |
| lint | check project structure |
| headings | show problematic headings (many false positives) |
| inclusions | compare inclusions in prose and slides |
| examples | re-run examples |
| check-examples | check which examples would re-run |
| fonts | check fonts in diagrams |
| spelling | check spelling against known words |
| index | show all index entries |
| --- | --- |
| html | create single-page HTML |
| latex | create LaTeX document |
| pdf-once | create PDF document with a single compilation |
| syllabus | remake syllabus diagrams |
| diagrams | convert diagrams from SVG to PDF |
| --- | --- |
| github | make root pages for GitHub |
| check | check source code |
| fix | fix source code |
| profile | profile compilation |
| clean | clean up stray files |
| --- | --- |
| status | status of chapters |
| valid | run html5validator on generated files |
| vars | show variables |
