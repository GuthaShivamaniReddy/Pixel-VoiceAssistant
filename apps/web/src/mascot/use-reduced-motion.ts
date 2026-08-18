"use client";

import { useEffect, useState } from "react";

export function usePrefersReducedMotion(): boolean {
  const [reduced, setReduced] = useState(false);

  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    const onChange = () => setReduced(media.matches);
    media.addEventListener("change", onChange);
    const timer = window.setTimeout(onChange, 0);
    return () => {
      window.clearTimeout(timer);
      media.removeEventListener("change", onChange);
    };
  }, []);

  return reduced;
}
