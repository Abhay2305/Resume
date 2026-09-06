export default function Testimonials() {
  const testimonials = [
    {
      stars: "★★★★★",
      quote: "\"I was skeptical at first, but Prompt Resume generated a better resume in 2 minutes than I'd created in 2 hours. The ATS score feature gave me confidence before applying.\"",
      name: "Sarah Mitchell",
      role: "Product Manager, Google",
      color: "#7BC4BE"
    },
    {
      stars: "★★★★★",
      quote: "\"As a recruiter, I see hundreds of resumes daily. The ones made with Prompt Resume consistently stand out. Clean formatting, relevant keywords, and professional structure.\"",
      name: "James Chen",
      role: "Senior Recruiter, Meta",
      color: "#F6B233"
    },
    {
      stars: "★★★★★",
      quote: "\"Switched from my old resume builder and the difference is night and day. The AI actually understands context and tailors content to my industry. Got 3 interview calls in a week.\"",
      name: "Maria Rodriguez",
      role: "Software Engineer, Stripe",
      color: "#4A9E98"
    }
  ];

  return (
    <section className="testimonials-section" id="testimonials">
      <div className="testimonials-inner">
        <div className="reveal">
          <div className="section-tag section-tag-amber">Testimonials</div>
          <h2 className="section-headline" style={{ maxWidth: 540 }}>Loved by professionals worldwide</h2>
          <p className="section-sub">Join thousands who've transformed their job search with AI-powered resumes.</p>
        </div>

        <div className="testimonials-grid">
          {testimonials.map((t, i) => (
            <div key={i} className="testimonial-card reveal">
              <div className="testimonial-stars">{t.stars}</div>
              <p className="testimonial-quote">{t.quote}</p>
              <div className="testimonial-author">
                <div className="testimonial-avatar" style={{ background: `${t.color}22`, color: t.color }}>
                  {t.name.charAt(0)}
                </div>
                <div>
                  <div className="testimonial-name">{t.name}</div>
                  <div className="testimonial-role">{t.role}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
