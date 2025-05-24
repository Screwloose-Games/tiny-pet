# Run this with: python .github/scripts/validate-audio-files.py $(cat audio_files.txt)

import os
import sys
import wave

MAX_FILE_SIZE = 49 * 1024 * 1024  # 49 MB

WAV_FILE_SPECIFICATIONS = {
    "sample_rate": 44100,  # Hz
    "bit_depth": 16,       # bits per sample
    "channels": 1,         # 1 for mono, 2 for stereo
    "target_lufs": -16,    # LUFS loudness normalization
    "peak_volume": -1.0,   # dBFS, avoid clipping
    "looping": False,      # true only for seamless loops
    "filename_convention": {
        "casing": "lowercase",
        "separator": "underscore",
        "extension": ".wav"
    },
    "max_length": 10,      # seconds
    "max_file_size": MAX_FILE_SIZE,  # 49 MB
}

class AudioFileValidator:
    def __init__(self, file_path):
        self.file_path = file_path
        self.errors = []

    def validate(self):
        if not os.path.isfile(self.file_path):
            self.errors.append(f"File does not exist: {self.file_path}")
            return False

        file_size = os.path.getsize(self.file_path)
        if file_size > WAV_FILE_SPECIFICATIONS["max_file_size"]:
            self.errors.append(f"File size exceeds limit: {file_size} bytes > {WAV_FILE_SPECIFICATIONS['max_file_size']} bytes")
        
        if not self.file_path.endswith(WAV_FILE_SPECIFICATIONS["filename_convention"]["extension"]):
            self.errors.append(f"Invalid file extension: {self.file_path}")

        if not self.file_path.islower():
            self.errors.append(f"Filename is not lowercase: {self.file_path}")
        
        if "_" not in self.file_path:
            self.errors.append(f"Filename does not contain underscore: {self.file_path}")
        
        # is 16 bit depth
        if not self.file_path.endswith('.wav'):
            self.errors.append(f"File is not a WAV file: {self.file_path}")
        
        # Check audio properties using wave module

        try:
            with wave.open(self.file_path, 'rb') as wav_file:
                sample_rate = wav_file.getframerate()
                channels = wav_file.getnchannels()
                sampwidth = wav_file.getsampwidth()  # in bytes

            # Check sample rate
            if sample_rate != WAV_FILE_SPECIFICATIONS["sample_rate"]:
                self.errors.append(
                f"Sample rate mismatch: {sample_rate} Hz (expected {WAV_FILE_SPECIFICATIONS['sample_rate']} Hz) in {self.file_path}"
                )

            # Check channels
            if channels != WAV_FILE_SPECIFICATIONS["channels"]:
                self.errors.append(
                f"Channel count mismatch: {channels} (expected {WAV_FILE_SPECIFICATIONS['channels']}) in {self.file_path}"
                )

            # Check bit depth
            bit_depth = sampwidth * 8
            if bit_depth != WAV_FILE_SPECIFICATIONS["bit_depth"]:
                self.errors.append(
                f"Bit depth mismatch: {bit_depth} (expected {WAV_FILE_SPECIFICATIONS['bit_depth']}) in {self.file_path}"
                )

            # Check duration
            n_frames = wav_file.getnframes()
            duration = n_frames / float(sample_rate)
            if duration > WAV_FILE_SPECIFICATIONS["max_length"]:
                self.errors.append(
                f"Audio duration exceeds limit: {duration:.2f} seconds (max {WAV_FILE_SPECIFICATIONS['max_length']} seconds) in {self.file_path}"
                )

        except wave.Error as e:
            self.errors.append(f"Error reading WAV file: {self.file_path} ({e})")
        except Exception as e:
            self.errors.append(f"Unexpected error reading WAV file: {self.file_path} ({e})")

        return not self.errors