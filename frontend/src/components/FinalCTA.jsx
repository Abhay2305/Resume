export default function FinalCTA({ onBuildResume }) {
  return (
    <section className="final-cta">
      <div className="cta-bg-circle" style={{ width: 400, height: 400, top: -100, left: -100 }} />
      <div className="cta-bg-circle" style={{ width: 300, height: 300, bottom: -80, right: -80 }} />
      <div className="cta-bg-circle" style={{ width: 200, height: 200, top: '50%', left: '60%' }} />
      
      <div className="final-cta-inner reveal">
        <h2 className="final-cta-headline">Ready to build your dream resume?</h2>
        <p className="final-cta-sub">Join 10,000+ professionals who've landed their dream jobs with Prompt Resume. Start for free — no credit card required.</p>
        <div className="final-cta-btns">
          <button className="btn-cta-white" onClick={onBuildResume}>
            Build my resume free →
          </button>
          <button className="btn-cta-outline" onClick={() => document.getElementById('templates')?.scrollIntoView({ behavior: 'smooth' })}>
            View templates
          </button>
        </div>
        <p className="final-cta-note">Free forever plan available · No credit card needed</p>
      </div>
    </section>
  );
}
