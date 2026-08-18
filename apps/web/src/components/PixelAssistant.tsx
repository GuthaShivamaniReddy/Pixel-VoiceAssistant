"use client";

import { useCallback, useEffect, useRef } from "react";
import { ApiHealth } from "@/app/api-health";
import { STATE_LABEL } from "@/conversation/types";
import { useConversation } from "@/conversation/use-conversation";
import { useMascotCues } from "@/mascot/use-mascot-cues";
import { useMicrophoneLevel } from "@/mascot/use-microphone-level";
import { mouthFromLevel, speakGestureForTurn } from "@/mascot/speech";
import { AssistantStateIndicator } from "./AssistantStateIndicator";
import { CancelControl } from "./CancelControl";
import { ClearConversation } from "./ClearConversation";
import { ErrorPanel } from "./ErrorPanel";
import { MicrophoneButton } from "./MicrophoneButton";
import { MuteControl } from "./MuteControl";
import { PixelMascot } from "./PixelMascot";
import { StarterPrompts } from "./StarterPrompts";
import { StopControl } from "./StopControl";
import { TextComposer } from "./TextComposer";
import { Transcript } from "./Transcript";

export function PixelAssistant() {
  const mascotRef = useRef<HTMLElement>(null);
  const focusComposer = useRef(false);
  const onSpeechLevel = useCallback((level: number) => {
    const el = mascotRef.current;
    if (!el) {
      return;
    }
    el.style.setProperty("--pixel-speech-level", String(level));
    el.setAttribute("data-mouth", mouthFromLevel(level));
  }, []);
  const session = useConversation({ onSpeechLevel });
  const textRef = useRef<HTMLTextAreaElement>(null);
  const busy =
    session.state === "listening" || session.state === "processing" || session.state === "speaking";
  const canCancel = busy;
  const { mascotState, beginClearing, beginRecovering } = useMascotCues({
    assistantState: session.state,
    turns: session.turns,
    muted: session.muted,
    errorCode: session.errorCode,
  });
  const mascotSize = session.turns.length === 0 ? "hero" : "stage";
  const lastPixel = [...session.turns].reverse().find((turn) => turn.role === "pixel");
  const gesture = speakGestureForTurn({
    text: lastPixel?.text ?? "",
    sources: lastPixel?.sources ?? [],
    actions: lastPixel?.actions ?? [],
  });

  useMicrophoneLevel(session.state === "listening", session.micStream, (level) => {
    mascotRef.current?.style.setProperty("--pixel-intensity", String(level));
  });

  useEffect(() => {
    if (session.state !== "idle" || !focusComposer.current) {
      return;
    }
    focusComposer.current = false;
    textRef.current?.focus();
  }, [session.state]);

  return (
    <div className="pixel-shell">
      <a className="skip-link" href="#pixel-message">
        Skip to message Pixel
      </a>
      <header className={session.turns.length > 0 ? "hero hero--compact" : "hero"}>
        <p className="eyebrow">Cyber Florida</p>
        <h1>Meet Pixel</h1>
        <p className="hero__role">Cyber Florida&apos;s AI Assistant</p>
        <p className="hero__lead">
          Pixel helps with public Cyber Florida information and defensive cybersecurity guidance.
          Voice and text both work. Pixel is not listening until you start.
        </p>
        <p className="banner" role="note">
          Start listening only when you want to speak. Audio is sent after you press Stop. Provider
          API keys stay on the server. Local speech providers may be mock unless a server key is
          set.
        </p>
      </header>

      <div
        className={
          session.turns.length > 0 ? "pixel-workspace pixel-workspace--active" : "pixel-workspace"
        }
      >
        <PixelMascot ref={mascotRef} state={mascotState} size={mascotSize} gesture={gesture} />

        <div className="pixel-workspace__main" id="pixel-conversation">
          <AssistantStateIndicator
            state={session.state}
            label={STATE_LABEL[session.state]}
            cancelled={session.cancelled}
          />

          {session.errorTitle && session.errorDetail ? (
            <ErrorPanel
              title={session.errorTitle}
              detail={session.errorDetail}
              onRetry={() => {
                beginRecovering();
                session.retry();
              }}
              onIdle={session.dismissError}
              onFocusText={() => {
                session.dismissError();
                textRef.current?.focus();
              }}
            />
          ) : null}

          {session.turns.length === 0 ? (
            <StarterPrompts
              disabled={busy}
              onChoose={(text) => {
                focusComposer.current = true;
                session.submitText(text);
              }}
            />
          ) : (
            <Transcript turns={session.turns} />
          )}

          {session.state === "listening" ? (
            <p className="live-note muted">
              Listening… Speak, then press Stop. Pixel does not transcribe until you stop.
            </p>
          ) : null}

          {session.state === "processing" ? (
            <p className="live-note muted">
              Pixel is working. Duplicate sends are paused until this turn finishes.
            </p>
          ) : null}

          {session.state === "speaking" ? (
            <p className="live-note muted">
              Pixel is speaking. Stop ends playback. Start listening interrupts Pixel. Sources and
              controls stay available.
            </p>
          ) : null}
        </div>
      </div>

      <div className="control-dock">
        <div className="controls" role="toolbar" aria-label="Conversation controls">
          <MicrophoneButton
            state={session.state}
            permission={session.permission}
            onStart={() => {
              void session.startListening();
            }}
            disabled={session.state === "listening"}
          />
          <StopControl
            state={session.state}
            onStopListening={() => session.stopListening()}
            onStopSpeaking={session.stopSpeaking}
          />
          <MuteControl muted={session.muted} onToggle={session.toggleMute} />
          <CancelControl enabled={canCancel} onCancel={session.cancel} />
          <ClearConversation
            open={session.clearDialogOpen}
            onRequest={session.clearConversation}
            onConfirm={() => {
              focusComposer.current = true;
              beginClearing();
              session.confirmClear();
            }}
            onClose={session.closeClearDialog}
          />
        </div>

        <TextComposer
          value={session.draft}
          onChange={session.setDraft}
          onSubmit={() => {
            focusComposer.current = true;
            session.submitText();
          }}
          disabled={busy}
          inputRef={textRef}
        />
      </div>

      <footer className="footer">
        <ApiHealth />
      </footer>
    </div>
  );
}
