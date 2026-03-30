# CST8504 作业 2 ROS2 视觉

---

## CST8504 作业 2 ROS 2 视觉

## 概览

创建 `aisd_vision` 与 `aisd_move` ROS 2 软件包。完成本作业后，你将能够：

- 创建 ROS 2 软件包
- 在软件包中创建与视觉相关的 ROS 2 节点（Python 模块）
- 运行 `rosdep` 安装软件包依赖
- 运行 `colcon build` 构建可运行的软件包
- 使用命令行启动节点并进行测试
- 使用 GitHub 仓库管理源代码

## 设置 Git 仓库

我们将使用 GitHub Classroom 为本次作业创建 Git 仓库。你的开发工作可以在借用笔记本或虚拟机上完成，因为你会把工作推送到 GitHub 仓库，之后可以在其他工作地点克隆该仓库。

访问以下链接即可使用起始代码（`aisd_msgs` 软件包）创建 GitHub 仓库：https://classroom.github.com/a/DUgO71X9

**我的 GitHub 仓库**: https://github.com/gitalg/aisd-vision-zhizhunbao

要在 Linux 命令行访问你的 GitHub 仓库，需要配置 SSH 密钥。请在任意一台 Ubuntu 服务器（借用笔记本或 VirtualBox 虚拟机）上运行以下命令生成公钥/私钥对。系统会提示你输入密码短语，为了更好的安全性，建议设置。如果使用密码短语，可选地配置 `ssh-agent` 来管理它（否则每次访问 GitHub 使用密钥时都需要输入）。

`ssh-keygen -t ed25519 -C "wang1059@algonquinlive.com"`

关于 SSH 密钥和 `ssh-agent` 的更多信息可参考：https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent

接着按照此处说明将公钥添加到 GitHub 账户：https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account

你已经在 VirtualBox 虚拟机上通过实验 5 建立了一个 ROS 2 工作空间，可以继续使用，或创建新的。如果在借用笔记本上工作，需要创建工作空间：

`mkdir -p ros2_ws/src`

要把 GitHub 仓库克隆到 ROS 2 工作空间，前往仓库页面，使用 Code 按钮复制 SSH 仓库 URL。SSH 地址形式类似 `git@github.com:gitalg/...`。运行以下命令（替换成实际 URL）：

```
cd ros2_ws/src
git clone git@github.com:gitalg/aisd-vision-zhizhunbao.git
cd aisd-vision-zhizhunbao
```

在 `aisd-vision-zhizhunbao` 仓库目录（执行上面命令后所在位置）中，根据页面：https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Creating-Your-First-ROS2-Package.html 的 Python 指引（不是 C++）创建 `aisd_vision` 和 `aisd_motion` 软件包。

两个新软件包初始只是空骨架，但此时我们要提交并推送到 GitHub 仓库。使用 Git 命令时需要位于 `~/ros2_ws/src/aisd-vision-zhizhunbao` 目录或其子目录，并在该目录下运行以下命令：

```
git add aisd-vision aisd-motion
git commit -m "created empty aisd-vision and aisd-motion packages"
git push
```

执行上述命令后，你应该能在 GitHub 仓库中看到新的软件包目录。这表明你能够将代码推送到仓库，同样也可以使用 `git pull` 拉取代码。

若要在另一台 Ubuntu 服务器（借用笔记本或 VirtualBox 虚拟机，取决于最初使用哪一台）克隆 GitHub 仓库，可把主目录下的 `.ssh` 文件夹复制到另一台机器的主目录，然后重复上述克隆命令。克隆完成后，通过 `git push` 和 `git pull` 保持两台机器的代码同步。

## VirtualBox 摄像头直通

注意，在 Linux 机器上，要访问摄像头、麦克风、扬声器等控制台硬件，必须在控制台登录（VirtualBox 窗口或借用笔记本的实际键盘，而非使用 Putty）。只要用户登录在控制台会话中，该控制台会话及远程 Putty 会话都能访问这些设备。

在虚拟机中工作时，为让 VirtualBox 虚拟机使用宿主笔记本的摄像头，需要安装 VirtualBox 扩展包，详情见：

https://docs.oracle.com/en/virtualization/virtualbox/6.0/admin/webcam-passthrough.html#webcam-using-guest

VMware Workstation/Fusion 虚拟机默认使用宿主摄像头，可在虚拟机设置中进行调整。

## 编写 `aisd_vision` 软件包

我们将先处理 `aisd_vision` 软件包，从编辑 `aisd_vision/package.xml` 开始，加入软件包依赖。所需依赖如下：

- `rclpy`：ROS 2 Python 客户端库
- `image_transport`：支持图像的发布与订阅
- `cv_bridge`：在 OpenCV 图像与 ROS 2 图像之间转换
- `std_msgs`：提供 `String` 消息类型
- `sensor_msgs`：提供 `Image` 消息类型
- `python3-mediapipe-pip`：用于 MediaPipe

`rosdep` 命令会参考 `package.xml`，后续会用它把软件包依赖添加到工作空间覆盖层。现在请编辑 `aisd_vision/package.xml` 文件，加入上述依赖。同时可以设置 `Description`、`Maintainer` 与 `License`（无需许可证）。

```
<depend>rclpy</depend>
<depend>image_transport</depend>
<depend>cv_bridge</depend>
<depend>sensor_msgs</depend>
<depend>std_msgs</depend>
<depend>aisd_msgs</depend>
<depend>python3-mediapipe-pip</depend>
```

接下来设置 `aisd_vision` 软件包的入口点。在 `aisd_vision/setup.py` 文件中找到 `entry_points` 变量，将其改为：

```
entry_points={
    'console_scripts': [
        'image_publisher = aisd_vision.image_publisher:main',
        'hands = aisd_vision.hands:main',
    ],
},
```

这意味着以后要从命令行启动 `aisd_vision` 节点，会使用以下命令：

```
ros2 run aisd_vision image_publisher
ros2 run aisd_vision hands
```

创建 `aisd_vision/aisd_vision/image_publisher.py` 文件，并把发布者代码模板复制进去，模板可从此处获取：https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html （写发布者节点）。

将文件顶部的导入语句替换为：

```
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
```

随后按如下步骤将代码改造成 `image_publisher`：

- 将类名 `MinimalPublisher` 改为 `ImagePublisher`（所有位置）
- 将函数名 `minimal_publisher` 改为 `image_publisher`（所有位置）
- 将消息类型 `String` 改为 `Image`
- 将主题 `topic` 改为 `video_frames`
- `timer_period` 可设为 0.1 或 0.2 秒
- 删除 `self.i`，因为不再计数信息，但需要添加：
  - `self.cap = cv2.VideoCapture(0)`
  - `self.br = CvBridge()`

在 `timer_callback` 函数中，可以用以下代码发布图像：

```
ret, frame = self.cap.read()
if ret == True:
    self.publisher_.publish(self.br.cv2_to_imgmsg(frame))
```

完成后提交工作到 Git 仓库。

创建 `aisd_vision/aisd_vision/hands.py` 文件，以订阅者模板为起点，可从此处复制：https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html （写订阅者节点）。

将代码调整为 `Hands` 节点，而非 `MinimalSubscriber`，并相应修改主题等内容，使其订阅 `ImagePublisher` 发布的消息。

`hands.py` 需要以下导入：

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

在构造函数中，需要初始化图像转换器，并创建一个发布 `Hand` 消息到 `cmd_hand` 主题的发布者：

```
# ROS 与 OpenCV 图像之间的转换器
self.br = CvBridge()
self.hand_publisher = self.create_publisher(Hand, 'cmd_hand', 10)
```

每当收到一条 `Image` 消息时，`listener_callback` 函数会被调用。请在回调中加入手部分析代码，并添加注释说明每行代码的作用：

```
def listener_callback(self, msg):
    image = self.br.imgmsg_to_cv2(msg)

    PINKY_FINGER_TIP = 20
    INDEX_FINGER_TIP = 8

    # 分析图像中的双手
    with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as myhands:

        # 为了提升性能，可将图像标记为不可写以实现引用传递
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = myhands.process(image)

        if results.multi_hand_landmarks:
            # 以食指与小指的位置发布手部位置
            msg = Hand()
            msg.xpinky = results.multi_hand_landmarks[0].landmark[PINKY_FINGER_TIP].x
            msg.xindex = results.multi_hand_landmarks[0].landmark[INDEX_FINGER_TIP].x

            if self.hand_publisher.get_subscription_count() > 0:
                self.hand_publisher.publish(msg)
            else:
                self.get_logger().info('waiting for subcriber')
```

完成后提交工作到 Git 仓库。

## 编写 `aisd_motion` 软件包

现在，你将独立完成 `aisd_motion` 软件包。该包包含一个 `Move` 节点，订阅 `cmd_hand` 主题的 `Hand` 消息，并在收到消息时向 `cmd_vel` 主题发布相应的 `Twist` 消息。

先编辑 `aisd_motion/package.xml`：

- 添加对 `aisd_msgs` 的依赖
- 设置 `Description`、`Maintainer` 与 `License`（无需许可证）

然后编辑 `aisd_motion/setup.py` 文件：

```
entry_points={
    'console_scripts': [
        'move = aisd_motion.move:main',
    ],
},
```

接着创建 `aisd_motion/aisd_motion/move.py` 模块。和 `aisd_vision/aisd_vision/hands.py` 类似，该模块会订阅一个主题并发布到另一个主题，因此可再次从最小订阅者模板开始。

所需导入如下：

```
import rclpy
from rclpy.node import Node
from aisd_msgs.msg import Hand
from geometry_msgs.msg import Twist
```

回调函数代码如下，请添加注释说明你对每行代码的理解：

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

完成后提交到 Git 仓库。

## 构建工作空间

现在可以构建工作空间。首先安装 `pip`：

`sudo apt install python3-pip`

切换到 `ros2_ws` 目录，使用 `rosdep` 安装依赖：

`rosdep install -i --from-path src --rosdistro humble -y`

期待看到如下提示，表示依赖安装成功：

`#All required rosdeps installed successfully`

## Numpy 版本

你可能会看到关于 `numpy` 版本的错误提示，例如：

```
ERROR: matplotlib 3.6.2 has requirement numpy>=1.19, but you'll have numpy 1.17.4 which is incompatible.
```

或者，即使运行 `rosdep` 时没有错误，之后运行 `image_publisher` 二进制文件时可能出现：

```
TypeError: 'numpy._DTypeMeta' object is not subscriptable
```

这些错误都源于 `numpy` 版本不匹配。可以通过安装 1.25.2 至 1.26.2 之间的 `numpy` 版本来解决：

`pip install numpy==1.25.2`

安装新版本后，可重新运行命令，若仍有问题，请继续排查并向实验指导老师寻求帮助。

依赖安装完成后，使用 `colcon` 构建工作空间：

`colcon build`

如果看到错误或其他问题，请调查原因，并向实验指导老师请求帮助。工作空间构建无误后别忘了执行 `git commit` 和 `git push`，这样就能在其他 Ubuntu 服务器 ROS 2 机器上克隆最新代码。

## 控制 Turtlesim 模拟器或 Create3

现在你已准备好用 ROS 2 节点控制模拟器或 Create3，流程如下：

- 在 Ubuntu 服务器上打开一个新终端窗口。不建议在运行 `colcon build` 的同一个终端执行以下命令。
- 运行如下命令以加载 overlay：

  `source ~/ros2_ws/install/local_setup.bash`

- 如果在借用笔记本上，确保其通过网线连接到 Create3。如果在虚拟机上，请在后台启动 Turtlesim 模拟器，注意我们将 `/turtle1/cmd_vel` 主题重映射为与 Create3 相同的 `cmd_vel` 名称：

  `ros2 run turtlesim turtlesim_node --ros-args --remap /turtle1/cmd_vel:=cmd_vel &`

- 在后台运行 `ImagePublisher` 节点（若出现前述 `TypeError`，请检查 `numpy` 版本）：

  `ros2 run aisd_vision image_publisher &`

- 在后台运行 `Move` 节点：

  `ros2 run aisd_motion move &`

- 在前台运行 `Hands` 节点（使用 Ctrl+C 停止）：

  `ros2 run aisd_vision hands`

此时 Create3 或 Turtlesim 模拟器应该会对摄像头中的手部动作作出反应。记住，对于 Create3 使用的是借用笔记本的摄像头，而对 Turtlesim 模拟器则使用你自己的电脑摄像头。祝你好运，玩的开心！如有需要请联系实验指导老师。

要关闭上述后台运行的节点，可输入 `jobs` 查看作业号，再使用 `kill %N`（N 为作业号）结束，例如：

`kill %3`

表示结束作业号 3。

## 演示要求

请确保为代码添加注释，展示你对其工作原理的理解。完成 `git push` 后即视为提交。演示时请做好以下准备：

- 登录你的虚拟机
- 在 Windows 笔记本上运行 Turtlesim 模拟器
- 让模拟器响应你的手势指令并旋转跟随食指
- 能够解释任意代码片段的作用、流程与职责等
