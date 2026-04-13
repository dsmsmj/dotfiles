import { useEffect, useState } from 'react'

type Props = {
  sessionId: string
  images: string[]
  onRefresh: () => void
}

export default function ImageGallery({ sessionId, images, onRefresh }: Props) {
  const [lightbox, setLightbox] = useState<string | null>(null)

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setLightbox(null)
      if (e.key === 'ArrowRight' && lightbox) {
        const i = images.indexOf(lightbox)
        if (i < images.length - 1) setLightbox(images[i + 1])
      }
      if (e.key === 'ArrowLeft' && lightbox) {
        const i = images.indexOf(lightbox)
        if (i > 0) setLightbox(images[i - 1])
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [lightbox, images])

  return (
    <aside className="image-gallery">
      <div className="gallery-header">
        <span className="gallery-title">生成图片</span>
        <span className="gallery-meta">#{sessionId}</span>
        <button className="btn-icon" onClick={onRefresh} title="刷新">
          ↺
        </button>
      </div>

      <div className="gallery-grid">
        {images.length === 0 ? (
          <div className="gallery-empty">
            <span className="gallery-empty-icon">🖼</span>
            <p>运行后图片将显示在这里</p>
          </div>
        ) : (
          images.map((url, idx) => (
            <button
              key={url}
              className="gallery-thumb"
              onClick={() => setLightbox(url)}
              title={`图片 ${idx + 1}`}
            >
              <img
                src={url}
                alt={`生成图片 ${idx + 1}`}
                loading="lazy"
              />
              <span className="gallery-thumb-num">{idx + 1}</span>
            </button>
          ))
        )}
      </div>

      {lightbox && (
        <div
          className="lightbox"
          onClick={() => setLightbox(null)}
          role="dialog"
          aria-modal
        >
          <img
            src={lightbox}
            alt="大图预览"
            onClick={e => e.stopPropagation()}
          />
          <button
            className="lightbox-close"
            onClick={() => setLightbox(null)}
            aria-label="关闭"
          >
            ✕
          </button>
          {images.length > 1 && (
            <div className="lightbox-nav" onClick={e => e.stopPropagation()}>
              <button
                disabled={images.indexOf(lightbox) === 0}
                onClick={() => {
                  const i = images.indexOf(lightbox)
                  if (i > 0) setLightbox(images[i - 1])
                }}
              >
                ‹
              </button>
              <span>{images.indexOf(lightbox) + 1} / {images.length}</span>
              <button
                disabled={images.indexOf(lightbox) === images.length - 1}
                onClick={() => {
                  const i = images.indexOf(lightbox)
                  if (i < images.length - 1) setLightbox(images[i + 1])
                }}
              >
                ›
              </button>
            </div>
          )}
        </div>
      )}
    </aside>
  )
}
