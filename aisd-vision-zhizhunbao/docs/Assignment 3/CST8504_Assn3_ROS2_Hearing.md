# CST8504 Assignment 3 ROS 2 Hearing

---

## Overview

Create the `aisd_hearing` and `aisd_speak` ROS 2 packages. When you have completed this assignment, you will know how to:

- Create more ROS 2 packages
- Create hearing-related and speaking ROS 2 Nodes (python modules) in packages
- Run rosdep to install additional package dependencies
- Run colcon build to build/rebuild packages ready to run
- Spin up hearing and speaking Nodes with command line and test them out
- Use a GitHub repository to manage your source code

## Git Repository and New Packages

You already have a ROS 2 workspace on your VirtualBox VM from Lab 2 and Assignment 2, and you can use that workspace, or create a new one.

In your `assignment-2-ros-2-and-vision-<yourname>` repository directory from Assignment 2, create the `aisd_hearing` and `aisd_speaking` packages, by following the python-specific (not cpp) instructions on this page: https://docs.ros.org/en/galactic/Tutorials/Beginner-Client-Libraries/Creating-Your-First-ROS2-Package.html

The two new packages will be just empty skeletons at first, but we will commit them at this point and push them to the GitHub repository. You need to be in the `~/ros2_ws/src/assignment-2-ros-2-and-vision-<yourname>` directory or below when using git commands for this repository in general, and you need to be in `~/ros2_ws/src/assignment-2-ros-2-and-vision-<yourname>` when you run these commands:

```bash
git add aisd-hearing aisd-speaking
git commit -m "created empty aisd-hearing and aisd-speaking packages"
git push
```

After this last command completes, you should see the new package directories in your repository on GitHub.

## Coding the aisd_hearing Package

We will begin with the `aisd_hearing` package, and start by using `aisd_hearing/package.xml` to address the packages that the `aisd_hearing` package depends on. Edit the `aisd_hearing/package.xml` file, to add the dependencies. While the file is open, you can also set the Description, Maintainer, and License elements (no license):

```xml
<depend>rclpy</depend>
<depend>std_msgs</depend>
<depend>python3-pyaudio</depend>
<depend>portaudio19-dev</depend>
<depend>python3-pip</depend>
```

There are additional dependencies that rosdep doesn't handle, so we will install those on the command line. The deepspeech command is for your VirtualBox VM, not the loaner laptop – see the note below.

```bash
sudo apt install python-is-python3
sudo apt install python3-pip
sudo apt install alsa-utils
pip install git+https://github.com/openai/whisper.git
sudo apt install ffmpeg
pip install pydub
pip install gtts
```

Now we will set up the entry points for the `aisd_hearing` package. This is handled in the `aisd_hearing/setup.py` file. Edit this file, find the `entry_points` variable, and change it to:

```python
entry_points={
    'console_scripts': [
        'recording_publisher = aisd_hearing.recording_publisher:main',
        'words_publisher = aisd_hearing.words_publisher:main',
        'speak_client = aisd_hearing.speak_client:main',
    ],
},
```

This specifies that when the time comes to spin up the `aisd_hearing` nodes from the command line, we will use the commands:

```bash
ros2 run aisd_hearing recording_publisher
ros2 run aisd_hearing words_publisher
ros2 run aisd_hearing speak_client
```

Create the `aisd_hearing/aisd_hearing/recording_publisher.py` file using the `recording_publisher_template.py` file which is attached to this assignment. In that file you will find comments that indicate places where code is missing, and those comments give instructions on how to fill in the missing code.

After finishing with `recording_publisher.py`, commit your work to the git repository.

Create the `aisd_hearing/aisd_hearing/words_publisher.py` file, using the `words_publisher_template.py` file which is attached to this assignment. As with the `recording_publisher.py` file, use the comments to fill in the missing code. **NOTE:** you will find that `unr_deepspeech_client.py` uses the `xrange` function twice, but for python3 you can simply change these two calls to `range`.

After finishing with `words_publisher.py`, commit your work to the git repository.

The `aisd_hearing/aisd_hearing/speak_client.py` file is provided for you.

**IMPORTANT:** After building the `aisd_hearing` package, you will need to create the directory where the recordings will be stored. To do this, assuming your workspace is in the aisd home directory and named `ros2_ws`, the command to create the recordings directory would be:

```bash
mkdir ~/ros2_ws/install/aisd_hearing/share/aisd_hearing/recordings
```

## Coding the aisd_speaking Package

Now you are ready to code the `aisd_speaking` package. Create the `aisd_speaking/aisd_speaking/speak.py` file by adapting the code for the MinimalService node, under Step 2 "Write the service node" here (do not use `Speak` as the class name, because that is a message name): https://docs.ros.org/en/galactic/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Service-And-Client.html

Here are the imports for `speak.py`:

```python
import io
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from aisd_msgs.srv import Speak
import rclpy
from rclpy.node import Node
```

Here is the code for the callback. Add comments to this code in order to show that you understand what each line is doing:

```python
def speak_callback(self, request, response):
    with io.BytesIO() as f:
        gTTS(text=request.words, lang='en').write_to_fp(f)
        f.seek(0)
        song = AudioSegment.from_file(f, format="mp3")
        play(song)
    response.response = "OK"
    return response
```

Edit the `aisd_speaking/package.xml` file:

Add the dependencies, and set the Description, Maintainer, and License elements (no license):

```xml
<depend>rclpy</depend>
<depend>std_msgs</depend>
<depend>ffmpeg</depend>
```

Another dependency is the GNU text to speech package, which we will install from the command line:

```bash
pip install gtts
```

Then edit the `aisd_speaking/setup.py` file:

```python
entry_points={
    'console_scripts': [
        'speak = aisd_speaking.speak:main',
    ],
},
```

Commit your work to the git repository.

## Build the workspace

You are now ready to build the workspace.

Log in to a new Putty window, change directories to the `ros2_ws` directory, and use rosdep to install any dependencies:

```bash
rosdep install -i --from-path src --rosdistro humble -y
```

You are expecting to see the following message when this command completes:

```
#All required rosdeps installed successfully
```

After dependencies are installed, build the workspace with colcon:

```bash
colcon build
```

If you see errors or problems, investigate the cause, and ask your lab instructor for help if necessary. When your workspace is building without issues, don't forget to do a git commit, and also a git push so that you can clone the GitHub repository on your other ubuntu-server ROS 2 machine(s).

## Spin up nodes

You are now ready to try your new ROS 2 nodes.

Log into a new window on your ubuntu-server machine. It is not recommended to do the following commands in the same terminal where you ran `colcon build`.

Source the overlay by running the following command:

```bash
source ~/ros2_ws/install/local_setup.bash
```

Spin up the RecordingPublisher node in the background:

```bash
ros2 run aisd_hearing recording_publisher &
```

Spin up the Speak node in the background:

```bash
ros2 run aisd_speaking speak &
```

Spin up the SpeakClient node in the background:

```bash
ros2 run aisd_hearing speak_client &
```

Spin up the WordsPublisher node in the background:

```bash
ros2 run aisd_hearing words_publisher &
```

To run all of these at once:

```bash
ros2 run aisd_speaking speak & \
ros2 run aisd_hearing recording_publisher & \
ros2 run aisd_hearing words_publisher & \
ros2 run aisd_hearing speak_client &
```

To shut down the nodes we ran in the background above, we can type the `jobs` command to see their job numbers, and use `kill %N` where N is a job number, for example:

```bash
kill %3
```

would kill job number 3.

## Demonstration

Be sure to comment your code to show that you understand what it is doing. After you have done a git push, your code can be considered submitted. For the demonstration, be prepared to show that you can:

- Log in to your virtual machine
- Speak to the laptop and have it tell you what it heard you say
- Be prepared to explain how any portion of your code works, what it is doing, what is its responsibilities, and so on.
