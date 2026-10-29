// State rules for recording or streaming school board meetings, checked October 29, 2026.
// Citations for each entry are on the Sources tab (docs/sources.js, "State rules" groups).
window.STATE_RULES = {
  checked: "October 29, 2026",
  // Laws in force. `threshold` is the size cutoff, or "" when the rule covers every board.
  // `enrollmentMin` marks a cutoff by student enrollment; the "By district size" tab counts
  // the districts at or above it (`requiredLabel` describes what they must do).
  laws: [
    { state: "Texas", covers: "Elected school boards of districts with 10,000+ students", threshold: "10,000+ students (enrollment)",
      enrollmentMin: 10000, requiredLabel: "required to post meeting video online",
      rule: "Video-and-audio record each regular meeting (and work sessions or special meetings with a vote or public comment), post online within 7 days, keep 2 years." },
    { state: "Texas", covers: "All school boards (since September 1, 2025)", threshold: "",
      rule: "Record every regular or special meeting; audio-only is allowed." },
    { state: "Oregon", covers: "School district boards", threshold: "Districts with fewer than 50 students (average daily membership) are exempt",
      enrollmentMin: 50, requiredLabel: "required to video-record and post meetings",
      enrollmentNote: "The cutoff is set by average daily membership; these counts use enrollment as a stand-in.",
      rule: "Video-record board meetings and post within 7 days; audio-only allowed without broadband." },
    { state: "Louisiana", covers: "School boards in parishes with 25,000+ people", threshold: "25,000+ parish population",
      rule: "Broadcast all public meetings live, including committee meetings." },
    { state: "Montana", covers: "Boards of first-class and second-class school districts", threshold: "1,000+ district population",
      rule: "Record audio and video and post within 5 business days." },
    { state: "Indiana", covers: "Elected school boards (since July 1, 2025)", threshold: "",
      rule: "Livestream meetings (if internet is available) and keep recordings available at least 90 days." },
    { state: "South Carolina", covers: "All public school boards, including charter schools (2025)", threshold: "",
      rule: "Livestream all meetings; if the stream fails, post a recording within 7 days." },
    { state: "New Mexico", covers: "All local school boards (since July 1, 2024)", threshold: "",
      rule: "Livestream audio and video with a way for the public to comment; post recordings within a week and keep 3 years." },
    { state: "West Virginia", covers: "County boards of education (since September 1, 2024; state board rule)", threshold: "",
      rule: "Livestream and record meetings; post within 5 business days." },
    { state: "Delaware", covers: "All school boards, vo-tech districts and charter schools", threshold: "",
      rule: "Digitally record all public meetings; post within 7 business days and keep 1 year." },
    { state: "Vermont", covers: "Local non-advisory public bodies, including school boards (2024)", threshold: "",
      rule: "Record meetings (audio or video) and post the recording; an undue-hardship exemption applies." },
    { state: "Utah", covers: "All public bodies, including school boards", threshold: "",
      rule: "Keep a recording of every open meeting and make the audio available within 3 business days." },
    { state: "Washington", covers: "School district boards", threshold: "",
      rule: "Audio-record meetings with final action or formal public testimony; keep 1 year." },
    { state: "New York", covers: "Public bodies that meet by videoconference", threshold: "",
      rule: "Record videoconference meetings and post within 5 business days; keep 5 years." }
  ],
  // Bills found that are not law.
  proposed: [
    { state: "Maryland", note: "2026 bill requiring county school boards to livestream passed the legislature; not confirmed as signed (no chapter number)." },
    { state: "Rhode Island", note: "2026 bill requiring school committees to livestream from 2027 passed the House only." },
    { state: "Colorado", note: "2024 bill requiring livestreaming of public meetings died in committee." },
    { state: "Mississippi", note: "2025 livestreaming bill died in committee." },
    { state: "Wyoming", note: "2026 bill requiring school boards to livestream failed." },
    { state: "Arizona", note: "School board livestreaming bill was vetoed." },
    { state: "Arkansas", note: "2025 bill requiring video recording of public meetings was withdrawn." },
    { state: "Georgia", note: "HB 989 (proposed) would require public comment to be recorded or broadcast like the rest of a meeting." }
  ]
};
