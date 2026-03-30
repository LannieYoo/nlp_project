# ============================================================================
# 1. Import required modules
# ============================================================================
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
from aisd_msgs.msg import Hand


# ============================================================================
# 2. Hands class: Subscribes to image topic, recognizes hand poses, and publishes hand landmark positions
# ============================================================================
class Hands(Node):

    def __init__(self):
        super().__init__('hands')
        
        # ============================================================================
        # [2.1] Create subscriber for video_frames topic
        # ============================================================================
        self.subscription = self.create_subscription(
            Image,
            'video_frames',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

        # ============================================================================
        # [2.2] Create converter between ROS and OpenCV images
        # ============================================================================
        self.br = CvBridge()
        
        # ============================================================================
        # [2.3] Create publisher for Hand messages on cmd_hand topic
        # ============================================================================
        self.hand_publisher = self.create_publisher(Hand, 'cmd_hand', 10)

    def listener_callback(self, msg):
        # ============================================================================
        # [2.4] Convert ROS Image message to OpenCV format
        # ============================================================================
        image = self.br.imgmsg_to_cv2(msg)

        # ============================================================================
        # [2.5] Define hand landmark indices for finger tips
        # ============================================================================
        PINKY_FINGER_TIP = 20
        INDEX_FINGER_TIP = 8

        # ============================================================================
        # [2.6] Initialize MediaPipe Hands detector and process image
        # ============================================================================
        with mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as myhands:

            # ============================================================================
            # [2.7] Mark image as not writeable to improve performance (pass by reference)
            # ============================================================================
            image.flags.writeable = False
            
            # ============================================================================
            # [2.8] Convert BGR to RGB for MediaPipe processing
            # ============================================================================
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # ============================================================================
            # [2.9] Process image to detect hand landmarks
            # ============================================================================
            results = myhands.process(image)

            # ============================================================================
            # [2.10] If hands detected, extract and publish finger positions
            # ============================================================================
            if results.multi_hand_landmarks:
                # ============================================================================
                # [2.11] Create Hand message with index finger and pinky positions
                # ============================================================================
                msg = Hand()
                msg.xpinky = results.multi_hand_landmarks[0].landmark[PINKY_FINGER_TIP].x
                msg.xindex = results.multi_hand_landmarks[0].landmark[INDEX_FINGER_TIP].x

                # ============================================================================
                # [2.12] Publish Hand message if subscribers exist
                # ============================================================================
                if self.hand_publisher.get_subscription_count() > 0:
                    self.hand_publisher.publish(msg)
                else:
                    self.get_logger().info('waiting for subscriber')


# ============================================================================
# 3. Main function
# ============================================================================
def main(args=None):
    
    # ============================================================================
    # [1] Initialize ROS 2
    # ============================================================================
    rclpy.init(args=args)
    
    # ============================================================================
    # [2] Create Hands node instance (triggers __init__: [2.1]-[2.3])
    # ============================================================================
    hands = Hands()
    
    # ============================================================================
    # [3] Spin the node to keep it alive (triggers callbacks: [2.4]-[2.12])
    # ============================================================================
    rclpy.spin(hands)
    
    # ============================================================================
    # [4] Clean up
    # ============================================================================
    hands.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
