"use client"

import React from 'react'

interface PaginationControlsProps {
  currentPage: number
  totalItems: number
  pageSize?: number
  onPageChange: (newPage: number) => void
}

export function PaginationControls({
  currentPage,
  totalItems,
  pageSize = 50,
  onPageChange,
}: PaginationControlsProps) {
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize))

  if (totalItems <= pageSize) {
    return null
  }

  const startItem = totalItems === 0 ? 0 : (currentPage - 1) * pageSize + 1
  const endItem = Math.min(currentPage * pageSize, totalItems)

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-4 py-4 px-2 text-sm text-gray-400 border-t border-gray-800">
      <div>
        Showing <span className="font-semibold text-white">{startItem}</span> to{" "}
        <span className="font-semibold text-white">{endItem}</span> of{" "}
        <span className="font-semibold text-white">{totalItems}</span> results
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage <= 1}
          className="px-3 py-1.5 rounded-lg border border-gray-800 bg-[#161a1d] text-gray-300 hover:bg-gray-800 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed transition"
        >
          &larr; Previous
        </button>

        <span className="px-3 py-1.5 rounded-lg bg-[#111415] border border-gray-800 text-gray-200 font-medium">
          Page {currentPage} of {totalPages}
        </span>

        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage >= totalPages}
          className="px-3 py-1.5 rounded-lg border border-gray-800 bg-[#161a1d] text-gray-300 hover:bg-gray-800 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed transition"
        >
          Next &rarr;
        </button>
      </div>
    </div>
  )
}
