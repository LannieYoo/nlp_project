#!/usr/bin/env python

from std_msgs.msg import String
from aisd_msgs.srv import Speak
import rclpy
from rclpy.node import Node

class SpeakClient(Node):
    def __init__(self):
        super().__init__('speak_client')
        self.get_logger().info('[Init] SpeakClient node initialized')
        self.cli = self.create_client(Speak, 'speak')
        self.get_logger().info('[Service] Waiting for speak service...')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('[Service] Service not available, waiting...')
        self.get_logger().info('[Service] Speak service is available')
        self.subscription = self.create_subscription(
            String,
            'ollama_reply',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning
        self.get_logger().info('[Subscribe] Subscribed to topic: ollama_reply')
        self.pending_requests = {}  # Track pending requests: {future_id: text}

    def listener_callback(self, msg):
        """Handle incoming words messages - non-blocking"""
        self.get_logger().info(f'[Words] Received: "{msg.data}"')
        self.send_request_async(msg.data)

    def send_request_async(self, text):
        """Send service request asynchronously without blocking the callback"""
        self.get_logger().debug(f'[TTS] Sending request: "{text}"')
        req = Speak.Request()
        req.words = text
        future = self.cli.call_async(req)
        # Store the future with the text for logging (using id for tracking)
        request_id = id(future)
        self.pending_requests[request_id] = text
        future.add_done_callback(lambda f: self.service_response_callback(f, request_id))

    def service_response_callback(self, future, request_id):
        """Handle service response asynchronously"""
        text = self.pending_requests.pop(request_id, "unknown")
        try:
            result = future.result()
            self.get_logger().info(f'[TTS] Response for "{text}": "{result.response}"')
        except Exception as e:
            self.get_logger().error(f'[Error] Service call failed for "{text}": {str(e)}')

def main(args=None):
    rclpy.init(args=args)
    speak_client = SpeakClient()
    speak_client.get_logger().info('[Init] ROS 2 initialized')
    speak_client.get_logger().info('[Init] Starting SpeakClient node...')
    try:
        speak_client.get_logger().info('[Run] Node spinning, waiting for words...')
        rclpy.spin(speak_client)
    except KeyboardInterrupt:
        speak_client.get_logger().info('[Shutdown] Keyboard interrupt received')
    except Exception as e:
        speak_client.get_logger().error(f'[Error] Node execution failed: {str(e)}')
    finally:
        speak_client.destroy_node()
        rclpy.shutdown()
        speak_client.get_logger().info('[Shutdown] ROS 2 shutdown complete')

if __name__ == "__main__":
    main()
