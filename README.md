# CS1430-Final-Project
Team: "Anything's Fine"

Summary: Image Classifier for IoT Devices using bounding boxes + CNNs. 

#Setting up:

Getting Data:
	Scraping Instructions (all commands are run in the 'scraper' directory):
		- To download Unsplash.com images:
			- Edit 'queries_unsplash.txt' with
			- Run 'make download_unsplash'
		- To download Amazon.com images (will need to be run on different wifi
		as the Amazon bot-detection kicks in. Or... you can just wait a few hours...):
			- First, make sure that a command-line WebP converter is installed on the 
			target system (instructions at https://developers.google.com/speed/webp/download).
			This installation is necessary to convert some of the WebP images into PNG images that
			are recognized by Python's skimage.imread
			- Then run 'make download_amazon'
			- In, addition, because Amazon.com employs bot detection measures, the script
			can only successfully download images for around 20min at a time. Switch
			wifi before then.
		- To resize and combine the Unsplash and Amazon images into one zipfile:
			- Run 'make resize_and_compile'

Running the Model: (if you don't already have saved weights or want to train on new data)
- Run the scraper and place the zipped file with image data in the model folder.
- Run "python model.py" from the model folder.

Starting Up the server:

- Run "python server.py" from the interface folder
- Note: If you're running on a VM in  Google Cloud Compute, make sure that the firewall allows http for port 8080. Then in the browser, your url should be something like http://xx.xxx.xxx.xxx:8080/ . If you're using the CS1430 evironment, you might also have to install flask ("pip install --user flask").