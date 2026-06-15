const TESTIMONIALS = [
  {
    stars: 5, avatar: "AK", bg: "rgba(123,196,190,0.18)", text: "#2D7A74",
    quote: "Uploaded my experience as a prompt and had a polished, ATS-ready resume in under two minutes.",
    name: "Arjun K.", role: "Software Engineer, Fresher"
  },
  {
    stars: 5, avatar: "SC", bg: "rgba(246,178,51,0.15)", text: "#8A5A00",
    quote: "The manual mode gives me total control while the AI suggestions keep everything sharp.",
    name: "Sophia C.", role: "Senior Product Manager"
  },
  // Add the rest of your testimonials here...
];

export default function Testimonials() {
  return (
    <div className="testimonials-section">
      <div className="testimonials-inner">
        <div className="text-centered">
          <div className="section-tag reveal" style={{ display: "inline-flex" }}>◈ Testimonials</div>
          <h2 className="section-headline reveal delay-1">Trusted by job seekers<br />across every industry</h2>
        </div>
        <div className="testimonials-grid">
          {TESTIMONIALS.map((t, i) => (
            <div className={`testimonial-card reveal delay-${i + 2}`} key={i}>
              <div className="testimonial-stars">{"★".repeat(t.stars)}</div>
              <p className="testimonial-quote">"{t.quote}"</p>
              <div className="testimonial-author">
                <div className="testimonial-avatar" style={{ background: t.bg, color: t.text }}>{t.avatar}</div>
                <div>
                  <div className="testimonial-name">{t.name}</div>
                  <div className="testimonial-role">{t.role}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}