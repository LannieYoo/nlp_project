#!/usr/bin/env python3
"""
ROS 2 RAG Ollama Publisher Node (Local Ollama Version).

Subscribes to the 'words' topic (Whisper STT output),
uses a local knowledge file for RAG context,
calls the local Ollama API to generate an answer,
and publishes the response to the 'ollama_reply' topic.

Architecture:
  [Whisper STT] --words--> [OllamaPublisher] --ollama_reply--> [SpeakClient]

Requirements:
  - Ollama installed and running locally (ollama serve)
  - Model pulled (e.g., ollama pull qwen2.5:0.5b)
  - Knowledge file at ~/ros2_ws/knowledge/knowledge.txt
"""
import os
import sys

try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import String
except ImportError:
    print("ROS2 (rclpy) not installed. This module requires ROS2 environment.")
    sys.exit(1)

try:
    from ollama import Client, ResponseError
except ImportError:
    print("'ollama' library not installed. Run: pip install ollama")
    sys.exit(1)


class OllamaPublisher(Node):
    """
    ROS 2 node that bridges Whisper speech-to-text output
    to the local Ollama language model with RAG context.

    Parameters
    ----------
    model : str
        Ollama model name (default: 'qwen2.5:0.5b').
    rag_path : str
        Path to the knowledge file for RAG context.
    """

    def __init__(self):
        super().__init__('ollama_publisher')

        # ── ROS 2 Parameters ─────────────────────────────────────────────
        self.declare_parameter('model', 'qwen2.5:0.5b')
        self.model = (
            self.get_parameter('model').get_parameter_value().string_value
        )

        self.declare_parameter('rag_path',
            os.path.expanduser('~/ros2_ws/knowledge/knowledge.txt'))
        self.rag_path = (
            self.get_parameter('rag_path').get_parameter_value().string_value
        )

        # ── Ollama Client (local) ────────────────────────────────────────
        self.client = Client(host='http://localhost:11434')

        # ── Load RAG Knowledge File ──────────────────────────────────────
        self.rag_context = ""
        if os.path.isfile(self.rag_path):
            try:
                with open(self.rag_path, 'r', encoding='utf-8') as f:
                    self.rag_context = f.read().strip()
                size_kb = len(self.rag_context) / 1024
                self.get_logger().info(
                    f'[Init] Loaded RAG file: {self.rag_path} ({size_kb:.1f} KB)'
                )
            except Exception as e:
                self.get_logger().error(f'[Error] Failed to read RAG file: {e}')
        else:
            self.get_logger().warn(f'[Init] RAG file not found: {self.rag_path}')

        # ── Publisher: ollama_reply ───────────────────────────────────────
        self.pub = self.create_publisher(String, 'ollama_reply', 10)

        # ── Subscriber: words (from Whisper STT) ─────────────────────────
        self.sub = self.create_subscription(String, 'words', self.cb, 10)

        # Prevent overlapping requests
        self.busy = False

        self.get_logger().info(
            f'[Init] OllamaPublisher initialized\n'
            f'  Model     : {self.model}\n'
            f'  RAG File  : {self.rag_path}\n'
            f'  Ollama API: http://localhost:11434'
        )

    # ── Callback: Incoming speech text ───────────────────────────────────
    def cb(self, msg: String):
        """Handle incoming transcribed text from the Whisper model."""
        import time

        text = msg.data.strip()
        if text == "" or self.busy:
            return

        # Cooldown: ignore input for N seconds after last reply (prevents echo loop)
        if hasattr(self, '_last_reply_time'):
            elapsed = time.time() - self._last_reply_time
            if elapsed < 15:  # 15 seconds cooldown for TTS to finish
                self.get_logger().info(
                    f'[Cooldown] Ignoring input ({elapsed:.0f}s < 15s since last reply)'
                )
                return

        self.busy = True
        self.get_logger().info(f'[Words] Received: "{text}"')

        try:
            reply = self.ask_ollama(text)
        except ResponseError as e:
            self.get_logger().error(f'[Error] Ollama API error: {e.error}')
            self.busy = False
            return
        except Exception as e:
            self.get_logger().error(f'[Error] Ollama error: {e}')
            self.busy = False
            return

        reply = (reply or "").strip()
        if reply:
            out = String()
            out.data = reply
            self.pub.publish(out)
            self.get_logger().info(f'[Reply] Published: "{out.data}"')
            self._last_reply_time = time.time()  # Start cooldown
        else:
            self.get_logger().warn('[Reply] Empty response from Ollama')

        self.busy = False

    # ── RAG Query via Local Ollama ───────────────────────────────────────
    def ask_ollama(self, user_text: str) -> str:
        """
        Generate a RAG-grounded response using local Ollama.

        The knowledge file content is included in the system prompt
        so that the model's responses are grounded in the domain data.
        """
        system_parts = [
            "You are a helpful AI assistant specializing in AI, ML, and NLP topics.",
            "Answer questions concisely based on the provided knowledge context.",
            "If the answer is not in the context, say so honestly.",
            "Reply in 2-3 short, clear sentences.",
        ]

        if self.rag_context:
            system_parts.append(
                "\n--- Knowledge Context ---\n"
                "Use the following information to answer the user's question:\n"
            )
            system_parts.append(self.rag_context)

        system_prompt = "\n".join(system_parts)

        self.get_logger().info(
            f'[Ollama] Sending query to local Ollama ({self.model})...'
        )

        res = self.client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
        )

        answer = res["message"]["content"]
        self.get_logger().info(f'[Ollama] Response generated ({len(answer)} chars)')
        return answer


def main(args=None):
    rclpy.init(args=args)
    node = OllamaPublisher()
    try:
        node.get_logger().info('[Run] Node spinning, waiting for words...')
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('[Shutdown] Keyboard interrupt received')
    except Exception as e:
        node.get_logger().error(f'[Error] Node execution failed: {str(e)}')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
