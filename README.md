# CS1430-Final-Project
Team: "Anything's Fine"

Scraping Instructions (all commands are run in the 'scraper' directory):
	- To download Unsplash.com images:
		- Run 'make download_unsplash'
	- To download Amazon.com images:
		- First make sure that a command-line WebP converter is installed on the 
		target system (instructions at https://developers.google.com/speed/webp/download).
		This installation is necessary to convert some of the WebP images into PNG images that
		are recognized by Python's skimage.imread
		- In addition, because Amazon.com employs bot detection measures, 
		- To resize combine the Unsplash and Amazon images into one zipfile, run
		'make resize_and_compile' in the 'scraper' d
