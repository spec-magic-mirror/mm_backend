# Magic Mirror Middleware and Backend Services
This repository contains the middleware REST server and backend image processing software used
by Magic Mirror. 

Instructions for use:
1. Launch MongoDB
2. Launch the middleware

	`python middleware.py <port>`

Now the middleware REST service is running and connected to the database.

API Methods:

`<url>/get_test`

This method only exsists to test a connection to the REST service.

Input:
	None

Output:
	A string to indicate a succesful connection to the service.


`<url>/detect_moles`

This method takes an image and returns the same image with all detected moles indicated.

Input:
	Photos to perform mole detection on (as dictionary of files)
	All files must be base64 encoded	
	e.g. 
	
	files={"front":<b64 encoded image data>, "back":<b64 encoded image data>}
	
Output:
	Photos with moles overlayed on them (as dictionary of files)
	All files will be base64 encoded
	The labels of each image will match the label of the original image provided
	e.g. 
	
	{"front":<b64 encoded image data>, "back":<b64 encoded image data>}
	
	Errors will be returned in the form of {"error": <error message string>} so
	it is advisable to check this field after getting a response since there
	is no guarantee that this method will return usable data.
