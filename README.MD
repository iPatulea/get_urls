Write a Python script that downloads files from the internet and saves them in a download directory.

The list of URLs to download will be provided in a simple text file. URLs are separated by a newline. Assume that the files are small, so downloading them does not require streaming.

Input.txt:
https://cdn-9.motorsport.com/images/mgl/24vA3r46/s500/max-verstappen-red-bull-racing-1.webp
https://cdn-8.motorsport.com/images/mgl/24vA4nA6/s500/daniel-ricciardo-mclaren-1.webp
https://cdn-8.motorsport.com/images/mgl/0L1nLWJ2/s500/lando-norris-mclaren-1.webp

The download directory should be provided as a command line parameter.

Consider the following and implement reasonable solutions for the following problems:

How to handle HTTP 404 errors?
How to make the download process faster?
How to display the progress of downloads?
How to handle cancellation? (i.e., the user presses CTRL+C)
Optional: How to handle retry in case of intermittent network errors?
