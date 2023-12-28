# Digital Steering
Please note that this assumes you already have Python installed on your system.

ONLY tested 3.10 Python so it might not work in newer and older versions

## Install Required Packages
First, you need to install the necessary Python packages. Open your terminal or command prompt and run the following commands:

pip install opencv-python

pip install mediapipe

## Download the Code
Copy the provided Python code into a file with a .py extension, for example, hand_tracking.py.

## Run the Code
Navigate to the directory where you saved hand_tracking.py using the terminal or command prompt.

## Exit the Application
To exit the application, press the 'q' key while the application window is active.

Make sure your system has a webcam or an external camera connected. The script uses the default camera (index 0). If you have multiple cameras or a different camera index, you may need to modify the code accordingly.

Feel free to ask if you have any questions or encounter any issues!

## Common Errors
DO NOT be tabbed into the window with the camera output. Please click a different window to use it if you want to see the steering wheel. Else it shouldn't matter.

If the tracker is not tracking your hands consider to close your hands while using. You can also lower the confidence bar on Line 65 and 66 (decimal = % for example 0.3 = %30 if you didn't know)

Same goes for the tracker falsely identifying a hand. You may raise the confidence bar on 65 and 66 (decimal = % for example 0.3 = %30 if you didn't know)

Steering Digitally :D
