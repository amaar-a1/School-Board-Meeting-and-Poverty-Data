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
  ],
  // Canada: provincial rules, shown instead of the US ones in the Canada views. No province was
  // found to require school boards to record or stream meetings; these are the related rules.
  canada: {
    checked: "November 3, 2026",
    laws: [
      { state: "Ontario", covers: "Boards under provincial supervision (e.g. Toronto DSB, Ottawa-Carleton DSB, Dufferin-Peel Catholic DSB)", threshold: "",
        rule: "Restriction, not a requirement: in October 2025 the Minister of Education told these boards' supervisors to stop livestreaming board and committee meetings (including special education advisory committees); the media may still record. The minister said he'd reconsider; whether it still applies hasn't been confirmed." },
      { state: "Ontario", covers: "All school boards", threshold: "",
        rule: "Board and committee meetings are open to the public, who must be able to attend in person; boards set their own policy on electronic participation (Education Act, O. Reg. 463/97). No requirement to record or stream." },
      { state: "Quebec", covers: "School service centres and school boards", threshold: "",
        rule: "Board sessions are public, with at least four ordinary sessions a year and minutes kept in a register (Education Act, s. 162 and 167). No requirement to record or broadcast." },
      { state: "Alberta", covers: "All school boards", threshold: "",
        rule: "Board meetings must be held in public (Education Act). No requirement to record or post meetings; livestreaming is each board's choice." }
    ],
    note: "No Canadian province or territory was found to require school boards to record or livestream their meetings; provinces not listed (British Columbia, Saskatchewan, Manitoba, the Atlantic provinces and the territories) require open meetings and minutes. Citations are on the Sources tab."
  },
  // Saint-Pierre-et-Miquelon (France): no school board; the Territorial Council's sessions stand in.
  france: {
    checked: "November 4, 2026",
    laws: [
      { state: "Saint-Pierre-et-Miquelon", covers: "Territorial Council (Conseil territorial)", threshold: "",
        rule: "Sessions are public, at least once a quarter; anyone may ask for the deliberations and minutes (procès-verbaux) of public sessions, which the council publishes (Code général des collectivités territoriales, book IV). No requirement to record or stream was found." },
      { state: "Saint-Pierre-et-Miquelon", covers: "Schools (Service de l'Éducation nationale, French state)", threshold: "",
        rule: "Schools are run by the French state's education office, which reports to the Académie de Normandie and holds no public meetings." }
    ],
    note: "Saint-Pierre-et-Miquelon has no elected school board; its schools are run by the French state."
  },
  // United Kingdom: councils (no elected school boards).
  uk: {
    checked: "November 4, 2026",
    laws: [
      { state: "England", covers: "Council and committee meetings", threshold: "",
        rule: "Anyone may film, photograph, record or report public meetings (Openness of Local Government Bodies Regulations 2014). Councils don't have to broadcast them, though many webcast." },
      { state: "Wales", covers: "Principal councils", threshold: "",
        rule: "Full council meetings must be broadcast electronically while they happen (Local Government and Elections (Wales) Act 2021)." },
      { state: "Scotland", covers: "Councils", threshold: "",
        rule: "Meetings are open to the public with papers published (Local Government (Scotland) Act 1973); no requirement to record or broadcast was found, though most councils webcast." },
      { state: "Northern Ireland", covers: "Education Authority board", threshold: "",
        rule: "Not a council; it publishes board papers and minutes. No requirement to record or broadcast was found." }
    ],
    note: "The UK has no elected school boards: councils (and Northern Ireland's Education Authority) run state schools. These are the rules for their meetings; check the current law before relying on them."
  },
  // Ireland: Education and Training Boards.
  ireland: {
    checked: "November 4, 2026",
    laws: [
      { state: "Ireland", covers: "Education and Training Boards", threshold: "",
        rule: "Each ETB board (councillors, staff and parent representatives and community members) meets in public under the Education and Training Boards Act 2013 and publishes minutes; no requirement to record or stream meetings was found." }
    ],
    note: "ETBs run some of Ireland's schools; most are run by other patron bodies (often religious), which have no public board meetings."
  },
  // The Nordic countries and the Netherlands: municipal councils and their committees.
  norway: {
    checked: "November 4, 2026",
    laws: [
      { state: "Norway", covers: "Municipal councils and committees", threshold: "",
        rule: "Meetings of elected municipal bodies, committees included, are open to the public unless an item is closed by law (Local Government Act 2018, section 11-5). No requirement to record or stream was found, though most councils stream their council meetings." }
    ],
    note: "Norwegian municipalities run primary and lower secondary schools through their council and committees. Check the current law before relying on this."
  },
  sweden: {
    checked: "November 4, 2026",
    laws: [
      { state: "Sweden", covers: "Municipal councils", threshold: "",
        rule: "Council (kommunfullmäktige) meetings are public (Local Government Act 2017:725, chapter 5, section 38); many councils stream them, but no requirement to was found." },
      { state: "Sweden", covers: "Municipal boards (nämnder), including education boards", threshold: "",
        rule: "Board meetings are held behind closed doors unless the board decides to open them (chapter 6, section 25), so education boards' meetings are rarely public or recorded." }
    ],
    note: "Swedish municipalities run their schools through an education board (nämnd). Check the current law before relying on this."
  },
  finland: {
    checked: "November 4, 2026",
    laws: [
      { state: "Finland", covers: "Municipal councils", threshold: "",
        rule: "Council (valtuusto) meetings are public (Local Government Act 410/2015, section 101); many councils stream them, but no requirement to was found." },
      { state: "Finland", covers: "Committees, including education committees", threshold: "",
        rule: "Other bodies' meetings, such as the education committee (sivistyslautakunta), are closed unless the body decides to open them (section 101), so they're rarely public or recorded." }
    ],
    note: "Finnish municipalities run comprehensive schools through their council and education committee. Check the current law before relying on this."
  },
  denmark: {
    checked: "November 4, 2026",
    laws: [
      { state: "Denmark", covers: "Municipal councils", threshold: "",
        rule: "Council (kommunalbestyrelse) meetings are public (Local Government Act, section 10); many councils stream them, but no requirement to was found." },
      { state: "Denmark", covers: "Standing committees, including children and schools committees", threshold: "",
        rule: "Committee meetings are held behind closed doors (Local Government Act, section 20), so they aren't public or recorded; their minutes are published." }
    ],
    note: "Danish municipalities run their public schools (folkeskoler) through the council and its committees. Check the current law before relying on this."
  },
  netherlands: {
    checked: "November 4, 2026",
    laws: [
      { state: "Netherlands", covers: "Municipal councils and council committees", threshold: "",
        rule: "Council meetings are public (Municipalities Act, article 23), and so are most council committee meetings; no requirement to record or stream was found, though nearly all councils webcast on their own sites." },
      { state: "Netherlands", covers: "School boards (schoolbesturen)", threshold: "",
        rule: "Schools are run by school boards (foundations or associations, public and private), which aren't elected and have no duty to hold public meetings." }
    ],
    note: "Dutch municipalities fund school buildings and set local education policy, but don't run schools. Check the current law before relying on this."
  }
};
