# PyTMX v2.15.2
_______________________________________________________________________________

## Map loader for TMX Files

bitcraft (leif dot theden at gmail.com)   
v2.15.2  - for python 2.6 and 2.7   

If you have any problems or suggestions, please contact me via email.

*Released under the LGPL v3*



## News
_______________________________________________________________________________

##### 02/24/14 - New Python 3 Support: see tmxloader.py docstring
##### 02/06/14 - Python 3 support coming soon

   
   
   
## Introduction
_______________________________________________________________________________

PyTMX is a map loader for python/pygame designed for games.  It provides smart
tile loading with a fast and efficient storage base.  Not only will does it
correctly handle most Tiled object types, it also will load meta data for
them, so you can modify your maps and objects in Tiled, instead of modifying
your source code.

Because PyTMX was built with games in mind, it differs slightly from Tiled in
a few minor aspects:

- Layers not aligned to the grid are not supported.
- Some object metadata attribute names are not supported (see docstrings)


PyTMX strives to balance performance, flexibility, and performance.  Feel free
to use the classes provided in pytmx.py as superclasses to your own maps, or
simply load the data with PyTMX and copy the data into your own classes with
the simple api.

I've included a test suite and demo in the 'tests' folder.  It should work
across all platforms.  test.py demonstrates loading a variety of maps and
formats, and demo.py shows how you can create scrolling maps in a very simple
fashion, while still retaining all the power of the Tiled Editor.

Finally, there is no save feature.  Once the map is loaded, it will be up to
you to provide a way to save changes to the map.  I've used the pickle module
with good results.


## Design Goals:
_______________________________________________________________________________

* Simple API with many handy functions
* Memory efficient and performant
* Extensible and easy to understand


## Features:
_______________________________________________________________________________

* Loads data, "properties" metadata, and images from Tiled's TMX format
* Supports base64, csv, gzip, zlib and uncompressed XML
* Properties for all native Tiled object types
* Point data for polygon and polyline objects
* Automatic flipping and rotation of tiles
* Image loading with pygame (will work without images as well)


## Why use PyTMX?
_______________________________________________________________________________

### PyTMX is efficient:
* Only the tiles used on a map are loaded into memory
* Map information is stored as integers (8-16 bit), not python objects (32+kb)
* Extensive use of generators and iterators make it easy on memory
* Code is designed for compact size and readability

### PyTMX is flexible:
* Supports all major Tiled features and object types
* Built-in pygame image loading
* PyTMX data classes can be extended
* Does not force you to render data in any particular way
* Includes many checks to give useful debugging information

### PyTMX is supported:
* GitHub hosting allows for community participation
* I have kept PyTMX current with new versions of Tiled since v.7

### PyTMX is usable:
* Liberal LGPL license means you can use PyTMX [almost] any way you want

_______________________________________________________________________________

Please see tmxloader.py's docstring for version information and sample usage.
Check tests/test.py and tests/demo.py for examples on how to use the library.

_______________________________________________________________________________
The 16x16 overworld tiles were created by MrBeast at opengameart.org. CC-BY 3.0
