# ============================================================================
# 1. Import required modules
# ============================================================================
import io
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from aisd_msgs.srv import Speak
import rclpy
from rclpy.node import Node


# ============================================================================
# 2. SpeakService class: Provides text-to-speech service
# ============================================================================
class SpeakService(Node):

    def __init__(self):
        super().__init__('speak_service')
        self.get_logger().info('SpeakService node initialized')
        
        # ============================================================================
        # [2.1] Create service server for Speak service
        # ============================================================================
        self.srv = self.create_service(Speak, 'speak', self.speak_callback)
        self.get_logger().info('Service server created: speak')

    def speak_callback(self, request, response):
        """
        Service callback function that converts text to speech and plays it.
        
        Args:
            request: Speak.Request containing text to speak
            response: Speak.Response to return
            
        Returns:
            Speak.Response: Response with status message
        """
        # ============================================================================
        # [2.2] Log received text
        # ============================================================================
        self.get_logger().info(f'Received text-to-speech request: "{request.words}"')
        
        # ============================================================================
        # [2.3] Create in-memory file-like object (BytesIO) to store audio data
        # ============================================================================
        with io.BytesIO() as f:
            # ============================================================================
            # [2.4] Generate speech from text using Google Text-to-Speech (gTTS)
            # lang='en': Specify English language
            # write_to_fp: Write MP3 audio data directly to file-like object
            # ============================================================================
            gTTS(text=request.words, lang='en').write_to_fp(f)
            
            # ============================================================================
            # [2.5] Reset file pointer to beginning for reading
            # ============================================================================
            f.seek(0)
            
            # ============================================================================
            # [2.6] Load MP3 audio from BytesIO object using pydub
            # ============================================================================
            song = AudioSegment.from_file(f, format="mp3")
            
            # ============================================================================
            # [2.7] Play the audio using pydub's playback module
            # ============================================================================
            play(song)
            self.get_logger().info('Audio playback completed')
        
        # ============================================================================
        # [2.8] Set response message to indicate success
        # ============================================================================
        response.response = "OK"
        self.get_logger().info('Service response: OK')
        return response


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
    # [2] Create SpeakService node instance (triggers __init__: [2.1])
    # ============================================================================
    speak_service = SpeakService()
    speak_service.get_logger().info('Starting SpeakService node...')
    
    # ============================================================================
    # [3] Spin the node to keep it alive (triggers callbacks: [2.2]-[2.8])
    # ============================================================================
    try:
        speak_service.get_logger().info('Node spinning, waiting for service requests...')
        rclpy.spin(speak_service)
    except KeyboardInterrupt:
        speak_service.get_logger().info('Keyboard interrupt received')
    except Exception as e:
        speak_service.get_logger().error(f'Error during node execution: {e}')
    
    # ============================================================================
    # [4] Clean up
    # ============================================================================
    speak_service.destroy_node()
    rclpy.shutdown()
    print('ROS 2 shutdown complete')


if __name__ == '__main__':
    main()

