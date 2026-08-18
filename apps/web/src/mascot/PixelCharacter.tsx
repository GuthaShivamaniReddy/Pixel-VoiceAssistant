"use client";

import { createContext, useContext, useId, type ReactNode } from "react";

const Paint = createContext("");

function usePaint() {
  const id = useContext(Paint);
  return (name: string) => `url(#${id}-${name})`;
}

function Face({ name, children }: { name: string; children: ReactNode }) {
  return <g className={`pixel-face pixel-face--${name}`}>{children}</g>;
}

function PixelAntennas() {
  const paint = usePaint();
  return (
    <>
      <g className="pixel-char__antenna pixel-char__antenna--left">
        <rect x="21.4" y="8" width="2.4" height="9" rx="1.2" fill={paint("metal")} />
        <circle cx="22.6" cy="6.2" r="3.1" fill="#143528" />
        <circle cx="22.6" cy="6.2" r="2.2" fill={paint("orb")} />
        <circle cx="21.8" cy="5.4" r="0.7" fill="#f4fff8" opacity="0.72" />
        <g className="pixel-char__signal pixel-char__signal--left">
          <path
            d="M16.5 5.2c1.8-1.6 4.2-1.6 6 0"
            fill="none"
            stroke="#7dffb3"
            strokeWidth="0.7"
            strokeLinecap="round"
            opacity="0.85"
          />
          <path
            d="M15.2 3.2c2.8-2.4 6.8-2.4 9.6 0"
            fill="none"
            stroke="#3aa56c"
            strokeWidth="0.55"
            strokeLinecap="round"
            opacity="0.55"
          />
        </g>
      </g>
      <g className="pixel-char__antenna pixel-char__antenna--right">
        <rect x="40.2" y="8" width="2.4" height="9" rx="1.2" fill={paint("metal")} />
        <circle cx="41.4" cy="6.2" r="3.1" fill="#143528" />
        <circle cx="41.4" cy="6.2" r="2.2" fill={paint("orb")} />
        <circle cx="40.6" cy="5.4" r="0.7" fill="#f4fff8" opacity="0.72" />
        <g className="pixel-char__signal pixel-char__signal--right">
          <path
            d="M41.5 5.2c1.8-1.6 4.2-1.6 6 0"
            fill="none"
            stroke="#7dffb3"
            strokeWidth="0.7"
            strokeLinecap="round"
            opacity="0.85"
          />
        </g>
      </g>
    </>
  );
}

function PixelHead() {
  const paint = usePaint();
  return (
    <g className="pixel-char__head">
      <PixelAntennas />
      <rect x="10" y="20.5" width="5.2" height="11" rx="2.2" fill={paint("metal")} />
      <rect x="48.8" y="20.5" width="5.2" height="11" rx="2.2" fill={paint("metal")} />
      <rect x="11.2" y="21.6" width="3" height="8.6" rx="1.4" fill="#1f8a5a" opacity="0.45" />
      <rect x="49.8" y="21.6" width="3" height="8.6" rx="1.4" fill="#1f8a5a" opacity="0.45" />
      <rect x="14.2" y="11.2" width="35.6" height="32.4" rx="6.4" fill="#07140e" />
      <rect x="15.4" y="12.4" width="33.2" height="30" rx="5.4" fill={paint("casing")} />
      <rect x="16.2" y="13.2" width="14" height="8" rx="3" fill="#ffffff" opacity="0.12" />
      <rect x="17.4" y="14.6" width="29.2" height="25.4" rx="3.6" fill={paint("bezel")} />
      <rect
        x="19.4"
        y="16.8"
        width="25.2"
        height="20.6"
        rx="2.6"
        fill="#06150f"
        className="pixel-char__screen"
      />
      <rect
        x="19.4"
        y="16.8"
        width="25.2"
        height="20.6"
        rx="2.6"
        fill={paint("screen")}
        className="pixel-char__screen"
        opacity="0.92"
      />
      <g opacity="0.16">
        <rect x="19.4" y="20.2" width="25.2" height="0.55" fill="#7dffb3" />
        <rect x="19.4" y="24.4" width="25.2" height="0.55" fill="#7dffb3" />
        <rect x="19.4" y="28.6" width="25.2" height="0.55" fill="#7dffb3" />
        <rect x="19.4" y="32.8" width="25.2" height="0.55" fill="#7dffb3" />
      </g>
      <rect x="20.2" y="17.6" width="11" height="4.2" rx="1.6" fill="#f4fff8" opacity="0.14" />
      <circle cx="45.6" cy="19.4" r="0.7" fill="#9dffc4" />

      <Face name="idle">
        <rect
          x="23.2"
          y="21.6"
          width="6.2"
          height="3.1"
          rx="1.5"
          fill="#7dffb3"
          className="pixel-char__eye"
        />
        <rect
          x="34.6"
          y="21.6"
          width="6.2"
          height="3.1"
          rx="1.5"
          fill="#7dffb3"
          className="pixel-char__eye"
        />
        <path
          d="M26.4 31.4c2.4 2.2 8.8 2.2 11.2 0"
          fill="none"
          stroke="#7dffb3"
          strokeWidth="1.4"
          strokeLinecap="round"
          className="pixel-char__mouth"
        />
      </Face>
      <Face name="listen">
        <rect
          x="22.6"
          y="20.8"
          width="7"
          height="3.6"
          rx="1.7"
          fill="#c8ffe0"
          className="pixel-char__eye"
        />
        <rect
          x="34.4"
          y="20.8"
          width="7"
          height="3.6"
          rx="1.7"
          fill="#c8ffe0"
          className="pixel-char__eye"
        />
        <rect
          x="24.2"
          y="28.2"
          width="1.7"
          height="5.2"
          rx="0.8"
          fill="#7dffb3"
          className="pixel-wave-bar"
        />
        <rect
          x="27.2"
          y="26.8"
          width="1.7"
          height="7.4"
          rx="0.8"
          fill="#c8ffe0"
          className="pixel-wave-bar"
        />
        <rect
          x="30.2"
          y="25.6"
          width="1.7"
          height="9.2"
          rx="0.8"
          fill="#7dffb3"
          className="pixel-wave-bar"
        />
        <rect
          x="33.2"
          y="26.8"
          width="1.7"
          height="7.4"
          rx="0.8"
          fill="#c8ffe0"
          className="pixel-wave-bar"
        />
        <rect
          x="36.2"
          y="28.2"
          width="1.7"
          height="5.2"
          rx="0.8"
          fill="#7dffb3"
          className="pixel-wave-bar"
        />
      </Face>
      <Face name="think">
        <rect
          x="23.4"
          y="20.4"
          width="6"
          height="3"
          rx="1.4"
          fill="#7dffb3"
          className="pixel-char__eye"
        />
        <rect
          x="34.8"
          y="20.4"
          width="6"
          height="3"
          rx="1.4"
          fill="#7dffb3"
          className="pixel-char__eye"
        />
        <circle cx="28.4" cy="28.2" r="1.05" fill="#3aa56c" className="pixel-think-dot" />
        <circle cx="32" cy="30.4" r="1.05" fill="#7dffb3" className="pixel-think-dot" />
        <circle cx="35.6" cy="28.2" r="1.05" fill="#3aa56c" className="pixel-think-dot" />
      </Face>
      <Face name="read">
        <rect
          x="22.8"
          y="22"
          width="8"
          height="2.2"
          rx="1.1"
          fill="#7dffb3"
          className="pixel-char__scan-eye"
        />
        <rect
          x="33.2"
          y="22"
          width="8"
          height="2.2"
          rx="1.1"
          fill="#7dffb3"
          className="pixel-char__scan-eye"
        />
        <rect
          x="22.4"
          y="25.6"
          width="19.2"
          height="1.1"
          rx="0.5"
          fill="#7dffb3"
          className="pixel-char__read-line"
        />
        <path d="M27 31.6h10" stroke="#3aa56c" strokeWidth="1.3" strokeLinecap="round" />
      </Face>
      <Face name="speak">
        <rect
          x="23.2"
          y="21"
          width="6.2"
          height="3.1"
          rx="1.5"
          fill="#c8ffe0"
          className="pixel-char__eye"
        />
        <rect
          x="34.6"
          y="21"
          width="6.2"
          height="3.1"
          rx="1.5"
          fill="#c8ffe0"
          className="pixel-char__eye"
        />
        <rect
          x="24.2"
          y="27.6"
          width="1.7"
          height="5.4"
          rx="0.8"
          fill="#7dffb3"
          className="pixel-wave-bar"
        />
        <rect
          x="27.2"
          y="26.4"
          width="1.7"
          height="7.4"
          rx="0.8"
          fill="#c8ffe0"
          className="pixel-wave-bar"
        />
        <rect
          x="30.2"
          y="25.2"
          width="1.7"
          height="9.2"
          rx="0.8"
          fill="#7dffb3"
          className="pixel-wave-bar"
        />
        <rect
          x="33.2"
          y="26.4"
          width="1.7"
          height="7.4"
          rx="0.8"
          fill="#c8ffe0"
          className="pixel-wave-bar"
        />
        <rect
          x="36.2"
          y="27.6"
          width="1.7"
          height="5.4"
          rx="0.8"
          fill="#7dffb3"
          className="pixel-wave-bar"
        />
        <ellipse
          cx="32"
          cy="31.6"
          rx="4.4"
          ry="1.15"
          fill="#7dffb3"
          className="pixel-char__mouth"
        />
        <ellipse
          cx="32"
          cy="32.1"
          rx="3.2"
          ry="1.7"
          fill="#c8ffe0"
          className="pixel-char__mouth-open"
        />
      </Face>
      <Face name="success">
        <rect
          x="23.4"
          y="22.2"
          width="6"
          height="2.2"
          rx="1.1"
          fill="#c8ffe0"
          className="pixel-char__eye"
        />
        <rect
          x="34.6"
          y="22.2"
          width="6"
          height="2.2"
          rx="1.1"
          fill="#c8ffe0"
          className="pixel-char__eye"
        />
        <path
          d="M25.8 30.2c2.8 3.2 9.6 3.2 12.4 0"
          fill="none"
          stroke="#c8ffe0"
          strokeWidth="1.5"
          strokeLinecap="round"
        />
      </Face>
      <Face name="warn">
        <rect
          x="23.6"
          y="21.6"
          width="5.4"
          height="3.8"
          rx="1.4"
          fill="#7dffb3"
          className="pixel-char__eye"
        />
        <rect
          x="35"
          y="21.6"
          width="5.4"
          height="3.8"
          rx="1.4"
          fill="#7dffb3"
          className="pixel-char__eye"
        />
        <path d="M27.6 31.8h8.8" stroke="#3aa56c" strokeWidth="1.4" strokeLinecap="round" />
      </Face>
      <Face name="ask">
        <rect
          x="22.8"
          y="21.2"
          width="6.2"
          height="3.1"
          rx="1.5"
          fill="#7dffb3"
          className="pixel-char__eye"
        />
        <rect
          x="35.2"
          y="22"
          width="5.4"
          height="3.8"
          rx="1.5"
          fill="#3aa56c"
          className="pixel-char__eye"
        />
        <circle cx="32" cy="30.4" r="1.4" fill="#c8ffe0" />
        <rect x="31.4" y="32.4" width="1.3" height="2.2" rx="0.6" fill="#7dffb3" />
      </Face>
      <Face name="error">
        <rect
          x="21.6"
          y="21.4"
          width="20.8"
          height="2"
          rx="0.8"
          fill="#3aa56c"
          className="pixel-char__glitch"
        />
        <rect
          x="23.4"
          y="25.6"
          width="17.2"
          height="2"
          rx="0.8"
          fill="#7dffb3"
          className="pixel-char__glitch"
        />
        <rect
          x="25.6"
          y="29.8"
          width="12.8"
          height="2"
          rx="0.8"
          fill="#3aa56c"
          className="pixel-char__glitch"
        />
      </Face>
      <Face name="offline">
        <rect x="23.6" y="22.2" width="6" height="2" rx="1" fill="#3aa56c" />
        <rect x="34.4" y="22.2" width="6" height="2" rx="1" fill="#3aa56c" />
        <path
          d="M27.2 26.4 36.8 34.2M36.8 26.4 27.2 34.2"
          stroke="#3aa56c"
          strokeWidth="1.4"
          strokeLinecap="round"
        />
      </Face>
      <g className="pixel-char__quiet">
        <path d="M29.4 27.6h5.2v2.2H29.4z" fill="#3aa56c" />
        <path d="M31.4 25.4h1.4v6.4H31.4z" fill="#3aa56c" />
      </g>
    </g>
  );
}

function PixelTorso() {
  const paint = usePaint();
  return (
    <g className="pixel-char__torso">
      <rect x="26.4" y="42.6" width="11.2" height="5.2" rx="2.2" fill={paint("metal")} />
      <circle cx="29.2" cy="45.2" r="0.7" fill="#7dffb3" opacity="0.7" />
      <circle cx="34.8" cy="45.2" r="0.7" fill="#7dffb3" opacity="0.7" />
      <rect x="17.6" y="46.6" width="28.8" height="20.4" rx="5.2" fill="#07140e" />
      <rect x="18.6" y="47.4" width="26.8" height="18.8" rx="4.6" fill={paint("armor")} />
      <rect x="19.6" y="48.2" width="11" height="6" rx="2.4" fill="#ffffff" opacity="0.22" />
      <rect x="20.2" y="48.6" width="4.2" height="3.2" rx="0.8" fill="#1d6a44" />
      <rect x="39.6" y="48.6" width="4.2" height="3.2" rx="0.8" fill="#1d6a44" />
      <rect x="20.2" y="59.4" width="4.2" height="3.2" rx="0.8" fill="#1d6a44" />
      <rect x="39.6" y="59.4" width="4.2" height="3.2" rx="0.8" fill="#1d6a44" />
      <path
        d="M32 50.4 35.6 56.6 32 61.2 28.4 56.6Z"
        fill="#1f8a5a"
        className="pixel-char__chest"
      />
      <path
        d="M32 51.6 34.4 56.2 32 59.4 29.6 56.2Z"
        fill="#7dffb3"
        className="pixel-char__chest"
      />
      <g className="pixel-char__chest-fx pixel-char__chest-fx--scan">
        <rect x="28.6" y="54.6" width="6.8" height="1.1" rx="0.5" fill="#c8ffe0" />
      </g>
      <g className="pixel-char__chest-fx pixel-char__chest-fx--check">
        <path
          d="M29.4 55.8 31.2 57.6 34.8 53.8"
          fill="none"
          stroke="#c8ffe0"
          strokeWidth="1.3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </g>
      <g className="pixel-char__chest-fx pixel-char__chest-fx--shield">
        <path
          d="M32 52.4c2.4 1.2 3.6 2.6 3.6 5.2 0 2.2-1.6 3.8-3.6 4.8-2-1-3.6-2.6-3.6-4.8 0-2.6 1.2-4 3.6-5.2Z"
          fill="#7dffb3"
          opacity="0.85"
        />
      </g>
      <rect x="19.6" y="65.6" width="24.8" height="3.6" rx="1.6" fill={paint("metal")} />
    </g>
  );
}

function Arm({ side }: { side: "left" | "right" }) {
  const paint = usePaint();
  const left = side === "left";
  const sx = left ? 16 : 48;
  const ux = left ? 13.6 : 47.2;
  const fx = left ? 12.2 : 48.4;
  const hx = left ? 9.2 : 49.6;
  return (
    <g className={`pixel-char__arm pixel-char__arm--${side}`}>
      <g className="pixel-char__shoulder">
        <circle cx={sx} cy="50.4" r="4.2" fill="#07140e" />
        <circle cx={sx} cy="50.4" r="3.3" fill={paint("joint")} />
        <circle cx={sx - 0.7} cy="49.6" r="1.1" fill="#ffffff" opacity="0.28" />
      </g>
      <g className="pixel-char__upper">
        <rect x={ux} y="52.6" width="6.4" height="10.4" rx="3.1" fill={paint("armor")} />
        <g className="pixel-char__elbow">
          <circle cx={ux + 3.2} cy="63.4" r="2.3" fill={paint("joint")} />
          <g className="pixel-char__fore">
            <rect x={fx} y="64.4" width="6.4" height="9.2" rx="3.1" fill={paint("metal")} />
            <g className="pixel-char__wrist">
              <rect x={fx - 0.2} y="72.4" width="6.8" height="2.2" rx="1" fill="#2a322e" />
              <g className="pixel-char__hand">
                <rect x={hx} y="73.8" width="8.4" height="6.4" rx="2.2" fill="#2a322e" />
                <rect x={hx + 1.1} y="75" width="1.2" height="4.2" rx="0.5" fill="#5a6560" />
                <rect x={hx + 3.2} y="75.2" width="1.2" height="4.4" rx="0.5" fill="#5a6560" />
                <rect x={hx + 5.3} y="75" width="1.2" height="4.2" rx="0.5" fill="#5a6560" />
              </g>
            </g>
          </g>
        </g>
      </g>
    </g>
  );
}

function Leg({ side }: { side: "left" | "right" }) {
  const paint = usePaint();
  const x = side === "left" ? 21.4 : 36.2;
  return (
    <g className={`pixel-char__leg pixel-char__leg--${side}`}>
      <g className="pixel-char__hip">
        <rect x={x} y="67.2" width="7.6" height="3.2" rx="1.4" fill={paint("joint")} />
        <g className="pixel-char__thigh">
          <rect x={x} y="69.2" width="7.6" height="11.2" rx="3.4" fill={paint("armor")} />
          <g className="pixel-char__knee">
            <circle cx={x + 3.8} cy="81" r="2.5" fill={paint("joint")} />
            <g className="pixel-char__boot">
              <rect x={x - 0.6} y="82.2" width="9.2" height="9.4" rx="2.6" fill={paint("boot")} />
              <rect x={x - 1.6} y="90.4" width="12.2" height="4.2" rx="1.6" fill="#0e3a26" />
              <rect x={x + 6.4} y="91" width="3.6" height="2.2" rx="0.8" fill="#2f8f5c" />
            </g>
          </g>
        </g>
      </g>
    </g>
  );
}

function PixelEffects() {
  return (
    <g className="pixel-char__fx">
      <g className="pixel-char__prop pixel-char__prop--page">
        <rect x="2.4" y="56.4" width="11.2" height="13.6" rx="1.6" fill="#07140e" />
        <rect x="3.2" y="57.2" width="9.6" height="12" rx="1.2" fill="#f7fff9" />
        <rect x="4.4" y="59.4" width="7.2" height="1.1" rx="0.4" fill="#1f8a5a" />
        <rect x="4.4" y="62.2" width="7.2" height="1.1" rx="0.4" fill="#1d6a44" />
        <rect x="4.4" y="65" width="4.8" height="1.1" rx="0.4" fill="#3aa56c" />
      </g>
      <g className="pixel-char__prop pixel-char__prop--wrench">
        <rect x="48.4" y="58.2" width="9.2" height="2" rx="1" fill="#7dffb3" />
        <rect x="55.2" y="55.6" width="3.2" height="7.2" rx="1.2" fill="#c8ffe0" />
      </g>
      <g className="pixel-char__prop pixel-char__prop--thumb">
        <rect x="51.6" y="47.2" width="4.2" height="8.4" rx="2" fill="#7dffb3" />
        <rect x="53.4" y="45.2" width="3.2" height="3.2" rx="1.4" fill="#c8ffe0" />
      </g>
      <g className="pixel-char__bits">
        <circle cx="7.2" cy="40.4" r="1.2" fill="#3aa56c" className="pixel-bit" />
        <circle cx="56.6" cy="36.4" r="1.3" fill="#7dffb3" className="pixel-bit" />
        <circle cx="8.6" cy="28.2" r="0.8" fill="#4cba7a" className="pixel-bit" />
      </g>
    </g>
  );
}

function PixelDefs({ id }: { id: string }) {
  const n = (name: string) => `${id}-${name}`;
  return (
    <defs>
      <linearGradient id={n("casing")} x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stopColor="#3d7a58" />
        <stop offset="42%" stopColor="#1c4634" />
        <stop offset="100%" stopColor="#0a1c14" />
      </linearGradient>
      <linearGradient id={n("bezel")} x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stopColor="#ffffff" />
        <stop offset="48%" stopColor="#e8f4ec" />
        <stop offset="100%" stopColor="#b7cbbf" />
      </linearGradient>
      <linearGradient id={n("armor")} x1="0.15" y1="0" x2="0.85" y2="1">
        <stop offset="0%" stopColor="#ffffff" />
        <stop offset="36%" stopColor="#f4fbf6" />
        <stop offset="100%" stopColor="#c3d6cb" />
      </linearGradient>
      <linearGradient id={n("metal")} x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stopColor="#4cba7a" />
        <stop offset="46%" stopColor="#1d6a44" />
        <stop offset="100%" stopColor="#0b2f1e" />
      </linearGradient>
      <linearGradient id={n("joint")} x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stopColor="#6fd49a" />
        <stop offset="100%" stopColor="#143528" />
      </linearGradient>
      <linearGradient id={n("boot")} x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stopColor="#3aa56c" />
        <stop offset="100%" stopColor="#0b2f1e" />
      </linearGradient>
      <radialGradient id={n("orb")} cx="34%" cy="28%" r="72%">
        <stop offset="0%" stopColor="#e9fff3" />
        <stop offset="48%" stopColor="#4cba7a" />
        <stop offset="100%" stopColor="#0e3a26" />
      </radialGradient>
      <radialGradient id={n("screen")} cx="48%" cy="36%" r="74%">
        <stop offset="0%" stopColor="#1a7048" />
        <stop offset="62%" stopColor="#071a12" />
        <stop offset="100%" stopColor="#020806" />
      </radialGradient>
      <filter id={n("shadow")} x="-18%" y="-8%" width="136%" height="128%">
        <feDropShadow dx="0" dy="1.6" stdDeviation="1.4" floodColor="#07140e" floodOpacity="0.28" />
      </filter>
    </defs>
  );
}

export function PixelCharacter({ compact = false }: { compact?: boolean }) {
  const paintId = useId().replace(/:/g, "");
  return (
    <Paint.Provider value={paintId}>
      <svg
        className={compact ? "pixel-char pixel-char--compact" : "pixel-char"}
        viewBox={compact ? "10 8 44 36" : "0 0 64 96"}
        width={compact ? 44 : 256}
        height={compact ? 36 : 384}
        aria-hidden="true"
      >
        <PixelDefs id={paintId} />
        {compact ? (
          <PixelHead />
        ) : (
          <g className="pixel-char__rig" filter={`url(#${paintId}-shadow)`}>
            <ellipse cx="32" cy="94.4" rx="15" ry="2.1" fill="#07140e" opacity="0.22" />
            <g className="pixel-char__lower">
              <Leg side="left" />
              <Leg side="right" />
            </g>
            <g className="pixel-char__core">
              <Arm side="left" />
              <PixelTorso />
              <Arm side="right" />
              <PixelHead />
            </g>
            <PixelEffects />
          </g>
        )}
      </svg>
    </Paint.Provider>
  );
}
