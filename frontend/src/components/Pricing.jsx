import { useNavigate } from "react-router-dom";

export default function Pricing() {
  const navigate = useNavigate();

  const plans = [
    {
      name: "Starter",
      price: "$0",
      desc: "Perfect for trying out Prompt Resume",
      features: [
        "1 resume generation",
        "Basic templates",
        "PDF export",
        "Email support"
      ],
      cta: "Get started",
      onClick: () => navigate("/register")
    },
    {
      name: "Pro",
      price: "$9",
      period: "/month",
      desc: "For serious job seekers",
      features: [
        "Unlimited generations",
        "All premium templates",
        "ATS optimization",
        "Priority support",
        "Cover letter AI"
      ],
      cta: "Start Pro trial",
      popular: true,
      onClick: () => navigate("/pricing")
    },
    {
      name: "Enterprise",
      price: "$29",
      period: "/month",
      desc: "For teams and recruiters",
      features: [
        "Everything in Pro",
        "Team collaboration",
        "Custom branding",
        "API access",
        "Dedicated support"
      ],
      cta: "Contact sales",
      onClick: () => navigate("/contact")
    }
  ];

  return (
    <section className="pricing-section" id="pricing">
      <div className="pricing-inner">
        <div className="reveal">
          <div className="section-tag">Pricing</div>
          <h2 className="section-headline">Simple, transparent pricing</h2>
          <p className="section-sub centered">No hidden fees. Cancel anytime.</p>
        </div>

        <div className="pricing-grid">
          {plans.map((plan, i) => (
            <div key={i} className={`pricing-card reveal ${plan.popular ? 'popular' : ''}`}>
              {plan.popular && <div className="popular-badge">Most Popular</div>}
              <div className="pricing-plan">{plan.name}</div>
              <div className="pricing-price">
                {plan.price}
                {plan.period && <span className="pricing-price-period">{plan.period}</span>}
              </div>
              <p className="pricing-desc">{plan.desc}</p>
              <div className="pricing-features">
                {plan.features.map((f, fi) => (
                  <div key={fi} className="pricing-feature">
                    <span className="pricing-check">✓</span>
                    {f}
                  </div>
                ))}
              </div>
              <button className={`btn-plan ${plan.popular ? 'primary' : ''}`} onClick={plan.onClick}>{plan.cta}</button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
