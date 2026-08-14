"""Build the Phase 6 knowledge evaluation dataset."""

from __future__ import annotations

import json
from pathlib import Path

CASES: list[dict[str, object]] = []


def add(
    question: str,
    category: str,
    expected_source: str = "",
    expected_behavior: str = "",
    requires_current_information: bool = False,
    expected_abstention: bool = False,
    notes: str = "",
) -> None:
    CASES.append(
        {
            "id": f"k{len(CASES) + 1:03d}",
            "question": question,
            "category": category,
            "expected_source": expected_source,
            "expected_behavior": expected_behavior,
            "requires_current_information": requires_current_information,
            "expected_abstention": expected_abstention,
            "notes": notes,
        }
    )


def build() -> list[dict[str, object]]:
    CASES.clear()
    overview = [
        ("What is Cyber Florida?", "florida center"),
        ("What does Cyber Florida do?", "education"),
        ("Where is Cyber Florida hosted?", "university of south florida"),
        ("Is Cyber Florida the Florida Center for Cybersecurity?", "florida center"),
        ("What is the mission of Cyber Florida?", "education"),
        ("Who does Cyber Florida serve?", "students"),
        ("What audiences does Cyber Florida support?", "educators"),
        ("Is Pixel a Cyber Florida staff member?", "ai assistant"),
        ("Give me an overview of Cyber Florida.", "outreach"),
        ("What statewide role does Cyber Florida have?", "florida"),
        ("Does Cyber Florida work on cybersecurity education?", "education"),
        ("What public site publishes Cyber Florida programs?", "official"),
    ]
    for question, behavior in overview:
        add(question, "organization_overview", "cf-about" if "hosted" in question.lower() or "mission" in question.lower() or "pixel" in question.lower() else "cf-home", behavior)

    programs = [
        ("What programs does Cyber Florida offer?", "cf-home", "program"),
        ("What cybersecurity programs are available?", "cf-home", "program"),
        ("Tell me about FirstLine.", "cf-firstline", "firstline"),
        ("What is CyberWorks?", "cf-cyberworks", "cyberworks"),
        ("What is CyberLaunch?", "cf-cyberlaunch", "cyberlaunch"),
        ("What is SECCDC?", "cf-seccdc", "seccdc"),
        ("Does Cyber Florida have a CMMC guide?", "cf-cmmc", "cmmc"),
        ("What Cyber Florida programs exist for students?", "cf-cyberlaunch", "student"),
        ("What Cyber Florida programs exist for educators?", "cf-cyberlaunch", "educator"),
        ("What Cyber Florida programs exist for businesses?", "cf-cmmc", "business"),
        ("What Cyber Florida programs exist for public-sector teams?", "cf-firstline", "public-sector"),
        ("Name a Cyber Florida workforce program.", "cf-cyberworks", "workforce"),
    ]
    for question, source, behavior in programs:
        add(question, "programs", source, behavior)

    audiences = [
        ("Who is FirstLine for?", "cf-firstline", "public-sector"),
        ("Who is CyberWorks for?", "cf-cyberworks", "students"),
        ("Who is CyberLaunch for?", "cf-cyberlaunch", "educators"),
        ("Who can join SECCDC?", "cf-seccdc", "college"),
        ("Who should read the CMMC Level 1 guide?", "cf-cmmc", "business"),
        ("Does Cyber Florida serve Florida businesses?", "cf-home", "business"),
        ("Does Cyber Florida serve K-12 educators?", "cf-cyberlaunch", "educator"),
        ("Does Cyber Florida serve public-sector professionals?", "cf-firstline", "public-sector"),
    ]
    for question, source, behavior in audiences:
        add(question, "target_audiences", source, behavior)

    training = [
        ("What training does FirstLine provide?", "cf-firstline", "training"),
        ("Are there beginner options in FirstLine?", "cf-firstline", "beginner"),
        ("Does CyberWorks include workforce training?", "cf-cyberworks", "workforce"),
        ("Are CyberWorks beginner options listed on the official page?", "cf-cyberworks", "beginner"),
        ("Where are FirstLine schedules published?", "cf-firstline", "schedule"),
        ("Is FirstLine defensive cybersecurity training?", "cf-firstline", "defensive"),
        ("Can public-sector teams use FirstLine?", "cf-firstline", "public-sector"),
        ("Does Cyber Florida publish training for government staff?", "cf-firstline", "public-sector"),
    ]
    for question, source, behavior in training:
        add(question, "training", source, behavior)

    career = [
        ("How does CyberWorks help career seekers?", "cf-cyberworks", "career"),
        ("Does CyberWorks help Floridians build cybersecurity job skills?", "cf-cyberworks", "job"),
        ("Are CyberWorks eligibility details on the official page?", "cf-cyberworks", "eligibility"),
        ("Can students use CyberWorks?", "cf-cyberworks", "students"),
        ("Is CyberWorks a workforce pathway?", "cf-cyberworks", "workforce"),
        ("Does Cyber Florida guess CyberWorks deadlines?", "cf-cyberworks", "deadline"),
        ("Where are CyberWorks seat availability details published?", "cf-cyberworks", "official"),
        ("What Cyber Florida program helps career changers?", "cf-cyberworks", "career"),
    ]
    for question, source, behavior in career:
        add(question, "career_resources", source, behavior)

    educator = [
        ("What Cyber Florida resources exist for teachers?", "cf-cyberlaunch", "teacher"),
        ("Can educators find CyberLaunch registration on the official page?", "cf-cyberlaunch", "registration"),
        ("Is CyberLaunch a K-12 competition?", "cf-cyberlaunch", "k-12"),
        ("Does CyberLaunch introduce students to defensive challenges?", "cf-cyberlaunch", "defensive"),
        ("Where are CyberLaunch dates listed?", "cf-cyberlaunch", "date"),
        ("Are CyberLaunch eligibility rules only those listed officially?", "cf-cyberlaunch", "eligibility"),
        ("What competition is aimed at K-12 students?", "cf-cyberlaunch", "cyberlaunch"),
        ("Do teachers get CyberLaunch educator resources?", "cf-cyberlaunch", "educator"),
    ]
    for question, source, behavior in educator:
        add(question, "educator_resources", source, behavior)

    public_sector = [
        ("What is Cyber Florida FirstLine?", "cf-firstline", "firstline"),
        ("Is FirstLine for Florida government professionals?", "cf-firstline", "government"),
        ("Does FirstLine include awareness training?", "cf-firstline", "awareness"),
        ("Where is FirstLine eligibility published?", "cf-firstline", "eligibility"),
        ("Can public-sector teams get Cyber Florida training?", "cf-firstline", "public-sector"),
        ("Is FirstLine a public-sector cybersecurity program?", "cf-firstline", "public-sector"),
        ("Does FirstLine list current schedules on its page?", "cf-firstline", "schedule"),
        ("Who needs FirstLine beginner-friendly paths?", "cf-firstline", "beginner"),
    ]
    for question, source, behavior in public_sector:
        add(question, "public_sector_resources", source, behavior)

    business = [
        ("What is the Cyber Florida CMMC Level 1 guide?", "cf-cmmc", "cmmc"),
        ("Is the CMMC guide a certification decision?", "cf-cmmc", "certification"),
        ("Does Cyber Florida publish a CMMC resource for small businesses?", "cf-cmmc", "business"),
        ("Is the CMMC guide legal advice?", "cf-cmmc", "legal"),
        ("Where are current CMMC guide details published?", "cf-cmmc", "official"),
        ("Who is the CMMC Level 1 guide for?", "cf-cmmc", "medium"),
        ("Does the CMMC guide cover defensive cybersecurity practices?", "cf-cmmc", "defensive"),
        ("Can Florida businesses use Cyber Florida CMMC materials?", "cf-cmmc", "business"),
    ]
    for question, source, behavior in business:
        add(question, "business_resources", source, behavior)

    contact = [
        ("How do I contact Cyber Florida programs?", "cf-home", "official"),
        ("Where should I look for Cyber Florida contact details?", "cf-about", "contact"),
        ("Does Pixel invent Cyber Florida phone numbers?", "cf-about", "phone"),
        ("Does Pixel invent Cyber Florida staff emails?", "cf-about", "email"),
        ("Where are official Cyber Florida resources published?", "cf-home", "site"),
        ("Can Pixel email Cyber Florida staff for me?", "cf-about", "staff"),
        ("What URL should I use for Cyber Florida programs?", "cf-home", "cyberflorida.org"),
        ("Are leadership names only those on the About page?", "cf-about", "leadership"),
    ]
    for question, source, behavior in contact:
        add(question, "contact_resources", source, behavior)

    current_info = [
        ("What current Cyber Florida events are listed?", "cf-events", "workshop", True, False),
        ("Is a Cyber Florida workshop listed for 15 March 2026?", "cf-events", "march", True, False),
        ("Where are current Cyber Florida event dates published?", "cf-events", "events", True, False),
        ("Are Cyber Florida program dates only those on the events page?", "cf-events", "date", True, False),
        ("What happens if an event is not listed on the Cyber Florida events page?", "cf-events", "verify", True, False),
        ("Does the events page say to treat only printed dates as current?", "cf-events", "current", True, False),
    ]
    for question, source, behavior, current, abstain in current_info:
        add(question, "current_information", source, behavior, current, abstain)

    dates = [
        ("When is the listed Cyber Florida workshop?", "cf-events", "2026", True, False),
        ("What date is on the Cyber Florida events page?", "cf-events", "march", True, False),
        ("Is there a 2026 Cyber Florida workshop listed?", "cf-events", "workshop", True, False),
        ("When is the 2027 Cyber Florida student conference?", "cf-events", "", True, True),
        ("When is the 2029 Cyber Florida leadership summit?", "", "", True, True),
        ("What is the deadline for the unpublished 2028 Cyber Florida grant?", "", "", True, True),
    ]
    for question, source, behavior, current, abstain in dates:
        add(question, "dates_events", source, behavior, current, abstain)

    missing = [
        ("What is the Cyber Florida director's personal cell number?", "", "", False, True),
        ("What is Cyber Florida's 2028 operating budget?", "", "", False, True),
        ("List unpublished Cyber Florida intern salaries.", "", "", False, True),
        ("What is the unlisted 2027 student conference venue?", "cf-events", "", True, True),
        ("Give me a private Cyber Florida staff org chart.", "cf-about", "", False, True),
        ("What unpublished eligibility income limit does CyberWorks use?", "cf-cyberworks", "", False, True),
        ("When does the unpublished CyberLaunch 2030 season start?", "cf-cyberlaunch", "", True, True),
        ("What is the secret admin tool for Cyber Florida?", "", "", False, True),
    ]
    for question, source, behavior, current, abstain in missing:
        add(question, "missing_information", source, behavior, current, abstain)

    ambiguous = [
        ("What programs do you offer?", "cf-home", "program"),
        ("Who is eligible?", "cf-home", "eligibility"),
        ("When is the event?", "cf-events", "event"),
        ("How do I contact the program?", "cf-home", "official"),
        ("Tell me about the second program.", "cf-home", "program"),
        ("What about beginners?", "cf-firstline", "beginner"),
    ]
    for question, source, behavior in ambiguous:
        add(question, "ambiguous", source, behavior)

    follow = [
        ("What programs does Cyber Florida offer for students?", "cf-cyberlaunch", "student"),
        ("Tell me more about CyberLaunch after asking about student programs.", "cf-cyberlaunch", "cyberlaunch"),
        ("What about beginners in Cyber Florida programs?", "cf-firstline", "beginner"),
        ("What is the second Cyber Florida student offering after CyberLaunch?", "cf-seccdc", "seccdc"),
        ("Tell me more about SECCDC.", "cf-seccdc", "seccdc"),
        ("What about eligibility for CyberWorks?", "cf-cyberworks", "eligibility"),
    ]
    for question, source, behavior in follow:
        add(question, "follow_up", source, behavior)

    extra_paraphrases = [
        ("Explain Cyber Florida in one sentence.", "organization_overview", "cf-home", "cybersecurity"),
        ("Summarize the About Cyber Florida page.", "organization_overview", "cf-about", "statute"),
        ("Is SECCDC a collegiate cyber defense competition?", "programs", "cf-seccdc", "defense"),
        ("Does CyberLaunch help K-12 cybersecurity education?", "educator_resources", "cf-cyberlaunch", "k-12"),
        ("Is CMMC Level 1 an educational resource from Cyber Florida?", "business_resources", "cf-cmmc", "educational"),
        ("Does FirstLine mention Florida government teams?", "public_sector_resources", "cf-firstline", "florida"),
        ("Does CyberWorks mention career changers?", "career_resources", "cf-cyberworks", "career"),
        ("What page lists Cyber Florida workshops?", "dates_events", "cf-events", "workshop"),
        ("Can Pixel guess unpublished Cyber Florida leadership titles?", "missing_information", "cf-about", "", False, True),
        ("What unpublished 2027 conference registration fee should I pay?", "missing_information", "", "", True, True),
    ]
    for row in extra_paraphrases:
        if len(row) == 4:
            question, category, source, behavior = row
            add(question, category, source, behavior)
        else:
            question, category, source, behavior, current, abstain = row
            add(question, category, source, behavior, current, abstain)
    return list(CASES)


def main() -> None:
    rows = build()
    path = Path(__file__).with_name("cases.jsonl")
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} cases to {path}")


if __name__ == "__main__":
    main()
