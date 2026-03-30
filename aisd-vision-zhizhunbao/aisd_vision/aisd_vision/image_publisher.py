# ============================================================================
# 1. Import required modules
# ============================================================================
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2


# ============================================================================
# 2. ImagePublisher class: Reads images from camera and publishes to video_frames topic
# ============================================================================
class ImagePublisher(Node):

    def __init__(self):
        super().__init__('image_publisher')
        self.get_logger().info('ImagePublisher node initialized')
        
        # ============================================================================
        # [2.1] Create publisher for Image messages on video_frames topic
        # ============================================================================
        self.publisher_ = self.create_publisher(Image, 'video_frames', 10)
        self.get_logger().info('Publisher created on topic: video_frames')
        
        # ============================================================================
        # [2.2] Create timer to periodically capture and publish frames (10Hz)
        # ============================================================================
        timer_period = 0.1
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.get_logger().info(f'Timer created with period: {timer_period}s (10Hz)')
        
        # ============================================================================
        # [2.3] Initialize camera capture (default camera index 0)
        # ============================================================================
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.get_logger().error('Failed to open camera')
        else:
            self.get_logger().info('Camera opened successfully (index 0)')
        
        # ============================================================================
        # [2.4] Create converter between ROS and OpenCV images
        # ============================================================================
        self.br = CvBridge()
        self.get_logger().info('CvBridge initialized')

    def timer_callback(self):
        # ============================================================================
        # [2.5] Read frame from camera
        # ============================================================================
        ret, frame = self.cap.read()
        
        # ============================================================================
        # [2.6] If frame captured successfully, publish to video_frames topic
        # ============================================================================
        if ret:
            try:
                # ============================================================================
                # [2.7] Convert OpenCV image to ROS Image message and publish
                # ============================================================================
                img_msg = self.br.cv2_to_imgmsg(frame, encoding="bgr8")
                self.publisher_.publish(img_msg)
                self.get_logger().debug(f'Published image: {img_msg.width}x{img_msg.height}')
            except Exception as e:
                self.get_logger().error(f'Error publishing image: {e}')
        else:
            self.get_logger().warn('Failed to read frame from camera')

    def destroy_node(self):
        # ============================================================================
        # [2.8] Release camera resources before destroying node
        # ============================================================================
        self.get_logger().info('Destroying ImagePublisher node...')
        if self.cap.isOpened():
            self.cap.release()
            self.get_logger().info('Camera released')
        super().destroy_node()
        self.get_logger().info('ImagePublisher node destroyed')


# ============================================================================
# 3. Main function
# ============================================================================
def main(args=None):
    
    # ============================================================================
    # [1] Initialize ROS 2
    # ============================================================================
    rclpy.init(args=args)
    print('ROS 2 initialized')
    
    # ============================================================================
    # [2] Create ImagePublisher node instance (triggers __init__: [2.1]-[2.4])
    # ============================================================================
    image_publisher = ImagePublisher()
    image_publisher.get_logger().info('Starting ImagePublisher node...')
    
    # ============================================================================
    # [3] Spin the node to keep it alive (triggers callbacks: [2.5]-[2.7])
    # ============================================================================
    try:
        image_publisher.get_logger().info('Node spinning, publishing images...')
        rclpy.spin(image_publisher)
    except KeyboardInterrupt:
        image_publisher.get_logger().info('Keyboard interrupt received')
    except Exception as e:
        image_publisher.get_logger().error(f'Error during node execution: {e}')
    
    # ============================================================================
    # [4] Clean up (triggers destroy_node: [2.8])
    # ============================================================================
    image_publisher.destroy_node()
    rclpy.shutdown()
    print('ROS 2 shutdown complete')


if __name__ == '__main__':
    main()
