# DigitalSteering
### What is DigitalSteering?
At its core, DigitalSteering employs sophisticated algorithms to interpret user inputs and translate them into virtual steering commands. The program mimics the functionality of a physical steering wheel, allowing users to navigate and control in-game vehicles with precision.

### Why DigitalSteering?
One of the primary goals of DigitalSteering is to break down barriers in gaming accessibility. By offering diverse and customizable control methods, it caters to a broader audience, including individuals with different physical abilities and disabilities.

DigitalSteering takes a step further by addressing the specific needs of individuals with limited mobility, particularly those without the use of arms or hands. The project incorporates adaptive technologies to empower gamers facing physical challenges, providing them with a means to enjoy gaming on equal terms.

# Guide For Pycharm
Please note that this assumes you already have Python installed on your system.

ONLY tested 3.10 Python so it might not work in newer and older versions

## Install Required Packages
First, you need to install the necessary Python packages. Open the integrated command prompt in Pycharm:

pip install opencv-python

pip install mediapipe

## Download the Code
Download the provided code and un-zip the file. After un-zipping go into pycharm and click on the three bars on top left. Click open... and select the un-zipped file

## Run the Code
Run steering.py by doing F10 + Shift or on the top right of the screen

## Exit the Application
To exit the application, press the 'q' key while the application window is active.

Make sure your system has a webcam or an external camera connected. The script uses the default camera (index 0). If you have multiple cameras or a different camera index, you may need to modify the code by changing the number from (0) (Line 61)

Feel free to ask if you have any questions or encounter any issues!

## Common Errors
DO NOT be tabbed into the window with the camera output. Please click a different window to use it if you want to see the steering wheel. Else it shouldn't matter.

If the tracker is not tracking your hands consider to close your hands while using. You can also lower the confidence bar on Line 65 and 66 (decimal = % for example 0.3 = %30 if you didn't know)

Same goes for the tracker falsely identifying a hand. You may raise the confidence bar on 65 and 66 (decimal = % for example 0.3 = %30 if you didn't know)

Steering Digitally :D
