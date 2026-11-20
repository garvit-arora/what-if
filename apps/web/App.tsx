"use client";

import { useState, type ReactNode } from "react";
import { motion } from "motion/react";
import Image from "next/image";
import { Circle, Eye, EyeOff } from "lucide-react";

const parentReveal = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.15, delayChildren: 0.2 } },
};

const childReveal = {
  hidden: { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

export default function App() {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <main className="flex min-h-screen w-full bg-black selection:bg-white/30 p-2 transition-all duration-500 lg:h-screen lg:overflow-hidden lg:p-4">
      <section className="relative hidden h-full w-[52%] flex-col items-center justify-end overflow-hidden rounded-3xl px-12 pb-32 shadow-2xl lg:flex">
        <Image
          src="/login.png"
          alt="Historical leaders surrounding a luminous what-if timeline"
          fill
          priority
          sizes="52vw"
          className="object-cover"
        />

        <motion.div
          variants={parentReveal}
          initial="hidden"
          animate="visible"
          className="relative z-10 w-full max-w-xs space-y-8"
        >
          <motion.div variants={childReveal} className="flex items-center gap-2">
            <Circle className="h-5 w-5 fill-white text-white" />
            <span className="text-xl font-semibold tracking-tight">Aurora</span>
          </motion.div>

          <motion.div variants={childReveal} className="space-y-3 text-center">
            <h1 className="whitespace-nowrap text-4xl font-medium tracking-tight">Join Aurora</h1>
            <p className="px-4 text-sm leading-relaxed text-white/60">
              Follow these 3 quick phases to activate your space.
            </p>
          </motion.div>

          <motion.div variants={childReveal} className="space-y-3">
            <StepItem number={1} text="Register your identity" active />
            <StepItem number={2} text="Configure your studio" />
            <StepItem number={3} text="Finalize your profile" />
          </motion.div>
        </motion.div>
      </section>

      <section className="flex flex-1 flex-col items-center justify-center overflow-y-auto px-4 py-12 sm:px-12 lg:overflow-hidden lg:px-16 lg:py-6 xl:px-24">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="w-full max-w-xl space-y-8 sm:space-y-10 lg:space-y-6"
        >
          <header className="space-y-2">
            <h2 className="text-3xl font-medium tracking-tight">Create New Profile</h2>
            <p className="text-sm text-white/40">Input your basic details to begin the journey.</p>
          </header>

          <div className="grid grid-cols-2 gap-4">
            <SocialButton icon={<GoogleMark />} label="Google" />
            <SocialButton icon={<GithubMark />} label="Github" />
          </div>

          <div className="relative flex items-center">
            <div className="w-full border-t border-white/10" />
            <span className="absolute left-1/2 -translate-x-1/2 bg-black px-4 text-xs font-medium uppercase tracking-widest text-white/40">Or</span>
          </div>

          <form className="space-y-5" onSubmit={(event) => event.preventDefault()}>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <InputGroup label="First Name" placeholder="Alex" type="text" />
              <InputGroup label="Last Name" placeholder="Morgan" type="text" />
            </div>
            <InputGroup label="Email" placeholder="alex@studio.com" type="email" />

            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium text-white">Password</label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Create a secure password"
                  className="h-11 w-full rounded-xl border-none bg-brand-gray px-4 pr-12 text-white outline-none placeholder:text-white/20 focus:ring-2 focus:ring-white/20"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((value) => !value)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-white/40 transition-colors hover:text-white"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              <p className="text-[11px] text-white/30">Requires at least 8 symbols.</p>
            </div>

            <button type="submit" className="mt-4 h-14 w-full rounded-xl bg-white font-semibold text-black transition hover:bg-white/90 active:scale-[0.98]">
              Create Account
            </button>
          </form>

          <p className="text-center text-sm text-white/40">
            Member of the team? <a href="#" className="font-medium text-white transition hover:text-white/70">Log in</a>
          </p>
          <a href="/history" className="block text-center text-xs font-medium uppercase tracking-[0.18em] text-white/35 transition hover:text-white">Explore History Lab →</a>
        </motion.div>
      </section>
    </main>
  );
}

function StepItem({ number, text, active = false }: { number: number; text: string; active?: boolean }) {
  return (
    <div className={`flex h-14 items-center gap-4 rounded-xl px-4 ${active ? "border border-white bg-white text-black" : "border-none bg-brand-gray text-white"}`}>
      <span className={`grid h-7 w-7 shrink-0 place-items-center rounded-full text-xs font-semibold ${active ? "bg-black text-white" : "bg-white/10 text-white/40"}`}>{number}</span>
      <span className="text-sm font-medium">{text}</span>
    </div>
  );
}

function SocialButton({ icon, label }: { icon: ReactNode; label: string }) {
  return <button type="button" className="flex h-12 items-center justify-center gap-3 rounded-xl border border-white/10 bg-black text-sm font-medium transition hover:bg-white/5">{icon}{label}</button>;
}

function InputGroup({ label, placeholder, type }: { label: string; placeholder: string; type: string }) {
  const id = label.toLowerCase().replaceAll(" ", "-");
  return (
    <div className="space-y-2">
      <label htmlFor={id} className="text-sm font-medium text-white">{label}</label>
      <input id={id} type={type} placeholder={placeholder} className="h-11 w-full rounded-xl border-none bg-brand-gray px-4 text-white outline-none placeholder:text-white/20 focus:ring-2 focus:ring-white/20" />
    </div>
  );
}

function GoogleMark() {
  return <svg className="h-5 w-5" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M21.6 12.23c0-.71-.06-1.4-.18-2.07H12v3.92h5.38a4.6 4.6 0 0 1-2 3.02v2.55h3.24c1.9-1.75 2.98-4.33 2.98-7.42Z"/><path fill="currentColor" opacity=".75" d="M12 22c2.7 0 4.98-.9 6.64-2.43l-3.24-2.55c-.9.6-2.05.96-3.4.96-2.61 0-4.82-1.77-5.61-4.14H3.04v2.62A10 10 0 0 0 12 22Z"/><path fill="currentColor" opacity=".5" d="M6.39 13.84A6 6 0 0 1 6.07 12c0-.64.11-1.26.32-1.84V7.54H3.04A10 10 0 0 0 2 12c0 1.61.38 3.14 1.04 4.46l3.35-2.62Z"/><path fill="currentColor" opacity=".9" d="M12 6.02c1.47 0 2.79.51 3.82 1.5l2.87-2.87A9.64 9.64 0 0 0 12 2a10 10 0 0 0-8.96 5.54l3.35 2.62C7.18 7.79 9.39 6.02 12 6.02Z"/></svg>;
}

function GithubMark() {
  return <svg className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-3.16 19.49c.5.09.68-.22.68-.48v-1.69c-2.78.61-3.37-1.18-3.37-1.18-.45-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.61.07-.61 1 .07 1.53 1.03 1.53 1.03.9 1.53 2.35 1.09 2.92.83.09-.65.35-1.09.64-1.34-2.22-.25-4.56-1.11-4.56-4.94 0-1.09.39-1.98 1.03-2.68-.1-.25-.45-1.27.1-2.64 0 0 .84-.27 2.75 1.02A9.57 9.57 0 0 1 12 7.01c.85 0 1.71.11 2.51.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.37.2 2.39.1 2.64.64.7 1.03 1.59 1.03 2.68 0 3.84-2.34 4.68-4.57 4.93.36.31.68.92.68 1.86v2.58c0 .27.18.58.69.48A10 10 0 0 0 12 2Z"/></svg>;
}
