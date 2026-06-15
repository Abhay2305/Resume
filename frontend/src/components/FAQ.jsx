import { useState } from "react";

const FAQS = [
  { q: "What makes this different from other resume builders?", a: "We combine AI-powered generation with a fully manual mode..." },
  { q: "How does the AI resume mode work?", a: "You describe your background in natural language..." },
  // Add the rest of your FAQs here...
];

function FAQItem({ q, a }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="faq-item">
      <button className="faq-question" onClick={() => setOpen(!open)}>
        {q}
        <span className={`faq-icon${open ? " open" : ""}`}>+</span>
      </button>
      <div className={`faq-answer${open ? " open" : ""}`}>{a}</div>
    </div>
  );
}

export default function FAQ() {
  return (
    <div className="faq-section">
      <div className="faq-inner">
        <div className="text-centered">
          <div className="section-tag reveal" style={{ display: "inline-flex" }}>? FAQ</div>
          <h2 className="section-headline reveal delay-1">Common questions</h2>
        </div>
        <div className="faq-list">
          {FAQS.map((f, i) => (
            <div className={`reveal delay-${i + 2}`} key={i}>
              <FAQItem q={f.q} a={f.a} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}