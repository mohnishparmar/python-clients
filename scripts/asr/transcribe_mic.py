# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#  * Neither the name of NVIDIA CORPORATION nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import argparse
import sys

import riva_api
from riva_api.script_utils import add_asr_config_argparse_parameters, add_connection_argparse_parameters


RATE = 16000
CHUNK = int(RATE / 10)  # 100ms


# TODO: add word boosting
def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Streaming transcription via Riva AI Services")
    parser.add_argument("--input-device", type=int, default=None, help="output device to use")
    parser.add_argument("--list-devices", action="store_true", help="list input devices indices")
    parser = add_asr_config_argparse_parameters(parser)
    parser = add_connection_argparse_parameters(parser)
    parser.add_argument(
        "--audio-frame-rate", type=int, help="Frame for input device. If not provided, then default value is used."
    )
    parser.add_argument("--file-streaming-chunk", type=int, default=1600)
    args = parser.parse_args()
    if args.audio_frame_rate is None:
        args.audio_frame_rate = riva_api.get_audio_device_info(args.input_device)['defaultSampleRate']
    return args


def main():
    args = get_args()

    if args.list_devices:
        riva_api.list_input_devices()
        sys.exit(0)

    auth = riva_api.Auth(args.ssl_cert, args.use_ssl, args.riva_uri)
    asr_client = riva_api.ASRClient(auth)
    config = riva_api.StreamingRecognitionConfig(
        config=riva_api.RecognitionConfig(
            encoding=riva_api.AudioEncoding.LINEAR_PCM,
            language_code=args.language_code,
            max_alternatives=1,
            enable_automatic_punctuation=args.automatic_punctuation,
            verbatim_transcripts=not args.no_verbatim_transcripts,
        ),
        interim_results=True,
    )
    riva_api.print_streaming(
        generator=asr_client.streaming_recognize_microphone_generator(
            args.input_device,
            streaming_config=config,
            file_streaming_chunk=args.file_streaming_chunk,
            audio_frame_rate=args.audio_frame_rate,
        ),
        show_intermediate=True,
    )


if __name__ == '__main__':
    main()
