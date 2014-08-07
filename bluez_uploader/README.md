This is a simple bluetooth transfer application for bluez -> android SL4A.
The android component, bluez_upload.py starts on your smartphone and listens on bluetooth.
The PC application upload.py is run with a file as a parameter to transfer over.

I use this mainly to easily and quickly transfer over Python scripts I am developing.
I haven't tried this on binary files, only Python scripts.
Be sure to update the hardcoded bluetooth MAC address in upload.py to your smartphone's.
