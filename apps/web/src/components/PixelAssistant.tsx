"use client";

import { useEffect, useRef } from "react";
import { ApiHealth } from "@/app/api-health";
import { STATE_LABEL } from "@/conversation/types";
import { useConversation } from "@/conversation/use-conversation";
import { AssistantStateIndicator } from "./AssistantStateIndicator";
import { CancelControl } from "./CancelControl";
import { ClearConversation } from "./ClearConversation";
import { ErrorPanel } from "./ErrorPanel";
import { MicrophoneButton } from "./MicrophoneButton";
import { MuteControl } from "./MuteControl";
import { StopControl } from "./StopControl";
import { TextComposer } from "./TextComposer";
import { Transcript } from "./Transcript";

export function PixelAssistant() {
  const session = useConversation();
  const textRef = useRef<HTMLTextAreaElement>(null);
  const busy =
    session.state === "listening" || session.state === "processing" || session.state === "speaking";
  const canCancel = busy;

  useEffect(() => {
    if (session.state === "idle" && session.turns.length > 0) {
      textRef.current?.focus();
    }
  }, [session.state, session.turns.length]);

  return (
    <div className="pixel-shell">
      <header className="hero">
        <p className="eyebrow">Cyber Florida</p>
        <h1>Pixel</h1>
        <p>
          An AI assistant for public Cyber Florida information and defensive cybersecurity guidance.
          Pixel is ready. It is not listening until you start.
        </p>
        <p className="banner" role="note">
          Phase 4 voice loop: microphone audio is sent to the Pixel API for speech-to-text, a short
          answer, and text-to-speech. RAG is not implemented. Provider API keys stay on the server.
        </p>
      </header>

      <AssistantStateIndicator
        state={session.state}
        label={STATE_LABEL[session.state]}
        cancelled={session.cancelled}
      />

      {session.errorTitle && session.errorDetail ? (
        <ErrorPanel
          title={session.errorTitle}
          detail={session.errorDetail}
          onRetry={session.retry}
          onIdle={session.dismissError}
          onFocusText={() => {
            session.dismissError();
            textRef.current?.focus();
          }}
        />
      ) : null}

      <Transcript turns={session.turns} />

      {session.state === "listening" ? (
        <p className="muted" role="status">
          Listening. Speak, then press Stop. Push-to-talk — Pixel does not transcribe until you
          stop.
        </p>
      ) : null}

      {session.state === "processing" ? (
        <p className="muted" role="status">
          Input received. Pixel is working. Duplicate sends are disabled until this turn finishes.
        </p>
      ) : null}

      {session.state === "speaking" ? (
        <p className="muted" role="status">
          Pixel is speaking. Stop ends playback. Start listening interrupts Pixel (barge-in).
        </p>
      ) : null}

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
          onConfirm={session.confirmClear}
          onClose={session.closeClearDialog}
        />
      </div>

      <TextComposer
        value={session.draft}
        onChange={session.setDraft}
        onSubmit={session.submitText}
        disabled={
          session.state === "listening" ||
          session.state === "processing" ||
          session.state === "speaking"
        }
        inputRef={textRef}
      />

      <footer className="footer">
        <ApiHealth />
      </footer>
    </div>
  );
}
