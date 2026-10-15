import sounddevice as sd
import numpy as np
import whisper
from scipy.io.wavfile import write

SAMPLE_RATE = 16000
MODEL_NAME = "medium"

def main():
    print("Loading Whisper model...")
    model = whisper.load_model(MODEL_NAME)

    print("\nReady to record!")
    input("Press ENTER to start speaking...")

    audio_chunks = []

    def callback(indata, frames, time, status):
        if status:
            print(status)
        audio_chunks.append(indata.copy())

    print("Recording... Speak now.")
    print("Press ENTER again when you finish.")

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            callback=callback,
        ):
            input()
    except KeyboardInterrupt:
        print("\nRecording interrupted.")

    if not audio_chunks:
        print("No audio recorded.")
        return

    audio = np.concatenate(audio_chunks, axis=0).flatten()

    # Save the recording as a WAV file
    write("recording.wav", SAMPLE_RATE,
          (audio * 32767).astype(np.int16))

    print("Transcribing your speech...")
    result = model.transcribe("recording.wav")

    print("\nYou said:")
    print(result["text"])

    with open("transcription.txt", "w", encoding="utf-8") as f:
        f.write(result["text"].strip())

    print("\nSaved transcript to transcription.txt")

if __name__ == "__main__":
    main()