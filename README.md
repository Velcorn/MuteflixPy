A simple Python script with a simple GUI that mutes the browser (Windows) or system (MacOS/Linux) when an ad is playing 
on either Twitch or Netflix. 

It works by periodically taking a screenshots of a specified bounding box for either Twitch or Netflix. 
It then uses OCR to extract text from the screenshot and checks if the text contains a specified string (Twitch) 
or uses a binary classifier to determine if an ad is playing (Netflix) and mutes the browser or system if it is.

## Installation
1. Clone the repository
2. Install the required packages using `pip install -r requirements.txt`
3. Optional: Use record.py to record your own training data for the Netflix classifier
4. Either download the trained model from [here](https://drive.google.com/file/d/15U3fO-jYcXjD6HSOfpH3HF6oYJxxSbZc/view?usp=sharing) or train your own model using the `train.py` script
5. Run the script using `python muteflix.py`
