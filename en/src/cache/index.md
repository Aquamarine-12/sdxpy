---
title: "A File Cache"
syllabus:
- FIXME
---

-   Data scientists often want to analyze the same files in several projects
    -   Those files might be too sensitive or too large to store in version control
    -   And shouldn't be duplicated anyway
-   Tools like [Git LFS][git_lfs] and [DVC][dvc] are an alternative
    -   Replace the file with a marker containing a unique ID
    -   Store the file in the cloud using that ID
    -   Create a cache of recently-used files
-   Our system has several parts
    -   The permanent archive
    -   An index of all the files it contains
    -   The local cache
    -   The replacements in version control
-   Several ways to implement each of these
    -   Which gives us a chance to explore some ideas in object-oriented programming

## A File Index {: #cache-index}

-   `index_base.py`
-   Define a named tuple `CacheEntry` to record identifier (hash) and timestamp (when file added)
-   Create a base class that specifies all the operations a file index can do
    -   Get and set the directory where the index file is stored
    -   Check if a particular file is known (using its identifier, not its name)
    -   Get a list of all known files (by identifier, not name)
    -   Add an identifier to the index (with a timestamp)
    -   Three abstract methods:
	-   Initialize the index if it doesn't already exist
        -   Load the index
	-   Save the index
    -   Note: create a function `current_time` rather than using `datetime.now` to simplify mocking

-   `index_csv.py`
-   Specifies that the index is stored in `index.csv` in the index directory
-   Loads the index by reading the CSV file and converting rows to `CacheEntry`
-   Saves the index
-   Creates an empty CSV file if necessary

-   `test_index_csv.py`
-   Can we load the index immediately (i.e., is it automatically created)?
-   Can we save and inspect entries?

## A Simple Cache {: #cache-simple}

-   `cache_base.py` defines behavior every cache must have
    -   How are cached files named? (identifier plus `.cache` suffix)
    -   Add a local file to the cache if it isn't already there
        -   Relies on abstract method `_add` that does everything that won't be common to all implementations
    -   Get the path to a local (cached) copy of a file given its identifier
    -   Does the cache have a particular file and what files are known?
        -   Relies on the index
	-   Which is hidden from the user: has-a rather than is-a or exposing components
-   `cache_filesystem.py` copies files to the cache but doesn't do anything else
    -   Primarily for testing
    -   But useful in its own right (use it to share large files between projects on the same machine)
-   `test_cache_filesystem.py`
    -   Is the cache initially empty?
    -   Can we add files?
    -   Can we find files we've added?
-   Note: so far it's up to the user to remember the mapping between `name.txt` and `abcd1234`
    -   We'll fix this soon
