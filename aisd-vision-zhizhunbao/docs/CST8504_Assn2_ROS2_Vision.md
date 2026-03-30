# CST8504 Assn2 ROS2 Vision

---

## CST8504 Assignment 2 ROS 2 Vision

## Overview

Create the aisd_vision and aisd_move ROS 2 packages. When you have completed this assignment, you will know how to

- Create ROS 2 packages
- Create vision-related ROS 2 Nodes (python modules) in packages
- Run rosdep to install package dependencies
- Run colcon build to build packages ready to run
- Spin up Nodes with command line and test them out
- Use a GitHub repository to manage your source code

## Setup Git Repository

We will use GitHub Classroom to create your git repository for this assignment. Your development work can then be done on either your loaner laptop or your virtual machine, because your work will be pushed to your GitHub repository which can then be cloned to other work locations.

You can get started by visiting the following link to create your GitHub repository with the starter code (aisd_msgs package): https://classroom.github.com/a/DUgO71X9

**My GitHub Repository**: https://github.com/gitalg/aisd-vision-zhizhunbao

To access your GitHub repository from the Linux command line, you will set up an SSH key for GitHub access. To generate a public/private key pair, run the following command on one of your Ubuntu-server machines (loaner laptop, or VirtualBox VM). You will be prompted to enter a passphrase, which is recommended for better security. If you use a passphrase, you can optionally set up ssh-agent to manage the passphrase for you (if not, you'll need to type the passphrase each time you access GitHub and use the key).

`ssh-keygen -t ed25519 -C "wang1059@algonquinlive.com"`

More details about ssh keys and the process as well as ssh-agent can be found here: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent

Now, add your public key to your GitHub account by following these instructions: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account

You already have a ROS 2 workspace on your VirtualBox VM from Lab 5, and you can use that workspace, or create a new one. If you’re working on the loaner laptop, you’ll need to create the workspace:

`mkdir -p ros2_ws/src`

To clone your GitHub repository into the ROS 2 workspace, go to your repository GitHub page and use the Code button to copy the SSH repository URL to your clipboard. The SSH URL will be of the form git@github.com:gitalg/... Run the following commands (use the actual URL):

```
cd ros2_ws/src
git clone git@github.com:gitalg/aisd-vision-zhizhunbao.git
cd aisd-vision-zhizhunbao
```

In the aisd-vision-zhizhunbao repository directory, which will be your current directory after running the above commands, create the aisd_vision and aisd_motion packages, by following the python-specific (not cpp) instructions on this page: https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Creating-Your-First-ROS2-Package.html

The two new packages will be just empty skeletons at first, but we will commit them at this point and push them to the GitHub repository. You need to be in the ~/ros2_ws/src/aisd-vision-zhizhunbao directory or below when using git commands for this repository in general, and you need to be in ~/ros2_ws/src/aisd-vision-zhizhunbao when you run these commands:

```
git add aisd-vision aisd-motion
git commit -m “created empty aisd-vision and aisd-motion packages”
git push
```

After this last command completes, you should see the new package directories in your repository on GitHub. You have shown you are able to push code to the GitHub repository, and you can also pull code from the GitHub repository with git pull.

To clone your GitHub repository into the workspace on your other Ubuntu-server machine (either the loaner laptop or the VirtualBox VM, depending on which one you chose to begin working on), you can copy the .ssh folder in your home directory to the home directory of the other Ubuntu-server machine, and run the cloning commands above. After cloning, you can push and pull code to and from the GitHub repository as necessary to keep your two Ubuntu-server machines in sync.

## Camera Passthrough for VirtualBox

Note that on a Linux machine, to have access to console hardware like camera, microphone, speakers, the Linux user must be logged into the console (the VirtualBox window, or the actual Loaner Laptop keyboard, not using Putty). As long as the user is logged in to the console, they will have access to console devices in that console session as well as remote Putty sessions.

When working with your virtual machine, for your VirtualBox virtual machine to access your host laptop’s camera, you will need to install a VirtualBox extension pack, as described here:

https://docs.oracle.com/en/virtualization/virtualbox/6.0/admin/webcam-passthrough.html#webcam-using-guest

VMware Workstation/Fusion virtual machines use the host’s camera by default, and this setting is one of the virtual machine settings.

## Coding the aisd_vision Package

We will begin with the aisd_vision package, and start by using aisd_vision/package.xml to address the packages that the aisd_vision package depends on. The dependencies are:

- rclpy: the ROS 2 client library for Python
- image_transport: to support publishing and subscribing to images
- cv_bridge: to translate from OpenCV images to ROS 2 images and back
- std_msgs: for String message type
- sensor_msgs: for Image message type
- python3-mediapipe-pip: for MediaPipe

The rosdep command references package.xml, and that command will later be used to actually add the packages to the workspace overlay. For now, edit the aisd_vision/package.xml file, to add the dependencies. While the file is open, you can also set the Description, Maintainer, and License elements (no license):

```
<depend>rclpy</depend>
<depend>image_transport</depend>
<depend>cv_bridge</depend>
<depend>sensor_msgs</depend>
<depend>std_msgs</depend>
<depend>aisd_msgs</depend>
<depend>python3-mediapipe-pip</depend>
```

Now we will set up the entry points for the aisd_vision package. This is handled in the aisd_vision/setup.py file. Edit this file, find the entry_points variable, and change it to

```
entry_points={
    'console_scripts': [
        'image_publisher = aisd_vision.image_publisher:main',
        'hands = aisd_vision.hands:main',
    ],
},
```

This specifies that when the time comes to spin up the aisd_vision nodes from the command line, we will use the commands

```
ros2 run aisd_vision image_publisher
ros2 run aisd_vision hands
```

Create the aisd_vision/aisd_vision/image_publisher.py file and copy the publisher code template into it, copying from here: https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html - write-the-publisher-node

Change the imports at the top of the file to

```
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
```

Convert the code to an image_publisher by making the following changes:

- MinimalPublisher becomes ImagePublisher (everywhere)
- minimal_publisher becomes image_publisher (everywhere)
- String (message type) becomes Image
- topic becomes video_frames
- timer_period can be .1 or .2 seconds or so
- self.i can be removed because we won’t count the messages, but we will need
  - `self.cap = cv2.VideoCapture(0)`
  - `self.br = CvBridge()`

Then, in the timer_callback function, we can publish an image:

```
ret, frame = self.cap.read()
if ret == True:
    self.publisher_.publish(self.br.cv2_to_imgmsg(frame))
```

Commit your work to the git repository.

Create the aisd_vision/aisd_vision/hands.py file, and begin with the template code for a subscriber, copied from here: https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html - write-the-subscriber-node

Adjust the code to make it a Hands node rather than a MinimalSubscriber node, and make the corresponding changes to the topic, etc, so that it subscribes to the messages published by the ImagePublisher.

Here are the imports for hands.py:

```
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
from aisd_msgs.msg import Hand
```

In the constructor, you will also need to initialize a converter for converting images, as well as a publisher of Hand messages to the cmd_hand topic:

```
# A converter between ROS and OpenCV images
self.br = CvBridge()
self.hand_publisher = self.create_publisher(Hand, 'cmd_hand', 10)
```

Every time an Image message is received, the listener_callback function will be called. The code to do the hand analysis goes in the callback function. Be sure to add comments to this code to show that you know what each line is doing:

```
def listener_callback(self, msg):
    image = self.br.imgmsg_to_cv2(msg)

    PINKY_FINGER_TIP = 20
    INDEX_FINGER_TIP = 8

    # Analyse the image for hands
    with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as myhands:

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = myhands.process(image)

        if results.multi_hand_landmarks:
            # publish the hand position in terms of index finger and pinky
            msg = Hand()
            msg.xpinky = results.multi_hand_landmarks[0].landmark[PINKY_FINGER_TIP].x
            msg.xindex = results.multi_hand_landmarks[0].landmark[INDEX_FINGER_TIP].x

            if self.hand_publisher.get_subscription_count() > 0:
                self.hand_publisher.publish(msg)
            else:
                self.get_logger().info('waiting for subcriber')
```

Commit your work to the git repository.

Coding the aisd_motion Package

Now you are ready to code the aisd_motion package basically on your own. There will be one Move node, that subscribes to Hand messages through the cmd_hand topic. Whenever it receives a Hand message the node should publish the appropriate Twist message on the cmd_vel topic.

Begin by editing the aisd_motion/package.xml file:

- Add the dependency: aisd_msgs.
- Set the Description, Maintainer, and License elements (no license).

Then edit the aisd_motion/setup.py file:

```
entry_points={
    'console_scripts': [
        'move = aisd_motion.move:main',
    ],
},
```

Then create the aisd_motion/aisd_motion/move.py module. Like the aisd_vision/aisd_vision/hands.py module, it will subscribe to one topic and publish to another, so as you did before you can start with the template code for a minimal subscriber.

Here are the imports:

```
import rclpy
from rclpy.node import Node
from aisd_msgs.msg import Hand
from geometry_msgs.msg import Twist
```

Here is the code for the callback. Add comments to this code in order to show that you understand what each line is doing:

```
def listener_callback(self, msg):
    angle = 0.0
    linear = 0.0

    if msg.xindex > 0.55:
        self.get_logger().info('right')
        angle = -0.1
    elif msg.xindex < 0.45:
        self.get_logger().info('left')
        angle = 0.1
    else:
        angle = 0.0

    if msg.xindex > msg.xpinky:
        self.get_logger().info('come')
        linear = 0.5
    else:
        self.get_logger().info('stay')
        linear = 0.0

    twist = Twist()
    twist.linear.x = linear
    twist.angular.z = angle

    if self.vel_publisher.get_subscription_count() > 0:
        self.vel_publisher.publish(twist)
    else:
        self.get_logger().info('waiting for subcriber')
```

Commit your work to the git repository.

## Build the Workspace

You are now ready to build the workspace. But first install pip by running the following command:

`sudo apt install python3-pip`

Change directories to the ros2_ws directory, and use rosdep to install any dependencies:

`rosdep install -i --from-path src --rosdistro humble -y`

You are expecting to see the following message when this command completes:

`#All required rosdeps installed successfully`

## Numpy Version

You may see an error about numpy being the wrong version for matplotlib:

```
ERROR: matplotlib 3.6.2 has requirement numpy>=1.19, but you'll have numpy 1.17.4 which is incompatible.
```

Alternatively, even if you don’t see an error when you run the rosdep command, you might see an error when you later run your image_publisher binary, such as:

```
TypeError: 'numpy._DTypeMeta' object is not subscriptable
```

Both of these errors are due to a mismatched numpy version. We can address this error by installing a numpy version between numpy>=1.25.2 and numpy<=1.26.2:

`pip install numpy==1.25.2`

After installing the newer version of numpy, you can re-run the command without errors. If there are still problems, then investigate the problems, and ask your lab instructor for help if necessary.

After dependencies are installed, build the workspace with colcon:

`colcon build`

If you see errors or problems, investigate the cause, and ask your lab instructor for help if necessary. When your workspace is building without issues, don’t forget to do a git commit, and also a git push so that you can clone the GitHub repository on your other ubuntu-server ROS 2 machine(s).

## Control the Turtlesim Simulator or Create3

You are now ready to control the simulator or Create3 with your ROS 2 nodes. The process is as follows:

- log into a new window on your ubuntu-server machine. It is not recommended to do the following commands in the same terminal where you ran colcon build.
- Source the overlay by running the following command:

  `source ~/ros2_ws/install/local_setup.bash`

- If you are on your loaner laptop, ensure it is network-cable connected to your Create3. If you are on your virtual machine, start the turtlesim simulator in the background, and note that we are remapping the /turtle1/cmd_vel topic name to be the same cmd_vel topic name as on the Create3:

  `ros2 run turtlesim turtlesim_node --ros-args --remap /turtle1/cmd_vel:=cmd_vel &`

- Spin up the ImagePublisher node in the background (if this gives the TypeError mentioned in the Numpy Version section above, check your version of numpy):

  `ros2 run aisd_vision image_publisher &`

- Spin up the Move node in the background:

  `ros2 run aisd_motion move &`

- Spin up the Hands node in the forground (cntl-C to stop it):

  `ros2 run aisd_vision hands`

Your Create3 or turtlesim simulator should now be paying attention to your hand when in view of the camera. Remember that is the loaner laptop camera for the Create3, or your laptop camera for the turtlesim simulator. Good luck and have fun! Ask your lab instructor for help if necessary.

To shut down the nodes we ran in the background above, we can type the jobs command to see their job numbers, and use kill %N where N is a job number, for example:

`kill %3`

would kill job number 3.

## Demonstration

Be sure to comment your code to show that you understand what it is doing. After you have done a git push, your code can be considered submitted. For the demonstration, be prepared to show that you can:

- Log in to your virtual machine
- Run the turtlesim simulator, displayed on your Windows laptop
- Have the simulator react to your hand commands and rotate to follow your index finger
- Be prepared to explain how any portion of your code works, what it is doing, what is its responsibilities, and so on.
