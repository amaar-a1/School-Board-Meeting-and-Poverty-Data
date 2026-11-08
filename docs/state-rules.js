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
  },
  newzealand: {
    title: "Rules for school board meetings",
    checked: "November 4, 2026",
    laws: [
      { state: "New Zealand", covers: "School boards (one per school)", threshold: "",
        rule: "Board meetings are open to the public unless the board excludes them for an item (Local Government Official Information and Meetings Act 1987, which applies to school boards); no requirement to record or stream was found." }
    ],
    note: "Each New Zealand state school has its own elected board, so the site's areas aren't boards. Check the current law before relying on this."
  },
  germany: {
    title: "Rules for district council and school committee meetings",
    checked: "November 4, 2026",
    laws: [
      { state: "Germany", covers: "District councils (Kreistage) and city councils, and their school committees", threshold: "",
        rule: "Meetings are generally public under each state's local government law (Landkreisordnung, Gemeindeordnung); recording or streaming usually needs the council's rules to allow it and the members' consent, so few are streamed." }
    ],
    note: "German schools are run jointly: the state (Land) employs teachers and sets the curriculum, and the district or city (the Schulträger) builds and runs the schools. Check each state's law before relying on this."
  },
  islands: {
    title: "Rules for education ministry meetings",
    checked: "November 4, 2026",
    laws: [
      { state: "Islands and microstates", covers: "Education ministries and departments", threshold: "",
        rule: "Not checked for each island. Their schools are run by a government ministry or department, which doesn't hold public board meetings the way a US school board does." }
    ],
    note: "Rules for the islands' education bodies weren't researched; check each place's own law."
  },
  iceland: {
    title: "Rules for municipal council and committee meetings",
    checked: "November 4, 2026",
    laws: [
      { state: "Iceland", covers: "Municipal councils", threshold: "",
        rule: "Council meetings are open to the public (Local Government Act 138/2011); councils may broadcast them, and many do, but no requirement to was found." },
      { state: "Iceland", covers: "Committees, including education committees", threshold: "",
        rule: "Committee meetings are closed to the public; their minutes (fundargerðir) are published and go to the council for approval." }
    ],
    note: "Icelandic municipalities run compulsory schools through their council and an education committee. Check the current law before relying on this."
  },
  switzerland: {
    title: "Rules for cantonal parliament and school board meetings",
    checked: "November 5, 2026",
    laws: [
      { state: "Switzerland", covers: "Cantonal parliaments", threshold: "",
        rule: "Sittings are public under each canton's constitution and parliament law; many cantons stream them on their own websites, but there's no national requirement." },
      { state: "Switzerland", covers: "Municipal school boards (Schulpflege, Schulkommission)", threshold: "",
        rule: "Where they exist, their meetings are usually closed, under each canton's municipal and education law; decisions are published." }
    ],
    note: "Each canton sets its own rules for schools and their boards. Check the canton's law before relying on this."
  },
  chile: {
    title: "Rules for municipal council meetings",
    checked: "November 6, 2026",
    laws: [
      { state: "Chile", covers: "Municipal councils (concejos municipales)", threshold: "",
        rule: "Council sessions are public (Ley Orgánica Constitucional de Municipalidades, 18.695), and municipalities must publish their minutes under the transparency law (20.285); streaming isn't required, though many councils stream." },
      { state: "Chile", covers: "Local Public Education Services (SLEP)", threshold: "",
        rule: "Each SLEP has a local education council (Consejo Local de Educación Pública) of parents, students, teachers and others (Ley 21.040); no requirement to record or stream its meetings was found." }
    ],
    note: "Check the current law before relying on this."
  },
  brazil: {
    title: "Rules for municipal chamber (câmara municipal) meetings",
    checked: "November 6, 2026",
    laws: [
      { state: "Brazil", covers: "Municipal chambers (câmaras municipais)", threshold: "",
        rule: "Chamber sessions are public under each municipality's organic law (lei orgânica) and the Constitution's principle of publicity (art. 37); the Access to Information Law (Lei 12.527/2011) requires municipalities over 10,000 people to publish information online. No federal law requires sessions to be streamed, though many chambers do." },
      { state: "Brazil", covers: "Public schools", threshold: "",
        rule: "Under the education law (LDB, Lei 9.394/1996) municipalities offer early childhood education and, with the states, primary education; most have a municipal education council (conselho municipal de educação), an appointed body. Schools have their own school councils." }
    ],
    note: "Rules differ by municipality. Check its organic law and chamber's internal rules before relying on this."
  },
  spain: {
    title: "Rules for town council (pleno) meetings",
    checked: "November 6, 2026",
    laws: [
      { state: "Spain", covers: "Town councils (plenos de los ayuntamientos)", threshold: "",
        rule: "Plenary sessions are public under the Local Government Act (Ley 7/1985, art. 70), except for matters affecting people's honour or privacy; councils may broadcast them, and several autonomous communities' laws or many councils' own rules require it. Committee meetings (comisiones informativas) aren't public." },
      { state: "Spain", covers: "Public schools", threshold: "",
        rule: "Each autonomous community's education department runs public schools under the Education Act (LOE as amended by LOMLOE). Municipalities maintain infant and primary school buildings and can have a municipal school council (consejo escolar municipal); each school has an elected school council (consejo escolar)." }
    ],
    note: "Rules differ by autonomous community and council. Check the council's own rules (reglamento orgánico) before relying on this."
  },
  peru: {
    title: "Rules for district council (concejo municipal) meetings",
    checked: "November 6, 2026",
    laws: [
      { state: "Peru", covers: "District and provincial councils (concejos municipales)", threshold: "",
        rule: "Council sessions are public under the Organic Law of Municipalities (Ley 27972, art. 13), except for matters that could affect privacy or security; the Transparency Law (Ley 27806) requires agreements and ordinances to be published. No national law requires sessions to be streamed." },
      { state: "Peru", covers: "Public schools", threshold: "",
        rule: "Public schools are run by the regional governments' education directorates and their local units (UGEL) under the General Education Law (Ley 28044); districts have no school board. Each school has a council (CONEI) and a parents' association (APAFA)." }
    ],
    note: "Check the current law and the council's internal rules (reglamento interno del concejo) before relying on this."
  },
  france: {
    title: "Rules for town council (conseil municipal) meetings",
    checked: "November 7, 2026",
    laws: [
      { state: "France", covers: "Town councils (conseils municipaux)", threshold: "",
        rule: "Council meetings are public under the General Code of Local Authorities (Code général des collectivités territoriales, art. L2121-18), and may be broadcast by audiovisual means; the council can vote to sit in private (huis clos). Minutes and decisions must be published." },
      { state: "France", covers: "Nursery and primary schools", threshold: "",
        rule: "Communes own, build and maintain their écoles and employ their non-teaching staff (Code de l'éducation, art. L212-4 and following); the Ministry of Education employs the teachers. Each school has a school council (conseil d'école), which isn't public. Collèges are run by the départements and lycées by the regions." }
    ],
    note: "Check the current code and the council's own rules (règlement intérieur) before relying on this."
  },
  italy: {
    title: "Rules for town council (consiglio comunale) meetings",
    checked: "November 8, 2026",
    laws: [
      { state: "Italy", covers: "Town councils (consigli comunali)", threshold: "",
        rule: "Council sessions are public unless the council's own rules say otherwise for particular matters (Testo unico degli enti locali, D.Lgs. 267/2000, art. 38); each council's rules (regolamento del consiglio) set how sessions are recorded or streamed, and no national law requires streaming. Decisions must be published on the comune's online notice board (albo pretorio) under the transparency decree (D.Lgs. 33/2013)." },
      { state: "Italy", covers: "Schools", threshold: "",
        rule: "State schools are run by the Ministry of Education and its regional offices; comuni provide and maintain the buildings of nursery, primary and lower secondary schools (Law 23/1996). Each school has an elected school council (consiglio di istituto or di circolo)." }
    ],
    note: "Check the current law and the council's own rules before relying on this."
  },
  poland: {
    title: "Rules for council (rada gminy) sessions",
    checked: "November 8, 2026",
    laws: [
      { state: "Poland", covers: "Town councils (rady gmin, rady miejskie)", threshold: "",
        rule: "Council sessions are public (Act on Municipal Self-Government, art. 11b). Since 2018 sessions must be broadcast and recorded, and the recordings published in the public information bulletin (BIP) and on the council's website (art. 20 sec. 1b), and votes are recorded by name." },
      { state: "Poland", covers: "Schools", threshold: "",
        rule: "Gminy run nursery schools and primary schools (Education Law of 2016, art. 8 and 11); counties run most secondary schools. The state pays an education subsidy and the regional school superintendent (kurator oświaty) oversees teaching." }
    ],
    note: "Check the current law and the council's own rules (statut gminy) before relying on this."
  },
  japan: {
    title: "Rules for board of education (教育委員会) meetings",
    checked: "November 8, 2026",
    laws: [
      { state: "Japan", covers: "Municipal boards of education", threshold: "",
        rule: "Board meetings are public, though the board can close part of a meeting for personnel and other listed matters by a two-thirds vote; since the 2015 reform the board must try to prepare and publish minutes (Act on the Organization and Operation of Local Educational Administration, art. 14). The mayor and the board also meet in a general education council (総合教育会議), which isn't counted here." },
      { state: "Japan", covers: "Schools", threshold: "",
        rule: "Each municipality's board of education runs its public elementary and lower secondary schools; prefectures pay most teachers and run most high schools." }
    ],
    note: "Check the current law and the board's own rules before relying on this."
  },
  portugal: {
    title: "Rules for municipal assembly and council meetings",
    checked: "November 8, 2026",
    laws: [
      { state: "Portugal", covers: "Municipal assemblies and councils", threshold: "",
        rule: "Meetings of the municipal assembly are public, and the council (câmara municipal) holds at least one public meeting a month (Law 75/2013, art. 49); since 2021 sessions may be streamed, and many municipalities do so. Minutes are published." },
      { state: "Portugal", covers: "Schools", threshold: "",
        rule: "Since Decree-Law 21/2019, municipalities run school buildings, non-teaching staff, meals and transport for pre-school and basic education; the Ministry of Education employs teachers. Each municipality has an education council (conselho municipal de educação)." }
    ],
    note: "Check the current law and the municipality's own rules before relying on this."
  },
  belgium: {
    title: "Rules for town council (gemeenteraad / conseil communal) meetings",
    checked: "November 8, 2026",
    laws: [
      { state: "Belgium", covers: "Town councils", threshold: "",
        rule: "Council meetings are public, except for matters about individuals (Flanders: Decree on Local Government of 2017, art. 28; Wallonia: Code de la démocratie locale, art. L1122-20; Brussels: the New Municipal Law, art. 93). Flemish councils must make an audio or video recording or a detailed record of their meetings public since 2019; elsewhere many councils stream." },
      { state: "Belgium", covers: "Schools", threshold: "",
        rule: "Education is run by the language communities. Municipalities organise their own primary (and some secondary) schools in the official subsidised network, with the town council as the governing body; the communities and the free networks run the rest." }
    ],
    note: "Check the current law and the council's own rules before relying on this."
  },
  ecuador: {
    title: "Rules for cantonal council (concejo municipal) meetings",
    checked: "November 7, 2026",
    laws: [
      { state: "Ecuador", covers: "Cantonal councils (concejos municipales of the GADs)", threshold: "",
        rule: "Council sessions are public under the Organic Code of Territorial Organization (COOTAD, art. 318), with ordinary sessions at least weekly, and citizens may take part through the 'silla vacía'; the Transparency Law (LOTAIP) requires councils' acts to be published. No national law requires sessions to be streamed." },
      { state: "Ecuador", covers: "Public schools", threshold: "",
        rule: "Public schools are run by the Ministry of Education through its zones and districts under the Organic Law of Intercultural Education (LOEI); cantons have no school board. Each school has a school government (gobierno escolar)." }
    ],
    note: "Check the current law and the council's own rules before relying on this."
  },
  mexico: {
    title: "Rules for town council (cabildo) meetings",
    checked: "November 6, 2026",
    laws: [
      { state: "Mexico", covers: "Town councils (cabildos / ayuntamientos)", threshold: "",
        rule: "Cabildo sessions are public under each state's municipal law (ley orgánica municipal), with closed sessions allowed for listed matters; the General Transparency Law requires minutes and agreements to be published. Several states require sessions to be streamed online; others don't." },
      { state: "Mexico", covers: "Public schools", threshold: "",
        rule: "Basic education is run by each state's education authority under the General Education Law; municipalities have no school board. Schools' parent bodies (Consejos de Participación Escolar) meet at school level." }
    ],
    note: "Rules differ by state. Check the state's municipal law before relying on this."
  },
  colombia: {
    title: "Rules for municipal council meetings",
    checked: "November 6, 2026",
    laws: [
      { state: "Colombia", covers: "Municipal councils (concejos municipales)", threshold: "",
        rule: "Council sessions are public (Ley 136 de 1994); many councils broadcast them on local TV, Facebook or YouTube, but no national requirement to stream was found." }
    ],
    note: "Schools are run by certified territorial entities (departments, districts and larger municipalities). Check the current law before relying on this."
  }
};
