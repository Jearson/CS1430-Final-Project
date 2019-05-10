# Does everything  -- beware, Amazon will probably CAPCTHA (bot-detect) us
# and prevent most of the rest of the images from  being downloaded after
# ~20min of scraping, at this point comment out the already scraped queries
# from queries_amazon.txt by inserting a '#' as the first character of the
# query line, and then switch wifi routers or use a(nother) VPN.
# From there you can resume amazon downloads by running 
# 'make download_amazon'
all: download_unsplash download_amazon zip

# Dowloads the images and pages specified in code/unsplash/queries.txt
download_unsplash:
	cd code/unsplash; python3 download_images.py

# Dowloads the images and pages specified in code/unsplash/queries.txt
download_amazon: 
	cd code/amazon; python3 download_images.py

# Resizes the files into 448x416 images and then zips them all up,
# with the zip in the model directory
zip:
	python3 resize_and_gather_imgs.py
	zip -r ../model/imgs.zip imgs
