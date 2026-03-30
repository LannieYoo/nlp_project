# CST8504 作业 3 ROS 2 听觉

---

## 概述

创建 `aisd_hearing` 和 `aisd_speak` ROS 2 包。完成本作业后，您将了解如何：

- 创建更多 ROS 2 包
- 在包中创建与听觉和语音相关的 ROS 2 节点（Python 模块）
- 运行 rosdep 安装额外的包依赖项
- 运行 colcon build 构建/重新构建准备运行的包
- 使用命令行启动听觉和语音节点并测试它们
- 使用 GitHub 仓库管理源代码

## Git 仓库和新包

您已经在 VirtualBox VM 上从实验 2 和作业 2 中有了一个 ROS 2 工作空间，您可以使用该工作空间，或创建一个新的。

在您来自作业 2 的 `assignment-2-ros-2-and-vision-<yourname>` 仓库目录中，按照此页面上的 Python 特定（非 cpp）说明创建 `aisd_hearing` 和 `aisd_speaking` 包：https://docs.ros.org/en/galactic/Tutorials/Beginner-Client-Libraries/Creating-Your-First-ROS2-Package.html

这两个新包最初只是空骨架，但我们将在此处提交它们并推送到 GitHub 仓库。在使用此仓库的 git 命令时，您需要位于 `~/ros2_ws/src/assignment-2-ros-2-and-vision-<yourname>` 目录或以下，并且在运行这些命令时，您需要位于 `~/ros2_ws/src/assignment-2-ros-2-and-vision-<yourname>`：

```bash
git add aisd-hearing aisd-speaking
git commit -m "created empty aisd-hearing and aisd-speaking packages"
git push
```

在最后一个命令完成后，您应该能在 GitHub 上的仓库中看到新的包目录。

## 编写 aisd_hearing 包

我们将从 `aisd_hearing` 包开始，首先使用 `aisd_hearing/package.xml` 来处理 `aisd_hearing` 包所依赖的包。编辑 `aisd_hearing/package.xml` 文件，添加依赖项。打开文件时，您还可以设置 Description、Maintainer 和 License 元素（无许可证）：

```xml
<depend>rclpy</depend>
<depend>std_msgs</depend>
<depend>python3-pyaudio</depend>
<depend>portaudio19-dev</depend>
<depend>python3-pip</depend>
```

还有一些 rosdep 无法处理的额外依赖项，因此我们将在命令行上安装它们。deepspeech 命令适用于您的 VirtualBox VM，而不是借用的笔记本电脑——请参阅下面的注释。

```bash
sudo apt install python-is-python3
sudo apt install python3-pip
sudo apt install alsa-utils
pip install git+https://github.com/openai/whisper.git
sudo apt install ffmpeg
pip install pydub
pip install gtts
```

现在我们将为 `aisd_hearing` 包设置入口点。这在 `aisd_hearing/setup.py` 文件中处理。编辑此文件，找到 `entry_points` 变量，并将其更改为：

```python
entry_points={
    'console_scripts': [
        'recording_publisher = aisd_hearing.recording_publisher:main',
        'words_publisher = aisd_hearing.words_publisher:main',
        'speak_client = aisd_hearing.speak_client:main',
    ],
},
```

这指定了当需要从命令行启动 `aisd_hearing` 节点时，我们将使用以下命令：

```bash
ros2 run aisd_hearing recording_publisher
ros2 run aisd_hearing words_publisher
ros2 run aisd_hearing speak_client
```

使用附加到此作业的 `recording_publisher_template.py` 文件创建 `aisd_hearing/aisd_hearing/recording_publisher.py` 文件。在该文件中，您会找到指示缺少代码位置的注释，这些注释提供了如何填写缺少代码的说明。

完成 `recording_publisher.py` 后，将您的工作提交到 git 仓库。

使用附加到此作业的 `words_publisher_template.py` 文件创建 `aisd_hearing/aisd_hearing/words_publisher.py` 文件。与 `recording_publisher.py` 文件一样，使用注释填写缺少的代码。**注意：** 您会发现 `unr_deepspeech_client.py` 两次使用 `xrange` 函数，但对于 python3，您只需将这两个调用更改为 `range`。

完成 `words_publisher.py` 后，将您的工作提交到 git 仓库。

`aisd_hearing/aisd_hearing/speak_client.py` 文件已为您提供。

**重要提示：** 构建 `aisd_hearing` 包后，您需要创建存储录音的目录。为此，假设您的工作空间位于 aisd 主目录中并命名为 `ros2_ws`，创建录音目录的命令将是：

```bash
mkdir ~/ros2_ws/install/aisd_hearing/share/aisd_hearing/recordings
```

## 编写 aisd_speaking 包

现在您已准备好编写 `aisd_speaking` 包。通过适配此处步骤 2 "编写服务节点" 下的 MinimalService 节点代码来创建 `aisd_speaking/aisd_speaking/speak.py` 文件（不要使用 `Speak` 作为类名，因为那是消息名称）：https://docs.ros.org/en/galactic/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Service-And-Client.html

以下是 `speak.py` 的导入：

```python
import io
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from aisd_msgs.srv import Speak
import rclpy
from rclpy.node import Node
```

以下是回调函数的代码。为此代码添加注释，以表明您理解每一行的作用：

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

编辑 `aisd_speaking/package.xml` 文件：

添加依赖项，并设置 Description、Maintainer 和 License 元素（无许可证）：

```xml
<depend>rclpy</depend>
<depend>std_msgs</depend>
<depend>ffmpeg</depend>
```

另一个依赖项是 GNU 文本转语音包，我们将从命令行安装它：

```bash
pip install gtts
```

然后编辑 `aisd_speaking/setup.py` 文件：

```python
entry_points={
    'console_scripts': [
        'speak = aisd_speaking.speak:main',
    ],
},
```

将您的工作提交到 git 仓库。

## 构建工作空间

现在您已准备好构建工作空间。

登录到新的 Putty 窗口，切换到 `ros2_ws` 目录，并使用 rosdep 安装任何依赖项：

```bash
rosdep install -i --from-path src --rosdistro humble -y
```

当此命令完成时，您应该看到以下消息：

```
#All required rosdeps installed successfully
```

安装依赖项后，使用 colcon 构建工作空间：

```bash
colcon build
```

如果您看到错误或问题，请调查原因，必要时向您的实验指导老师寻求帮助。当您的工作空间构建没有问题后，不要忘记进行 git commit，还要进行 git push，以便您可以在其他 ubuntu-server ROS 2 机器上克隆 GitHub 仓库。

## 启动节点

现在您已准备好尝试新的 ROS 2 节点。

登录到 ubuntu-server 机器上的新窗口。不建议在运行 `colcon build` 的同一终端中执行以下命令。

通过运行以下命令来 source overlay：

```bash
source ~/ros2_ws/install/local_setup.bash
```

在后台启动 RecordingPublisher 节点：

```bash
ros2 run aisd_hearing recording_publisher &
```

在后台启动 Speak 节点：

```bash
ros2 run aisd_speaking speak &
```

在后台启动 SpeakClient 节点：

```bash
ros2 run aisd_hearing speak_client &
```

在后台启动 WordsPublisher 节点：

```bash
ros2 run aisd_hearing words_publisher &
```

要同时运行所有这些：

```bash
ros2 run aisd_speaking speak & \
ros2 run aisd_hearing recording_publisher & \
ros2 run aisd_hearing words_publisher & \
ros2 run aisd_hearing speak_client &
```

要关闭我们在上面后台运行的节点，我们可以输入 `jobs` 命令查看它们的作业编号，并使用 `kill %N`，其中 N 是作业编号，例如：

```bash
kill %3
```

将杀死作业编号 3。

## 演示

请务必注释您的代码，以表明您理解它的作用。在您完成 git push 后，您的代码可以被视为已提交。对于演示，请准备好展示您可以：

- 登录到您的虚拟机
- 对着笔记本电脑说话，让它告诉您它听到您说的话
- 准备好解释您的代码的任何部分如何工作、它在做什么、它的职责是什么等等。
