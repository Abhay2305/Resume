const PRICING_PLANS = [
  {
    plan: "Free",
    price: "0",
    desc: "Perfect for getting started",
    features: [
      "2 resumes",
      "5 templates",
      "PDF export",
      "Basic ATS score",
      "Manual mode"
    ],
    cta: "Start free",
    popular: false,
  },
  {
    plan: "Pro",
    price: "9",
    desc: "For serious job seekers",
    features: [
      "Unlimited resumes",
      "All 24 templates",
      "AI resume mode",
      "Advanced ATS analysis",
      "PDF + DOCX export",
      "Priority support"
    ],
    cta: "Start Pro",
    popular: true,
  },
  {
    plan: "Team",
    price: "29",
    desc: "For career coaches & teams",
    features: [
      "Everything in Pro",
      "Up to 10 seats",
      "Shared template library",
      "Bulk export",
      "Analytics dashboard",
      "Custom branding"
    ],
    cta: "Contact us",
    popular: false,
  },
];

export default function Pricing() {
  return (
    <div className="pricing-section" id="pricing">
      <div className="pricing-inner">
        <div className="section-tag reveal" style={{ display: "inline-flex" }}>
          ◧ Pricing
        </div>
        <h2 className="section-headline reveal delay-1">
          Simple, transparent pricing
        </h2>
        <p className="section-sub centered reveal delay-2">
          Start free. Upgrade when you're ready. No hidden fees, no surprise charges.
        </p>
        
        <div className="pricing-grid">
          {PRICING_PLANS.map((p, i) => (
            <div className={`pricing-card${p.popular ? " popular" : ""} reveal delay-${i + 2}`} key={i}>
              {p.popular && <div className="popular-badge">Most Popular</div>}
              
              <div className="pricing-plan">{p.plan}</div>
              <div className="pricing-price">
                <span className="pricing-price-currency">$</span>
                {p.price}
                <span className="pricing-price-period">/mo</span>
              </div>
              <p className="pricing-desc">{p.desc}</p>
              
              <div className="pricing-features">
                {p.features.map((f, j) => (
                  <div className="pricing-feature" key={j}>
                    <div className="pricing-check">✓</div>
                    {f}
                  </div>
                ))}
              </div>
              
              <button className={`btn-plan${p.popular ? " primary" : ""}`}>
                {p.cta}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}