# CS1430-Final-Project
Team: "Anything's Fine"

Summary: Image Classifier for IoT Devices using bounding boxes + CNNs. 

Logistics:

Getting Data:
- Run the scraper and place the zipped file with image data in the model folder.

Running Model: (if you don't already have saved weights or want to train on new data)

- Run "python model.py" from the model folder.

Starting up server:

- Run "python server.py" from the interface folder
- Note: If you're running on a VM in  Google Cloud Compute, make sure that the firewall allows http for port 8080. Then in the browser, your url should be something like http://xx.xxx.xxx.xxx:8080/