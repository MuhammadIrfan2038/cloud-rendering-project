"use client";

import { useEffect, useState } from "react";
import BlendFileUploader from "@/components/BlendFileUploader";
import { DownloadIcon } from "lucide-react";

export default function HomePage() {
  const [projectName, setProjectName] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [currentFrame, setCurrentFrame] = useState<number | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [isRendering, setIsRendering] = useState<boolean>(false);
  const [uploadFinished, setUploadFinished] = useState(false);
  const [file, setFile] = useState<File | null>(null);

  useEffect(() => {
    const cleanupZip = async () => {
      try {
        const res = await fetch("http://localhost:8000/cleanup_zip", {
          method: "POST",
        });
        const result = await res.json();
        console.log("[DEBUG] ZIP cleanup:", result);
      } catch (error) {
        console.error("Gagal membersihkan ZIP:", error);
      }
    };

    cleanupZip(); // dijalankan saat pertama kali halaman dibuka
  }, []);

  useEffect(() => {
    if (!projectName) return;

    const intervalId = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8000/render/progress/${projectName}`);
        if (res.ok) {
          const data = await res.json();
          console.log("[DEBUG] data progress:", data);

          setStatus(data.status);
          setCurrentFrame(data.current_frame);

          if (data.status === "done") {
            setDownloadUrl(`http://localhost:8000/download/${data.project_name}`);
            clearInterval(intervalId);
            setIsRendering(false);
          }
        }
      } catch (err) {
        console.error("Gagal mengambil progres:", err);
      }
    }, 1000);

    return () => clearInterval(intervalId);
  }, [projectName]);

    const resetState = () => {
    setFile(null);
    setProjectName(null);
    setStatus(null);
    setCurrentFrame(null);
    setDownloadUrl(null);
    setUploadFinished(false);
    setIsRendering(false);
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gray-100 px-4">
      <h1 className="text-2xl font-bold mb-4 text-gray-800">3D Cloud Renderer</h1>
      <div className="bg-white shadow-xl rounded-2xl p-8 w-full max-w-md text-center">

        {!projectName && (
          <BlendFileUploader
            onFileSelected={(file) => {
              if (!file) return;
              resetState();
              setIsRendering(true);
            }}
            onUploadFinished={(projectName) => {
              setProjectName(projectName);      // simpan nama project
              setUploadFinished(true);          // proses render dimulai
            }}
          />
        )}

        {isRendering && (
          <div className="flex flex-col items-center justify-center mt-6">
            <div
              className="h-8 w-8 animate-spin rounded-full border-4 border-solid border-neutral-800 border-e-transparent mb-3"
              role="status"
            >
              <span className="sr-only">Loading...</span>
            </div>
            <p className="text-gray-700 font-medium text-sm">
              {uploadFinished ? "Render On Progress..." : "Uploading..."}
            </p>
          </div>
        )}

        {status && (
          <div className="">
            <p className="text-2xl font-bold text-neutral-900 mb-6">{status === "done" ? "Render Complete" : ""}</p>
            <p className="text-m text-gray-800 mb-2">
              {status !== "done" && currentFrame !== null
                ? `Rendering Frame ${currentFrame}`
                : status === "done"
                ? "Your file is ready"
                : ""}
            </p>

        {status === "done" && downloadUrl && (
          <div className="mt-4 flex flex-col sm:flex-row items-center justify-center gap-4">
            <a
              href={downloadUrl}
              className="flex items-center gap-2 bg-neutral-200 text-black px-4 py-2 rounded-xl hover:bg-neutral-400 transition"
              download
            >
              <DownloadIcon className="w-4 h-4" />
              Download
            </a>

            <button
              onClick={resetState}
              className="bg-neutral-200 text-black px-4 py-2 rounded-xl hover:bg-neutral-400 transition"
            >
              Upload Another
            </button>
          </div>
        )}
          </div>
        )}
      </div>
    </main>
  );
}
