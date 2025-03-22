import { useState, useRef } from "react";

const AudioRecorder = ({ onUpload }:any) => {
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef<any>(null);
  const audioChunksRef = useRef<any[]>([]);
  function convertBlobToBase64(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64String = reader.result as string;
        resolve(base64String.split(',')[1]); // Remove the "data:audio/mp3;base64," prefix
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob); // Read the Blob as a base64 data URL
    });
  }
  

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
          const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
          const audioFile = new File([audioBlob], "recording.webm", { type: "audio/webm" });
          
          if (onUpload) {
            onUpload(audioFile);
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