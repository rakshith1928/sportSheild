import Link from 'next/link'
import { ArrowRight, Shield, Globe, Zap, CheckCircle2 } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans">
      {/* Header */}
      <header className="flex items-center justify-between px-8 py-6 max-w-7xl w-full mx-auto">
        <div className="flex items-center gap-2">
          <Shield className="w-8 h-8 text-primary" />
          <span className="text-xl font-bold tracking-tight">SportShield AI</span>
        </div>
        <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-muted-foreground">
          <Link href="#solutions" className="hover:text-foreground transition-colors">Solutions</Link>
          <Link href="#technology" className="hover:text-foreground transition-colors">Technology</Link>
          <Link href="#compliance" className="hover:text-foreground transition-colors">Compliance</Link>
        </nav>
        <div className="flex items-center gap-4">
          <Link href="/login" className="text-sm font-medium hover:text-primary transition-colors">
            Log in
          </Link>
          <Link 
            href="/signup" 
            className="text-sm font-medium px-4 py-2 rounded-md border border-border hover:bg-card transition-colors"
          >
            Sign up
          </Link>
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center">
        {/* Hero Section */}
        <section className="w-full max-w-5xl mx-auto px-6 py-24 md:py-32 flex flex-col items-center text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium mb-8">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
            </span>
            Active Monitoring Online
          </div>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 leading-tight">
            Securing the Future of <br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">
              Global Sports Rights
            </span>
          </h1>
          <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mb-10 leading-relaxed">
            Combat piracy and protect your digital assets with autonomous AI fingerprinting 
            and real-time automated takedown protocols.
          </p>
          <div className="flex flex-col sm:flex-row items-center gap-4">
            <Link 
              href="/dashboard" 
              className="flex items-center gap-2 bg-primary text-primary-foreground px-8 py-4 rounded-md font-medium text-lg hover:bg-primary/90 transition-all shadow-[0_0_20px_rgba(255,107,107,0.3)] hover:shadow-[0_0_30px_rgba(255,107,107,0.5)]"
            >
              Enter Command Center <ArrowRight className="w-5 h-5" />
            </Link>
            <Link 
              href="#contact" 
              className="px-8 py-4 rounded-md font-medium text-lg border border-border hover:bg-card transition-colors"
            >
              View Documentation
            </Link>
          </div>
        </section>

        {/* Stats Section */}
        <section className="w-full border-y border-border bg-card/50">
          <div className="max-w-7xl mx-auto px-6 py-12">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 divide-x divide-border/50">
              <div className="flex flex-col items-center text-center">
                <span className="text-4xl font-bold text-primary mb-2">99.8%</span>
                <span className="text-sm font-medium text-muted-foreground">Detection Rate</span>
              </div>
              <div className="flex flex-col items-center text-center">
                <span className="text-4xl font-bold text-foreground mb-2">12s</span>
                <span className="text-sm font-medium text-muted-foreground">Avg Response Time</span>
              </div>
              <div className="flex flex-col items-center text-center">
                <span className="text-4xl font-bold text-foreground mb-2">4M+</span>
                <span className="text-sm font-medium text-muted-foreground">Daily Scans</span>
              </div>
              <div className="flex flex-col items-center text-center">
                <span className="text-4xl font-bold text-foreground mb-2">$2B+</span>
                <span className="text-sm font-medium text-muted-foreground">Revenue Protected</span>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="w-full max-w-7xl mx-auto px-6 py-24" id="solutions">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Command Center Capabilities</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Integrated security tools built for the modern digital rights landscape.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-card border border-border p-8 rounded-xl hover:border-primary/50 transition-colors group">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Shield className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold mb-3">AI Fingerprinting</h3>
              <p className="text-muted-foreground leading-relaxed">
                Inject invisible, forensic watermarks into every stream to trace leaks back to the precise subscriber source within seconds.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-card border border-border p-8 rounded-xl hover:border-primary/50 transition-colors group">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Globe className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold mb-3">Global Web Scanning</h3>
              <p className="text-muted-foreground leading-relaxed">
                Autonomous spiders scan indexed sites, social media, and pirate IPTV networks 24/7 to identify illegal re-broadcasts.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-card border border-border p-8 rounded-xl hover:border-primary/50 transition-colors group">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Zap className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold mb-3">Automated Takedowns</h3>
              <p className="text-muted-foreground leading-relaxed">
                Instantly trigger DMCA notices and ISP block requests. AI-driven legal protocols resolve threats without human intervention.
              </p>
            </div>
          </div>
        </section>

        {/* Visual Control Highlight */}
        <section className="w-full max-w-7xl mx-auto px-6 py-12 mb-24 flex flex-col md:flex-row items-center gap-12">
          <div className="flex-1">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">Total Visual Control</h2>
            <p className="text-lg text-muted-foreground mb-8">
              Manage your entire IP portfolio from a single, unified command center designed for rapid decision-making.
            </p>
            <ul className="space-y-4">
              <li className="flex items-center gap-3">
                <CheckCircle2 className="w-6 h-6 text-success" />
                <span className="font-medium">Real-time heatmaps of pirate activity</span>
              </li>
              <li className="flex items-center gap-3">
                <CheckCircle2 className="w-6 h-6 text-success" />
                <span className="font-medium">One-click legal escalation</span>
              </li>
              <li className="flex items-center gap-3">
                <CheckCircle2 className="w-6 h-6 text-success" />
                <span className="font-medium">Comprehensive audit trails for litigation</span>
              </li>
            </ul>
          </div>
          <div className="flex-1 w-full bg-card border border-border rounded-xl p-8 relative overflow-hidden h-[400px] flex items-center justify-center shadow-lg">
             {/* Abstract Dashboard representation since we don't have the image file */}
             <div className="absolute inset-0 opacity-10 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-primary via-background to-background"></div>
             <Shield className="w-32 h-32 text-primary opacity-20 absolute" />
             <div className="relative z-10 text-center">
                <div className="text-2xl font-bold text-muted-foreground mb-2">Live Telemetry</div>
                <div className="flex gap-2 justify-center mt-4">
                  <div className="w-2 h-16 bg-primary rounded-full animate-pulse"></div>
                  <div className="w-2 h-24 bg-success rounded-full animate-pulse delay-75"></div>
                  <div className="w-2 h-12 bg-primary rounded-full animate-pulse delay-150"></div>
                  <div className="w-2 h-32 bg-accent rounded-full animate-pulse delay-300"></div>
                  <div className="w-2 h-20 bg-success rounded-full animate-pulse delay-500"></div>
                </div>
             </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-border py-8 text-center text-sm text-muted-foreground">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4">
          <p>© 2026 SportShield AI. Secure Intelligence for Global Sports.</p>
          <div className="flex gap-6">
            <Link href="#" className="hover:text-foreground">Privacy Policy</Link>
            <Link href="#" className="hover:text-foreground">Terms of Service</Link>
            <Link href="#" className="hover:text-foreground">Security</Link>
          </div>
        </div>
      </footer>
    </div>
  )
}
