import { useState, useRef } from "react";

const AudioRecorder = ({ onUpload }:any) => {
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef<any>(null);
  const audioChunksRef = useRef<any[]>([]);

  const handleClick = async () => {
    if (!recording) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorderRef.current = new MediaRecorder(stream);
        audioChunksRef.current = [];

        mediaRecorderRef.current.ondataavailable = (event:any) => {
          if (event.data.size > 0) {
            console.log("Received audio chunk:", event.data.size); // Debugging log
            audioChunksRef.current.push(event.data);
          }
        };

        mediaRecorderRef.current.onstop = async () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
          console.log("Final Blob size:", audioBlob.size);
          const formData = new FormData();
          formData.append("audio", audioBlob, "recording.wav");
          
          if (onUpload) {
            onUpload(formData);
          }
        };

        mediaRecorderRef.current.start();
        setRecording(true);
      } catch (error) {
        console.error("Error accessing microphone: ", error);
      }
    } else {
      mediaRecorderRef.current?.stop();
      setRecording(false);
    }
  };

  return (
    <button onClick={handleClick} className="testModeButton">
      {recording ? "Stop Recording" : "Start Recording"}
    </button>
  );
};

export default AudioRecorder;