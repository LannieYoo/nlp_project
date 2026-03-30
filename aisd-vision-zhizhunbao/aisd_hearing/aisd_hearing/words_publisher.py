#!/usr/bin/env python
"""
Words Publisher — Whisper STT Node (using faster-whisper + Silero VAD)

Uses faster-whisper with built-in Silero VAD to:
  1. Filter out non-speech audio BEFORE transcription (prevents hallucinations)
  2. Transcribe speech segments with CTranslate2 backend (4-6x faster)
"""

from std_msgs.msg import String
import rclpy
from rclpy.node import Node

import os

from faster_whisper import WhisperModel

class WordsPublisher(Node):
    def __init__(self):
        super().__init__('words_publisher')
        self.get_logger().info('[Init] WordsPublisher node initialized')
        self.publisher_ = self.create_publisher(String, 'words', 10)
        self.get_logger().info('[Publish] Publisher created on topic: words')
        self.subscription = self.create_subscription(
            String,
            'recording',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning
        self.get_logger().info('[Subscribe] Subscribed to topic: recording')

        # faster-whisper: CTranslate2 backend, ~4-6x faster than openai-whisper
        # 'small' model: 244M params, good Chinese+English accuracy, reasonable on CPU
        self.get_logger().info('[Whisper] Loading faster-whisper model (small, int8)...')
        self.model = WhisperModel("small", device="cpu", compute_type="int8")
        self.get_logger().info('[Whisper] Model loaded successfully')

    def listener_callback(self, msg):
        filename = os.path.basename(msg.data)
        self.get_logger().info(f'[Whisper] Analyzing: {filename}')
        try:
            # Check if file exists
            if not os.path.exists(msg.data):
                self.get_logger().error(f'[Error] Audio file does not exist: {filename}')
                return

            transcribed_text = self.mystt(msg.data)
            self.get_logger().info(f'[Transcribe] Result: "{transcribed_text}"')

            # Filter out remaining edge-case hallucinations
            if self._is_hallucination(transcribed_text):
                self.get_logger().warn(f'[Filter] Skipped hallucination: "{transcribed_text[:80]}..."')
                return

            text = String()
            text.data = transcribed_text
            self.publisher_.publish(text)
            self.get_logger().info('[Publish] Text published to words topic')
        except Exception as e:
            self.get_logger().error(f'[Error] Processing failed: {str(e)}')
            import traceback
            self.get_logger().error(traceback.format_exc())

    def mystt(self, audio_path):
        """Transcribe audio using faster-whisper with Silero VAD pre-filtering."""
        segments, info = self.model.transcribe(
            audio_path,
            language=None,                      # auto-detect language (supports Chinese + English)
            beam_size=1,                        # greedy decoding: fail fast on silence
            temperature=0,                      # deterministic output
            condition_on_previous_text=False,    # prevent hallucination carry-over
            vad_filter=True,                     # ** Silero VAD: skip non-speech segments **
            vad_parameters=dict(
                min_silence_duration_ms=500,     # merge speech chunks separated by <500ms
                speech_pad_ms=200,               # pad speech segments by 200ms
                threshold=0.5,                   # VAD confidence threshold
            ),
        )

        # Collect text from speech segments only
        texts = []
        for segment in segments:
            self.get_logger().debug(
                f'[VAD] Segment [{segment.start:.1f}s - {segment.end:.1f}s]: "{segment.text.strip()}"'
            )
            texts.append(segment.text.strip())

        result = " ".join(texts).strip()

        if not result:
            self.get_logger().info('[VAD] No speech detected in audio (all filtered by VAD)')

        return result

    def _is_hallucination(self, text: str) -> bool:
        """Detect remaining Whisper hallucinations that slip past VAD."""
        t = text.strip().lower()

        # Empty or too short
        if len(t) == 0:
            return True

        # For Chinese text (no spaces), check character count
        # For English text (with spaces), check word count
        words = t.split()
        if len(words) <= 1 and len(t) < 2:
            return True

        # Known Whisper hallucination phrases (substring match)
        hallucination_phrases = [
            "thank you", "thanks for watching", "subscribe",
            "like and subscribe", "please subscribe",
            "bye", "goodbye", "see you",
            "the end", "silence",
            "thanks for listening", "thank you for watching",
            "you're watching", "stay tuned",
        ]
        for phrase in hallucination_phrases:
            if phrase in t:
                return True

        # Detect repetitive text (same phrases repeated)
        words = t.split()
        if len(words) > 4:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.35:
                return True

        # Detect repeated n-grams (e.g. "we are not going to" x5)
        if len(words) > 8:
            trigrams = [" ".join(words[i:i+3]) for i in range(len(words)-2)]
            trigram_counts = {}
            for tg in trigrams:
                trigram_counts[tg] = trigram_counts.get(tg, 0) + 1
            max_repeat = max(trigram_counts.values()) if trigram_counts else 0
            if max_repeat >= 3:
                return True

        return False

def main(args=None):
   rclpy.init(args=args)
   words_publisher = WordsPublisher()
   words_publisher.get_logger().info('[Init] ROS 2 initialized')
   words_publisher.get_logger().info('[Init] Starting WordsPublisher node...')
   try:
       words_publisher.get_logger().info('[Run] Node spinning, waiting for recordings...')
       rclpy.spin(words_publisher)
   except KeyboardInterrupt:
       words_publisher.get_logger().info('[Shutdown] Keyboard interrupt received')
   except Exception as e:
       words_publisher.get_logger().error(f'[Error] Node execution failed: {str(e)}')
   finally:
       words_publisher.destroy_node()
       rclpy.shutdown()
       words_publisher.get_logger().info('[Shutdown] ROS 2 shutdown complete')

if __name__ == "__main__":
    main()

