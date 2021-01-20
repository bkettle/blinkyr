# Ruffler

This thing should let you input the URL of a page that includes a SWF file. Then, that url will be sent back to the server, which will search in the HTML of that page to find the SWF file. It will save the SWF file somewhere on the server (or in an s3 bucket) then store the url in a database. Each file will have an ID created for it, like a URL shortener, and the user will then be directed to the corresponding page, where the SWF file will play full screen using ruffler. 

Django? Or just flask? There's not much that has to happen, probably django is overkill but idk.
