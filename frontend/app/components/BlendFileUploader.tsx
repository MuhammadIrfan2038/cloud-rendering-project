"use client";

import { useEffect, useState } from "react";
import { AlertCircleIcon, ImageUpIcon, XIcon } from "lucide-react";
import axios from "axios";

interface Props {
  onFileSelected: (file: File | null) => void;
  onUploadFinished: (projectName: string) => void;
  resetState?: boolean;
}

export default function BlendFileUploader({ onFileSelected, onUploadFinished, resetState }: Props) {
  const [fileName, setFileName] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const maxSizeMB = 100;
  const maxSizeBytes = maxSizeMB * 1024 * 1024;

  useEffect(() => {
    if (resetState) {
      setFileName(null);
      setErrorMessage(null);
      setIsUploading(false);
    }
  }, [resetState]);

  const handleFile = async (file: File) => {
    if (!file.name.endsWith(".blend")) {
      setErrorMessage("Hanya file .blend yang didukung.");
      return;
    }
    if (file.size > maxSizeBytes) {
      setErrorMessage(`Ukuran file melebihi ${maxSizeMB}MB`);
      return;
    }

    // Valid file, lanjutkan
    setErrorMessage(null);
    setFileName(file.name);
    setIsUploading(true);
    onFileSelected(file); // Inform parent bahwa file dipilih

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/render`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const projectName = response.data.project_name;
      console.log("Render sukses:", projectName);

      // Inform parent bahwa upload selesai
      onUploadFinished(projectName);
    } catch (error) {
      console.error("Gagal render:", error);
      setErrorMessage("Gagal merender file.");
    } finally {
      setIsUploading(false);
    }
  };

  if (isUploading) return null; // Sembunyikan uploader saat upload berlangsung

  return (
    <div
      role="button"
      onClick={() => document.getElementById("blend-input")?.click()}
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => {
        e.preventDefault();
        const dropped = e.dataTransfer.files[0];
        if (dropped) handleFile(dropped);
      }}
      className="border-input hover:bg-accent/50 relative flex min-h-40 flex-col items-center justify-center overflow-hidden rounded-xl border border-dashed p-4 transition-colors bg-gray-50 cursor-pointer"
    >
      <input
        type="file"
        id="blend-input"
        accept=".blend"
        className="hidden"
        onChange={(e) => {
          const selected = e.target.files?.[0];
          if (selected) handleFile(selected);
        }}
      />

      {!fileName ? (
        <div className="flex flex-col items-center justify-center px-4 py-3 text-center">
          <div className="bg-white mb-2 flex size-11 shrink-0 items-center justify-center rounded-full border">
            <ImageUpIcon className="size-4 opacity-60" />
          </div>
          <p className="mt-4 text-sm font-medium">
            Drop file <strong>.blend</strong> di sini atau klik untuk unggah
          </p>
          {/* <p className="text-muted-foreground text-xs">
            Maksimum {maxSizeMB}MB
          </p> */}
        </div>
      ) : (
        <div className="text-sm font-medium text-gray-700 flex items-center justify-center gap-2">
          <span>{fileName}</span>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setFileName(null);
              setErrorMessage(null);
              onFileSelected(null);
            }}
          >
            <XIcon className="w-4 h-4 text-red-500" />
          </button>
        </div>
      )}

      {errorMessage && (
        <p className="text-sm text-red-600 mt-2 flex items-center justify-center gap-1">
          <AlertCircleIcon className="w-4 h-4" /> {errorMessage}
        </p>
      )}
    </div>
  );
}
