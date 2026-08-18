export const STARTER_PROMPTS = [
  { id: "about", label: "What is Cyber Florida?" },
  { id: "phish", label: "Explain phishing." },
  { id: "programs", label: "What programs are available for students?" },
  { id: "scam", label: "I clicked a suspicious link. What should I do?" },
] as const;

type StarterPromptsProps = {
  onChoose: (text: string) => void;
  disabled: boolean;
};

export function StarterPrompts({ onChoose, disabled }: StarterPromptsProps) {
  return (
    <div className="transcript--empty">
      <p>Ask Pixel about Cyber Florida or defensive cybersecurity. Try a starting question:</p>
      <ul className="starters">
        {STARTER_PROMPTS.map((item) => (
          <li key={item.id}>
            <button type="button" disabled={disabled} onClick={() => onChoose(item.label)}>
              {item.label}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
