## Dannnno's WebBrowser

This is a very long term project I'm going to play around with.  In general I'm interested in how to most effectively
write parsers and I'd like to practice using a well solved problem (html, js, css).  This way I can compare my
implementation to existing implementations and better locate edge cases I wouldn't otherwise notice.

I'm also interested in browser rendering - I'm curious how something parses an HTML file (and associated CSS, JS, etc)
and then displays it appropriately.  I want to play around with that as well.

Eventually I'd like to take a crack at a JavaScript interpreter.

I'd like for all of this to be written in Python.  I'm planning on starting in CPython and getting things working properly 
there.  Eventually I'd like to find the important bits (probably the JavaScript interpreter) and use ctypes or
cython to speed it up.  

In short, this rather ambitiously named project will eventually seek to have some level of functionality consistent with
other webbrowsers (on a much smaller scale in all likelihood)


###Approximate timeline/order of events:
  1. Getting a working implementation of a CSS Parser.  This will probably be a gradual process, lots of coming back and 
covering edge cases and such.
  2. Getting a working implementation of an HTML Parser.  Again, gradual.  Going to take a lot of work... <understatement
of the year>
  3. HTML rendering.  I frankly have no idea how I'm even going to approach this
  4. CSS rendering.  See above
  5. Working implementation of a JavaScript Parser.  See <1>, <2>
  6. JavaScript interpreter.  See <3>
  7. JavaScript rendering (ie rendering things based on JavaScript)
  8. Actual browser implementation.  Don't really know what this will entail, but I imagine a lot of stuff with HTTP 
requests
  9. Use my new browser semi-exclusively.  Fix edge cases as they come up.
  10. ???
  11. Profit!


...

At least where I'm standing, that is an entire list of non-trivial problems.  This isn't ambitious; its insane as
a one man project.  It'll be fun though. Learn a lot.


### Testing

This will have to be a well tested job to even come close to functioning.  I plan on testing somewhat rigorously from the
get-go and then updating for edge cases as often as necessary.

All tests can be run using nose from the commandline

    \Path\To\Directory\WebBrowser\> nosetests
    
    
