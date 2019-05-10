# CS1430-Final-Project
Team: "Anything's Fine"

Summary: Image Classifier for IoT Devices using bounding boxes + CNNs.

Note: The scraper rig requires the availibility of symlinks, so this will probably only work on Linux or Mac systems 

Scraping Instructions (all commands are run in the 'scraper' directory):
	- To download Unsplash.com images:
		- Specify what/how much to download by editing 'queries_unsplash.txt' with the fields:
				<search string to query unsplash with>
				<total number pages to download>
				<exact name of category directory to save to>
			All on the same line and separated by a singe comma. This represents
			a single query.
		- Run 'make download_unsplash'
	- To download Amazon.com images (will need to be run on different wifi
	as the Amazon bot-detection kicks in. Or... you can just wait a few hours...):
		- Specify what/how much to download by editing 'queries_amazon.txt' with the fields:
				<query to search on amazon with>
				<start page number to download>
				<end page number to download>
				<exact name of category directory to save to>
			All on the same line and separated by a singe comma. This represents
			a single query.
		- Run 'make download_amazon' to download the images
		- Because Amazon.com employs bot detection measures, the script
		can only successfully download images for around 20min at a time. Switch
		wifi before then. Otherwise most of the rest of the product images won't 
		be able to be downloaded and you'll get a lot of empty directories
	- To resize all the images and put them into a zipfile in the model folder:
		- Run 'make zip'

Running the Model: (if you don't already have saved weights or want to train on new data)
- Run the scraper and place the zipped file with image data in the model folder.
- Run "python model.py" from the model folder.

Starting Up the server:

- Run "python server.py" from the interface folder
- Note: If you're running on a VM in  Google Cloud Compute, make sure that the firewall allows http for port 8080. Then in the browser, your url should be something like http://xx.xxx.xxx.xxx:8080/ . If you're using the CS1430 evironment, you might also have to install flask ("pip install --user flask").