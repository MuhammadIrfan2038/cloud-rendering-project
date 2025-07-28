'use client'

import React, { useEffect, useState } from 'react'

interface RenderData {
  id: number
  filename: string
  frame_start: number
  frame_end: number
  output_format: string
  output_dir: string
  status: string
  rendered_at: string
}

const RenderHistoryTable = () => {
  const [data, setData] = useState<RenderData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('http://localhost:8000/render-history')
        const json = await res.json()
        setData(json)
      } catch (error) {
        console.error('Gagal fetch:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) return <p>Loading riwayat render...</p>

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">Riwayat Hasil Render</h2>
      <table className="table-auto border-collapse w-full">
        <thead>
          <tr className="bg-gray-200">
            <th className="border px-4 py-2">#</th>
            <th className="border px-4 py-2">Filename</th>
            <th className="border px-4 py-2">Frame</th>
            <th className="border px-4 py-2">Format</th>
            <th className="border px-4 py-2">Status</th>
            <th className="border px-4 py-2">Tanggal Render</th>
            <th className="border px-4 py-2">Download</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item, i) => (
            <tr key={item.id} className="text-center">
              <td className="border px-4 py-2">{i + 1}</td>
              <td className="border px-4 py-2">{item.filename}</td>
              <td className="border px-4 py-2">
                {item.frame_start} - {item.frame_end}
              </td>
              <td className="border px-4 py-2">{item.output_format}</td>
              <td className="border px-4 py-2">{item.status}</td>
              <td className="border px-4 py-2">{new Date(item.rendered_at).toLocaleString()}</td>
              <td className="border px-4 py-2">
                <a
                    href={`http://localhost:8000/download-zip/${item.id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    download
                >
                    <button>Download</button>
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default RenderHistoryTable
