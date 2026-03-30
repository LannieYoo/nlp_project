# ============================================================================
# 1. Import required modules
# ============================================================================
import rclpy
import time
from rclpy.node import Node
from geometry_msgs.msg import Twist
from aisd_msgs.msg import Hand


# ============================================================================
# 2. Move class: Subscribes to hand positions, calculates and publishes robot velocity commands
# ============================================================================
class Move(Node):

    def __init__(self):
        super().__init__('move')
        
        # ============================================================================
        # [2.1] Create subscriber for cmd_hand topic
        # ============================================================================
        self.subscription = self.create_subscription(
            Hand,
            'cmd_hand',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

        # ============================================================================
        # [2.2] Create publisher for Twist messages on cmd_vel topic
        # ============================================================================
        self.vel_publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        
        # ============================================================================
        # [2.3] Track last received message time
        # ============================================================================
        self.last_msg_time = None
        self.last_twist = Twist()  # Default: all zeros (stop)
        
        # ============================================================================
        # [2.4] Create timer to periodically publish stop command if no hand detected
        # ============================================================================
        self.timer = self.create_timer(0.1, self.timer_callback)  # 10Hz

    def listener_callback(self, msg):
        # ============================================================================
        # [2.5] Update last message received time
        # ============================================================================
        self.last_msg_time = time.time()
        
        # ============================================================================
        # [2.6] Initialize angle and linear velocity
        # ============================================================================
        angle = 0.0
        linear = 0.0

        # ============================================================================
        # [2.7] Determine angular velocity based on index finger position
        # ============================================================================
        if msg.xindex > 0.55:
            self.get_logger().info(f'Turn right gesture detected (index finger position: {msg.xindex:.2f})')
            angle = -0.1
        elif msg.xindex < 0.45:
            self.get_logger().info(f'Turn left gesture detected (index finger position: {msg.xindex:.2f})')
            angle = 0.1
        else:
            angle = 0.0

        # ============================================================================
        # [2.8] Determine linear velocity based on index and pinky finger positions
        # ============================================================================
        if msg.xindex > msg.xpinky:
            self.get_logger().info(f'Move forward gesture detected (index: {msg.xindex:.2f}, pinky: {msg.xpinky:.2f})')
            linear = 0.5
        else:
            self.get_logger().info(f'Stop gesture detected (index: {msg.xindex:.2f}, pinky: {msg.xpinky:.2f})')
            linear = 0.0

        # ============================================================================
        # [2.9] Create and configure Twist message
        # ============================================================================
        twist = Twist()
        twist.linear.x = linear
        twist.angular.z = angle
        self.last_twist = twist

        # ============================================================================
        # [2.10] Publish Twist message if subscribers exist
        # ============================================================================
        if self.vel_publisher.get_subscription_count() > 0:
            self.vel_publisher.publish(twist)
        else:
            self.get_logger().info('Waiting for cmd_vel topic subscribers...')
    
    def timer_callback(self):
        # ============================================================================
        # [2.11] If no message received in last 0.5 seconds, publish stop command
        # ============================================================================
        if self.last_msg_time is None or (time.time() - self.last_msg_time) > 0.5:
            stop_twist = Twist()  # All zeros = stop
            if self.vel_publisher.get_subscription_count() > 0:
                self.vel_publisher.publish(stop_twist)
        else:
            # ============================================================================
            # [2.12] Publish last received command to maintain motion
            # ============================================================================
            if self.vel_publisher.get_subscription_count() > 0:
                self.vel_publisher.publish(self.last_twist)


# ============================================================================
# 3. Main function
# ============================================================================
def main(args=None):
    
    # ============================================================================
    # [1] Initialize ROS 2
    # ============================================================================
    rclpy.init(args=args)
    
    # ============================================================================
    # [2] Create Move node instance (triggers __init__: [2.1]-[2.4])
    # ============================================================================
    move = Move()
    
    # ============================================================================
    # [3] Spin the node to keep it alive (triggers callbacks: [2.5]-[2.12])
    # ============================================================================
    rclpy.spin(move)
    
    # ============================================================================
    # [4] Clean up
    # ============================================================================
    move.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
