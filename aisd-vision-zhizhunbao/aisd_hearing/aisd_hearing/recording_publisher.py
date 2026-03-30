#!/usr/bin/env python
from ament_index_python.packages import get_package_share_directory 
from sys import byteorder
import sys
from array import array
from struct import pack
import os

import pyaudio
import wave
import audioop
import threading

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


THRESHOLD = 2000  # Higher threshold to reject background noise and prevent Whisper hallucinations
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
MAX_WAIT_CHUNKS = 1000  # Wait up to ~100 seconds for sound to start
MAX_RECORDING_CHUNKS = 3000  # Maximum ~300 seconds (5 minutes) of recording to prevent infinite recording (safety limit)
SILENT_CHUNKS_REQUIRED = 32  # ~2 seconds of silence to stop recording (faster response in Q&A mode)
MAX_RECORDING_TIME = 15  # Maximum recording time in seconds (a single question rarely exceeds 15s)

class RecordingPublisher(Node):
    def __init__(self):
        super().__init__('recording_publisher')
        self.get_logger().info('RecordingPublisher node initialized')
        self.publisher_ = self.create_publisher(String, 'recording', 10)
        self.get_logger().info('Publisher created on topic: recording')
        self.listening = False
        
        # Start recording loop in a separate thread to avoid blocking the node
        self.recording_thread = threading.Thread(target=self._recording_loop, daemon=True)
        self.recording_thread.start()
        self.get_logger().info('Recording thread started')

    def _recording_loop(self):
        """Recording loop that runs in a separate thread"""
        ##################################
        # TODO (not required for Assignment 3) Change the audio_path to a parameter
        ##################################
        audio_path = get_package_share_directory('aisd_hearing')
        audio_path =  audio_path + "/recordings"
        # Ensure recordings directory exists
        if not os.path.exists(audio_path):
            os.makedirs(audio_path)
            self.get_logger().info('Created recordings directory: %s' % audio_path)
        device = find_device(sys.argv)
        rate = 16000
        self.get_logger().info('Using audio device: %d, sample rate: %d Hz' % (device, rate))
        while 1:
            current_time = str(self.get_clock().now().nanoseconds)
            audio_file = "{}/{}.wav".format(audio_path, current_time)
            self.get_logger().debug('Recording to: %s' % audio_file)

            try:
                self.get_logger().info('[Recording] Starting new recording...')
                record_to_file(audio_file, rate=rate, device=device, logger=self.get_logger())
                
                # Verify file exists before publishing
                if not os.path.exists(audio_file):
                    self.get_logger().error(f'[Error] File not created: {audio_file}')
                    continue  # Skip publishing this file
                else:
                    file_size = os.path.getsize(audio_file)
                    file_size_kb = file_size / 1024
                    self.get_logger().info(f'[Recording] Completed: {file_size_kb:.1f} KB')
            except Exception as e:
                self.get_logger().error(f'[Error] Recording failed: {str(e)}')
                import traceback
                self.get_logger().error(traceback.format_exc())
                continue
        
            # Publish file path
            if os.path.exists(audio_file):
                msg = String()
                msg.data = audio_file
                self.publisher_.publish(msg)
                filename = os.path.basename(audio_file)
                self.get_logger().info(f'[Publish] File published to ROS topic: {filename}')
            else:
                self.get_logger().error(f'[Error] Cannot publish - file does not exist')

##############################
# There are 6 methods needed from unr_deepspeech_client.py
# Your task here is to figure out which methods those are, and paste them
# here in place of this comment
# You are not required to make those methods part of the
# RecordingPublsher class definition, but that would be better programming style.
##############################

def is_silent(snd_data):
    "Returns 'True' if below the 'silent' threshold"
    return max(snd_data) < THRESHOLD

def normalize(snd_data):
    "Average the volume out"
    if len(snd_data) == 0:
        return array('h')
    MAXIMUM = 16384
    times = float(MAXIMUM)/max(abs(i) for i in snd_data)

    r = array('h')
    for i in snd_data:
        r.append(int(i*times))
    return r

def trim(snd_data):
    "Trim the blank spots at the start and end"
    def _trim(snd_data):
        snd_started = False
        r = array('h')

        for i in snd_data:
            if not snd_started and abs(i)>THRESHOLD:
                snd_started = True
                r.append(i)

            elif snd_started:
                r.append(i)
        return r

    # Trim to the left
    snd_data = _trim(snd_data)

    # Trim to the right
    snd_data.reverse()
    snd_data = _trim(snd_data)
    snd_data.reverse()
    return snd_data

def add_silence(snd_data, seconds, rate):
    "Add silence to the start and end of 'snd_data' of length 'seconds' (float)"
    r = array('h', [0 for i in range(int(seconds*rate))])
    r.extend(snd_data)
    r.extend([0 for i in range(int(seconds*rate))])
    return r

def record(rate, device, logger=None):
    """
    Record a word or words from the microphone and
    return the data as an array of signed shorts.

    Normalizes the audio, trims silence from the
    start and end, and pads with 0.5 seconds of
    blank sound to make sure VLC et al can play
    it without getting chopped off.
    """
    if logger is None:
        import logging
        logger = logging.getLogger('recording_publisher')
    
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=1, rate=rate,
        input=True, output=True, frames_per_buffer=CHUNK_SIZE,
        input_device_index=device)

    num_silent = 0
    snd_started = False
    chunks_waited = 0
    last_status = None  # Track last printed status to avoid duplicate prints
    chunk_count = 0  # Track total chunks for periodic status updates

    r = array('h')

    logger.info("[Recording] Waiting for sound input... (speak now)")
    while 1:
        chunk_count += 1
        # little endian, signed short
        snd_data = array('h', stream.read(CHUNK_SIZE, exception_on_overflow=False))
        if byteorder == 'big':
            snd_data.byteswap()
        r.extend(snd_data)

        silent = is_silent(snd_data)
        max_amplitude = max(abs(i) for i in snd_data) if len(snd_data) > 0 else 0

        # Continuously log audio status (reduced verbosity)
        if silent:
            if last_status != 'silent':
                logger.debug("No sound detected")
                last_status = 'silent'
        else:
            if last_status != 'sound':
                logger.debug(f"Sound detected (level: {max_amplitude})")
                last_status = 'sound'

        if not snd_started:
            chunks_waited += 1
            # Keep waiting for actual speech — do not auto-start on silence
            # This prevents Whisper from hallucinating on background noise
            if chunks_waited > MAX_WAIT_CHUNKS:
                logger.info("[Recording] Still waiting for speech input...")
                chunks_waited = 0  # Reset and keep waiting
                r = array('h')  # Clear accumulated silence data

        if silent and snd_started:
            num_silent += 1
        elif not silent and not snd_started:
            snd_started = True
            logger.info(f"[Recording] Started (audio level: {max_amplitude})")
            last_status = None  # Reset status tracking
        elif not silent and snd_started:
            # Reset silent counter when sound is detected again
            if num_silent > 0:
                num_silent = 0
        
        # Periodic status update every 100 chunks (~10 seconds at 16000 Hz)
        if snd_started and chunk_count % 100 == 0:
            total_seconds = chunk_count * CHUNK_SIZE / rate
            if num_silent == 0:
                # Sound detected - show audio level
                logger.info(f"[Recording] Progress: {total_seconds:.1f}s / {MAX_RECORDING_TIME}s (Sound detected, level: {max_amplitude})")
            else:
                # Silence detected - show silence count
                logger.info(f"[Recording] Progress: {total_seconds:.1f}s / {MAX_RECORDING_TIME}s (Silence: {num_silent}/{SILENT_CHUNKS_REQUIRED})")

        # Check for silence-based stop (reduced requirement for noisy environments)
        if snd_started and num_silent > SILENT_CHUNKS_REQUIRED:
            total_seconds = chunk_count * CHUNK_SIZE / rate
            logger.info(f"[Recording] Stopped: Silence detected ({total_seconds:.1f}s recorded)")
            break
        
        # Time-based auto-stop: stop after MAX_RECORDING_TIME seconds even if there's sound
        if snd_started:
            total_seconds = chunk_count * CHUNK_SIZE / rate
            if total_seconds >= MAX_RECORDING_TIME:
                logger.info(f"[Recording] Stopped: Time limit reached ({MAX_RECORDING_TIME}s)")
                break
        
        # Prevent infinite recording if there's continuous sound (safety limit)
        if snd_started and len(r) // CHUNK_SIZE > MAX_RECORDING_CHUNKS:
            total_seconds = chunk_count * CHUNK_SIZE / rate
            logger.info(f"[Recording] Stopped: Safety limit reached ({total_seconds:.1f}s)")
            break

    sample_width = p.get_sample_size(FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()

    r = normalize(r)
    r = trim(r)
    r = add_silence(r, 0.5, rate)
    return sample_width, r

def record_to_file(path, rate, device, logger=None):
    "Records from the microphone and outputs the resulting data to 'path'"
    if logger is None:
        import logging
        logger = logging.getLogger('recording_publisher')
    
    sample_width, data = record(rate, device, logger=logger)
    logger.info(f"[Recording] Finished: {len(data)} samples captured")

    if rate != 16000:
        data_16GHz = audioop.ratecv(data, sample_width, 1, rate, 16000, None)[0]
    else:
        data_16GHz = pack('<' + ('h'*len(data)), *data)
        
    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(sample_width)
    wf.setframerate(16000)
    wf.writeframes(data_16GHz)
    wf.close()
    logger.info(f"[File] Saved: {os.path.basename(path)}")

def find_device(args):
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    
    device = -1
    
    import logging
    logger = logging.getLogger('recording_publisher')
    
    if len(args) > 1 and args[1] != "--ros-args":
        if args[1] == "-1":
            logger.info("\nListing audio devices and exiting: ")
            # Print audio devices
            # Ref: https://stackoverflow.com/a/39677871
            for i in range(0, numdevices):
                if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    logger.info("Input Device id %d - %s" % (i, p.get_device_info_by_host_api_device_index(0, i).get('name')))
            sys.exit(0)
        else:
            try:
                device = int(args[1])
            except ValueError:
                logger.error("Invalid audio device id.")
                logger.error("usage: ros2 run aisd_hearing recording_publisher [audio_device_index]")
                sys.exit(1)
    elif len(args) == 1 or (len(args) > 1 and args[1] == "--ros-args"): # search for default device        
        for i in range(0, numdevices):
             if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                 if p.get_device_info_by_host_api_device_index(0, i).get('name') == 'default':
                     device = i
                     logger.info("Using device {}".format(i))
                     break
        if device == -1:
            logger.error("Unable to find default device. Here are the available audio devices: ")
            for i in range(0, numdevices):
                if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    logger.error("Input Device id %d - %s" % (i, p.get_device_info_by_host_api_device_index(0, i).get('name')))
            sys.exit(1)
    else:
        logger.error("usage: ros2 run aisd_hearing recording_publisher [audio_device_index]")
        sys.exit(1)

    return device
        
def main(args=None):
   ############################
   # Place the standard code for a publisher here
   ############################
   rclpy.init(args=args)
   recording_publisher = RecordingPublisher()
   recording_publisher.get_logger().info('ROS 2 initialized')
   recording_publisher.get_logger().info('Starting RecordingPublisher node...')
   try:
       recording_publisher.get_logger().info('Node spinning, recording audio...')
       rclpy.spin(recording_publisher)
   except KeyboardInterrupt:
       recording_publisher.get_logger().info('Keyboard interrupt received')
   except Exception as e:
       recording_publisher.get_logger().error('Error during node execution: %s' % str(e))
   finally:
       recording_publisher.get_logger().info('ROS 2 shutdown complete')
       recording_publisher.destroy_node()
       rclpy.shutdown()

if __name__ == "__main__":
    main()
