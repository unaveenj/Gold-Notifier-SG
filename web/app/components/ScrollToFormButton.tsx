'use client'

export default function ScrollToFormButton() {
  const handleClick = () => {
    document.getElementById('subscribe')?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <button className="btn-gold-outline" onClick={handleClick}>
      Subscribe Free
    </button>
  )
}
