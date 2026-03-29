#!/usr/bin/env python3
"""
ROS2 Ollama Publisher Node — RAG-based response generation.
Subscribes to 'words' topic (Whisper STT output),
publishes responses to 'ollama_reply' topic.

Converted from Part 1 RAG engine to ROS2 node for Part 2.
"""

import os
import sys

# Import ROS2 dependencies
try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import String
except ImportError:
    print("ROS2 (rclpy) not installed. This module requires ROS2 environment.")
    print("Run this on the loaner laptop with ROS2 installed.")
    sys.exit(1)

from ollama import Client


class OllamaPublisher(Node):
    """
    ROS2 node that integrates the RAG engine.
    Subscribes to Whisper STT output and publishes RAG-based responses.
    """

    def __init__(self):
        super().__init__('ollama_publisher')

        # Declare ROS parameters
        self.declare_parameter('model', 'qwen2.5:0.5b')
        self.declare_parameter('rag_path',
                               '/home/aisd/aisd_ali/knowledge/ragfile.txt')
        self.declare_parameter('ollama_host', 'http://localhost:11434')

        # Get parameter values
        self.model = (
            self.get_parameter('model')
            .get_parameter_value().string_value
        )
        self.rag_path = (
            self.get_parameter('rag_path')
            .get_parameter_value().string_value
        )
        self.ollama_host = (
            self.get_parameter('ollama_host')
            .get_parameter_value().string_value
        )

        # Initialize Ollama client
        self.client = Client(host=self.ollama_host)

        # Load RAG context from knowledge file
        self.rag_context = ""
        if os.path.isfile(self.rag_path):
            try:
                with open(self.rag_path, 'r', encoding='utf-8') as f:
                    self.rag_context = f.read().strip()
                self.get_logger().info(f'Loaded RAG file: {self.rag_path}')
            except Exception as e:
                self.get_logger().error(f'Failed to read RAG file: {e}')
        else:
            self.get_logger().warn(f'RAG file not found: {self.rag_path}')

        # Publisher: ollama_reply topic
        self.pub = self.create_publisher(String, 'ollama_reply', 10)

        # Subscriber: words topic (Whisper output)
        self.sub = self.create_subscription(String, 'words', self.cb, 10)

        # Busy flag to prevent concurrent processing
        self.busy = False

        self.get_logger().info(
            f'OllamaPublisher initialized: model={self.model}'
        )

    def cb(self, msg: String):
        """Callback for incoming speech-to-text words."""
        text = msg.data.strip()
        if text == "" or self.busy:
            return

        self.busy = True
        self.get_logger().info(f'WORDS: "{text}"')

        try:
            reply = self.ask_ollama(text)
        except Exception as e:
            self.get_logger().error(f'Ollama error: {e}')
            self.busy = False
            return

        reply = (reply or "").strip()
        if reply:
            out = String()
            out.data = reply
            self.pub.publish(out)
            self.get_logger().info(f'OLLAMA_REPLY: "{out.data}"')

        self.busy = False

    def ask_ollama(self, user_text: str) -> str:
        """Generate a response using Ollama with RAG context."""
        system_parts = [
            "You are an AI textbook assistant. "
            "Answer questions about AI, ML, and NLP concepts accurately. "
            "Keep responses concise but informative."
        ]

        if self.rag_context:
            system_parts.append(
                "Use the following knowledge as the primary source of truth:"
            )
            system_parts.append(self.rag_context)

        system_prompt = "\n\n".join(system_parts)

        res = self.client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
        )
        return res["message"]["content"]


def main(args=None):
    rclpy.init(args=args)
    node = OllamaPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
