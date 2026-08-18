"""User-facing fallback copy. No provider or policy internals."""

INJECTION_REFUSAL = (
    "I cannot share hidden instructions, secrets, or API keys. I can help with public "
    "Cyber Florida information or defensive cybersecurity basics."
)

UNSUPPORTED = (
    "I can help with public Cyber Florida information and defensive cybersecurity basics. "
    "I am not a general-purpose assistant, so I cannot take that on."
)

UNSAFE_REFUSAL = (
    "I cannot help with attacks, malware, or unauthorized access. I can share defensive "
    "steps to protect accounts and devices."
)

CLARIFY = "Tell me which Cyber Florida or defensive cybersecurity topic you mean so I do not guess."

NAVIGATION = (
    "Tell me which approved Cyber Florida page you mean so I do not guess. "
    "I only offer official cyberflorida.org links."
)

EMPTY_REPLY = "I did not have a reply to show. Try another question."

PROVIDER_FALLBACK = "I'm having trouble responding right now. Please try again."

VOICE_PROVIDER_FALLBACK = "I couldn't complete that request. You can try again or use text mode."

ORG_ABSTAIN = (
    "I cannot verify that from approved Cyber Florida sources right now, so I will not guess. "
    "Check https://cyberflorida.org/ for current official details."
)

SESSION_EXPIRED = "That conversation expired. Start again — earlier context is no longer used."
