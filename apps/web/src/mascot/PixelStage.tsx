"use client";

import { useId } from "react";

export function PixelStage() {
  const id = useId().replace(/:/g, "");
  const n = (name: string) => `${id}-${name}`;

  return (
    <svg
      className="pixel-stage"
      viewBox="0 0 120 80"
      preserveAspectRatio="xMidYMax slice"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id={n("sky")} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#b7ddd0" />
          <stop offset="42%" stopColor="#d4eedf" />
          <stop offset="100%" stopColor="#9ecfb8" />
        </linearGradient>
        <linearGradient id={n("floor")} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#cfe8d8" />
          <stop offset="100%" stopColor="#8fbf9a" />
        </linearGradient>
        <linearGradient id={n("build")} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#6eaa86" />
          <stop offset="100%" stopColor="#3d6f54" />
        </linearGradient>
        <linearGradient id={n("build-dark")} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#4e8664" />
          <stop offset="100%" stopColor="#2a5540" />
        </linearGradient>
        <radialGradient id={n("haze")} cx="50%" cy="28%" r="70%">
          <stop offset="0%" stopColor="#f4fff8" stopOpacity="0.45" />
          <stop offset="100%" stopColor="#f4fff8" stopOpacity="0" />
        </radialGradient>
        <filter id={n("soft")} x="-8%" y="-8%" width="116%" height="116%">
          <feGaussianBlur stdDeviation="0.35" />
        </filter>
      </defs>

      <rect width="120" height="80" fill={`url(#${n("sky")})`} />
      <ellipse cx="60" cy="18" rx="52" ry="16" fill={`url(#${n("haze")})`} />

      <g className="pixel-stage__city">
        <rect x="4" y="34" width="13" height="20" rx="1.6" fill={`url(#${n("build")})`} />
        <rect x="18" y="24" width="11" height="30" rx="1.8" fill={`url(#${n("build-dark")})`} />
        <rect x="31" y="32" width="15" height="22" rx="1.6" fill={`url(#${n("build")})`} />
        <rect x="81" y="30" width="11" height="22" rx="1.6" fill={`url(#${n("build")})`} />
        <rect x="93" y="18" width="17" height="34" rx="2" fill={`url(#${n("build-dark")})`} />
        <rect x="107" y="28" width="9" height="24" rx="1.5" fill={`url(#${n("build")})`} />
        <circle cx="22" cy="31" r="1.1" fill="#7dffb3" opacity="0.85" />
        <circle cx="100" cy="25" r="1.15" fill="#7dffb3" opacity="0.8" />
        <circle cx="37" cy="38" r="1" fill="#c8ffe0" opacity="0.7" />
      </g>

      <g className="pixel-stage__floor">
        <path d="M0 52h120v28H0z" fill={`url(#${n("floor")})`} />
        <path d="M0 52h120l-10 28H10z" fill="#7fb392" opacity="0.18" />
        {Array.from({ length: 8 }, (_, index) => (
          <path
            key={`h-${index}`}
            d={`M0 ${54 + index * 3.2}h120`}
            fill="none"
            stroke="#4e8664"
            strokeWidth="0.35"
            opacity={0.18 - index * 0.012}
          />
        ))}
        {Array.from({ length: 11 }, (_, index) => {
          const t = index / 10;
          const topX = 8 + t * 104;
          const botX = -6 + t * 132;
          return (
            <path
              key={`v-${index}`}
              d={`M${topX} 52 L${botX} 80`}
              fill="none"
              stroke="#4e8664"
              strokeWidth="0.35"
              opacity="0.16"
            />
          );
        })}
      </g>

      <g className="pixel-stage__circuit">
        <path
          d="M8 60h18v7"
          fill="none"
          stroke="#2f8f5c"
          strokeWidth="0.9"
          strokeLinecap="round"
          opacity="0.45"
        />
        <path
          d="M90 64h18"
          fill="none"
          stroke="#2f8f5c"
          strokeWidth="0.9"
          strokeLinecap="round"
          opacity="0.4"
        />
      </g>

      <g className="pixel-stage__terminal">
        <rect x="91" y="41" width="25" height="19" rx="2.4" fill="#07140e" />
        <rect x="93" y="43.2" width="21" height="13.2" rx="1.5" fill="#143528" />
        <rect
          x="95.2"
          y="45.4"
          width="4.2"
          height="2.2"
          rx="0.6"
          className="pixel-stage__term-dot"
          fill="#7dffb3"
        />
        <rect x="101.2" y="45.6" width="10.4" height="1.8" rx="0.6" fill="#2f8f5c" />
        <rect x="95.2" y="49.8" width="16.4" height="1.8" rx="0.6" fill="#1d6a44" />
        <rect x="95.2" y="53.4" width="8.2" height="1.2" rx="0.5" fill="#7dffb3" opacity="0.7" />
      </g>

      <g className="pixel-stage__nodes">
        <circle cx="11.5" cy="19.5" r="1.7" fill="#2f8f5c" opacity="0.55" />
        <circle cx="69.5" cy="15.5" r="1.7" fill="#7dffb3" opacity="0.45" />
        <circle cx="49" cy="11" r="1.2" fill="#4cba7a" opacity="0.4" />
        <circle cx="29" cy="13" r="1.1" fill="#2f8f5c" opacity="0.35" />
      </g>

      <g className="pixel-stage__docs">
        <rect x="6" y="15" width="13" height="15" rx="1.4" fill="#0d2418" />
        <rect x="7.1" y="16.1" width="10.8" height="12.8" rx="1" fill="#f7fff9" />
        <rect x="8.4" y="18.6" width="8.2" height="1.1" rx="0.4" fill="#2f8f5c" />
        <rect x="8.4" y="21.6" width="8.2" height="1.1" rx="0.4" fill="#2f8f5c" />
        <rect x="8.4" y="24.6" width="5.2" height="1.1" rx="0.4" fill="#1d6a44" />
        <rect
          x="16"
          y="19"
          width="13"
          height="15"
          rx="1.4"
          fill="#0d2418"
          className="pixel-stage__doc-best"
        />
        <rect x="17.1" y="20.1" width="10.8" height="12.8" rx="1" fill="#f7fff9" />
        <rect x="18.4" y="22.6" width="8.2" height="1.1" rx="0.4" fill="#7dffb3" />
        <rect x="18.4" y="25.6" width="8.2" height="1.1" rx="0.4" fill="#2f8f5c" />
      </g>

      <g className="pixel-stage__shield">
        <rect x="50" y="7.5" width="18.5" height="16.5" rx="2.2" fill="#0d2418" />
        <rect x="51.2" y="8.7" width="16.1" height="14.1" rx="1.6" fill="#e8fff2" />
        <path
          d="M59.2 11.4c2.6 1.3 3.8 2.8 3.8 5.6 0 2.4-1.7 4.1-3.8 5.2-2.1-1.1-3.8-2.8-3.8-5.2 0-2.8 1.2-4.3 3.8-5.6Z"
          fill="#2f8f5c"
        />
        <path
          d="M59.2 13.2c1.6 0.8 2.3 1.8 2.3 3.6 0 1.5-1 2.6-2.3 3.3-1.3-0.7-2.3-1.8-2.3-3.3 0-1.8 0.7-2.8 2.3-3.6Z"
          fill="#7dffb3"
        />
      </g>

      <g className="pixel-stage__mute">
        <rect x="97.5" y="11.5" width="11.5" height="9" rx="1.6" fill="#f7fff9" />
        <path d="M100.4 14.2h3.2v4.2h-3.2z" fill="#0d2418" />
        <path d="M103.6 13.6 107.2 12.4v7.2L103.6 18.4z" fill="#0d2418" />
        <path d="M99 13.2 108.4 19.6" stroke="#8b1e1e" strokeWidth="1.1" strokeLinecap="round" />
      </g>

      <g className="pixel-stage__cable">
        <path
          d="M14 49.2h16c1.4 0 2.4-1.4 2.4-2.8"
          fill="none"
          stroke="#0d2418"
          strokeWidth="1.8"
          strokeLinecap="round"
        />
        <circle cx="32.4" cy="45.4" r="1.6" fill="#8b1e1e" />
      </g>

      <g className="pixel-stage__spark" filter={`url(#${n("soft")})`}>
        <circle cx="41" cy="21" r="1.3" fill="#7dffb3" />
        <circle cx="47" cy="16.5" r="1.1" fill="#c8ffe0" />
        <circle cx="71" cy="24.5" r="1.2" fill="#4cba7a" />
      </g>

      <g className="pixel-stage__moth">
        <ellipse cx="25.4" cy="18.6" rx="2.2" ry="1.15" fill="#7dffb3" />
        <ellipse cx="23.4" cy="17.6" rx="0.8" ry="0.7" fill="#2f8f5c" />
        <ellipse cx="27.6" cy="17.6" rx="0.8" ry="0.7" fill="#2f8f5c" />
      </g>

      <g className="pixel-stage__sweep">
        <rect x="20" y="29.5" width="6.4" height="6.4" rx="1.4" fill="#f7fff9" opacity="0.85" />
        <rect x="36" y="25.5" width="5.2" height="5.2" rx="1.2" fill="#f7fff9" opacity="0.7" />
        <rect x="54" y="21.5" width="4.2" height="4.2" rx="1" fill="#f7fff9" opacity="0.55" />
      </g>
    </svg>
  );
}
