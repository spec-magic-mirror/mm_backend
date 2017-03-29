# Magic Mirror Middleware and Backend Services
This repository contains the middleware REST server and backend image processing software used
by Magic Mirror. 

Instructions for use:
1. Launch MongoDB
2. Launch the middleware
	python middleware.py <port>

Now the middleware REST service is running and connected to the database.

API:
<url>/detect_moles
Input:
	Photos to perform mole detection on (as dictionary of files)
	All files must be base64 encoded	
	e.g. files={"front":<b64 encoded image data>, "back":<b64 encoded image data>}
	
Output:
	Photos with moles overlayed on them (as dictionary of files)
	All files will be base64 encoded
	The labels of each image will match the label of the original image provided
	e.g. {"front":<b64 encoded image data>, "back":<b64 encoded image data>}
