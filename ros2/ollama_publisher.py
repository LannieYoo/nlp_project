#!/usr/bin/env python3
"""
ROS 2 RAG Ollama Publisher Node (Part 2).

Subscribes to the 'words' topic (Whisper STT output),
sends the query to the Windows FastAPI RAG backend via HTTP,
and publishes the generated answer to the 'ollama_reply' topic.

Architecture:
  [Whisper STT] --words--> [OllamaPublisher] --ollama_reply--> [SpeakClient]

The FastAPI backend (running on the Windows PC) handles:
  - Document retrieval (BM25 + vector search)
  - Ollama LLM generation (qwen2.5:0.5b)
  - RAG-grounded answer synthesis
"""
import sys

try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import String
except ImportError:
    print("ROS2 (rclpy) not installed. This module requires ROS2 environment.")
    print("Run this on the loaner laptop with ROS2 installed.")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("'requests' library not installed. Run: pip install requests")
    sys.exit(1)


class OllamaPublisher(Node):
    """
    ROS 2 node that bridges Whisper speech-to-text output
    to the RAG-powered Ollama language model backend.

    Parameters
    ----------
    api_url : str
        URL of the FastAPI search endpoint on the Windows PC.
        Default: 'http://192.168.x.x:8000/api/search'
        (Replace with actual Windows PC IP from `ipconfig`)
    model : str
        Ollama model name to use for generation (default: 'qwen2.5:0.5b').
    top_k : int
        Number of source documents to retrieve (default: 3).

    Subscriptions
    -------------
    words : std_msgs/String
        Transcribed text from Whisper STT (words_publisher).

    Publications
    ------------
    ollama_reply : std_msgs/String
        Generated answer from the RAG pipeline.
    """

    def __init__(self):
        super().__init__('ollama_publisher')

        # ── ROS 2 Parameters ─────────────────────────────────────────────
        # Windows PC's IP address + FastAPI endpoint
        # (use `ipconfig` on Windows terminal to find the IP)
        self.declare_parameter('api_url', 'http://192.168.x.x:8000/api/search')
        self.api_url = (
            self.get_parameter('api_url').get_parameter_value().string_value
        )

        self.declare_parameter('model', 'qwen2.5:0.5b')
        self.model = (
            self.get_parameter('model').get_parameter_value().string_value
        )

        self.declare_parameter('top_k', 3)
        self.top_k = (
            self.get_parameter('top_k').get_parameter_value().integer_value
        )

        # ── Publisher: ollama_reply ───────────────────────────────────────
        self.pub = self.create_publisher(String, 'ollama_reply', 10)

        # ── Subscriber: words (from Whisper STT) ─────────────────────────
        self.sub = self.create_subscription(String, 'words', self.cb, 10)

        # Prevent overlapping requests
        self.busy = False

        self.get_logger().info(
            f'[Init] OllamaPublisher initialized\n'
            f'  Backend API : {self.api_url}\n'
            f'  Model       : {self.model}\n'
            f'  Top-K       : {self.top_k}'
        )

    # ── Callback: Incoming speech text ───────────────────────────────────
    def cb(self, msg: String):
        """Handle incoming transcribed text from the Whisper model."""
        text = msg.data.strip()
        if text == "" or self.busy:
            return

        self.busy = True
        self.get_logger().info(f'[Words] Received: "{text}"')

        try:
            reply = self.ask_backend(text)
        except Exception as e:
            self.get_logger().error(f'[Error] Backend API error: {e}')
            self.busy = False
            return

        reply = (reply or "").strip()
        if reply:
            out = String()
            out.data = reply
            self.pub.publish(out)
            self.get_logger().info(f'[Reply] Published: "{out.data}"')
        else:
            self.get_logger().warn('[Reply] Empty response from backend')

        self.busy = False

    # ── RAG Query via FastAPI ────────────────────────────────────────────
    def ask_backend(self, user_text: str) -> str:
        """
        Call the FastAPI backend on the Windows PC to generate
        a RAG-grounded response.

        POST /api/search
        {
            "query": "<user_text>",
            "top_k": 3,
            "model": "qwen2.5:0.5b",
            "methods": ["fts", "vector"]
        }

        Returns the 'answer' field from the JSON response.
        """
        payload = {
            "query": user_text,
            "top_k": self.top_k,
            "model": self.model,
            "methods": ["fts", "vector"],
        }

        self.get_logger().info(
            f'[API] Sending request to {self.api_url} ...'
        )
        res = requests.post(self.api_url, json=payload, timeout=60.0)
        res.raise_for_status()

        data = res.json()
        answer = data.get("answer", "I could not find an answer.")

        # Log source documents for traceability
        sources = data.get("sources", [])
        if sources:
            self.get_logger().info(
                f'[API] Retrieved {len(sources)} source document(s)'
            )
            for i, src in enumerate(sources):
                self.get_logger().debug(
                    f'  Source {i+1}: {src.get("book_id", "?")} '
                    f'p.{src.get("page_idx", "?")} '
                    f'({src.get("method", "?")})'
                )

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
