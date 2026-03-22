from flask import Flask, render_template, request, redirect, session
import random
from pathlib import Path
from itsdangerous import BadSignature, URLSafeSerializer

app = Flask(__name__)
app.secret_key = "estrack_exam_secret"

PASS_THRESHOLD = 0.8

questions = [

{
"question":"During EXMO support, which value continuously changes on the mimic due to ramping:",
"options":[
"BLF in GSRC pages",
"Measured BLF",
"Uplink frequency",
"Actual radiated frequency"
],
"correct":"Actual radiated frequency",
"explanation":"BLF in GSRC shows the frequency the S/C is nominally configured for (can't be up to date 24/7); measured BLF is the current frequency the S/C is expecting considering doppler shift; U/L frequency reflects the F at start uplink time (after initial doppler compensation); Actual radiated frequency shows the real time F radiated by the G/S (since ramping means continuously adjusting the F due to doppler shift, this value will change accordingly)."
},

{
"question":"During ranging calibration TTCP and DMD alarms occur because:",
"options":[
"Carrier loop instability",
"Uplink carrier without modulation",
"Es/No below threshold",
"Sweep not executed"
],
"correct":"Uplink carrier without modulation",
"explanation":"During ranging calibration the carrier is present without modulation."
},

{
"question":"Interrupting ranging calibration risks:",
"options":[
"Loss of spacecraft lock",
"Leaving subsystems in inconsistent configuration",
"Resetting uplink chain",
"Forcing re-sweep"
],
"correct":"Leaving subsystems in inconsistent configuration",
"explanation":"Stopping the procedure will leave subsystems in an inconsistent configuration, and a manual configuration will be required."
},

{
"question":"During pre-pass the carrier is visible but there is no modulation. Most likely:",
"options":[
"Sweep not executed",
"Idle pattern active",
"Ranging calibration ongoing",
"Coherency active"
],
"correct":"Ranging calibration ongoing",
"explanation":"During ranging calibration the signal loops inside the TTCP so the antenna is radiating (carrier up) but no modulation is applied."
},

{
"question":"Carrier Loop Level (used in chart configuration) most directly reflects:",
"options":[
"Signal-to-noise ratio",
"Received signal power",
"Doppler tracking accuracy",
"Baseband stability"
],
"correct":"Received signal power",
"explanation":"Carrier Loop Level is measured in dBm and measures the strength of the signal. Note: a negative value in dBm still corresponds to a positive value in Watts, just very low."
},

{
"question":"Estimated Es/No (used in chart configuration) measures:",
"options":[
"Carrier frequency offset",
"Signal quality",
"Radiated uplink stability",
"Diversity combining efficiency"
],
"correct":"Signal quality",
"explanation":"Es/No is the signal to noise ratio (SNR). It's the ratio between the signal received from the spacecraft and the noise produced by space background radiation (along with any other radio frequency source, space is vast and unknown)."
},

{
"question":"Stable AGC with increasing Es/No indicates:",
"options":[
"Carrier loss",
"Signal quality degradation",
"SPAN misconfiguration",
"Wrong intermediate frequency"
],
"correct":"Signal quality degradation",
"explanation":"Signal power remains stable but the noise level increases, degrading the signal-to-noise ratio."
},

{
"question":"Actual Intermediate Frequency (used in chart configuration) displays:",
"options":[
"Modulated carrier",
"Unmodulated carrier at 230 MHz",
"Doppler shift",
"Ranging tone"
],
"correct":"Unmodulated carrier at 230 MHz",
"explanation":"The IF monitor shows the carrier before modulation."
},

{
"question":"SPAN backend must be configured using:",
"options":[
"ULM radiated frequency",
"DMD average IF frequency",
"Carrier Loop Level",
"Estimated Es/No"
],
"correct":"DMD average IF frequency",
"explanation":"Backend Spectrum Analyser monitors the telemetry received from the spacecraft. It must therefore be configured using the IF frequency measured by the demodulator."
},

{
"question":"SPAN frontend must be configured using:",
"options":[
"ULM actual radiated frequency",
"DMD IF frequency",
"Carrier Loop Level",
"ADLS input"
],
"correct":"ULM actual radiated frequency",
"explanation":"Frontend spectrum analyser monitors the uplink radiation produced by the station."
},

{
"question":"Only one spacecraft visible in the spectrum analyser during MSPA support. Signal is expected from both according to PPCP. Solution:",
"options":[
"Change SPAN bandwidth",
"Change ADLS input",
"Check downlink frequency",
"Enable coherency"
],
"correct":"Change SPAN bandwidth",
"explanation":"For EXMO and MEX support (the only MSPA support at the moment), in oder to see both S/C you need at least 15 MHz of bandwidth"
},

{
"question":"Correct Kiruna uplink path:",
"options":[
"TCU → IFM1 → AULS → SSPA → Polarizer → Antenna",
"IFM1 → TCU → AULS → Polarizer → SSPA → Antenna",
"TCU → AULS → IFM1 → SSPA → Polarizer → Antenna",
"TCU → IFM1 → SSPA → AULS → Antenna → Polarizer"
],
"correct":"TCU → IFM1 → AULS → SSPA → Polarizer → Antenna",
"explanation":"TCU generates telecommands. IFM1 performs IF modulation. AULS (Antenna Uplink Switch) routes the signal. SSPA amplifies the signal. Polarizer prepares the signal before radiation. Antenna transmits to the spacecraft."
},

{
"question":"Kiruna S-band downlink path:",
"options":[
"SLNA → SDC → ADLS → CORTEX",
"SLNA → ADLS → SDC → CORTEX",
"SDC → SLNA → ADLS → CORTEX",
"SLNA → CORTEX → ADLS → SDC"
],
"correct":"SLNA → SDC → ADLS → CORTEX",
"explanation":"SLNA amplifies the weak signal received from the spacecraft. SDC performs the signal downconversion. ADLS routes the signal to the correct processing chain. CORTEX processes telemetry."
},

{
"question":"X-band support at Kiruna exists:",
"options":[
"For all spacecraft",
"Only when ADLS configured",
"Only for Cryosat",
"When IFR4 active"
],
"correct":"Only for Cryosat",
"explanation":"Cryosat is the only spacecraft currently configured for X-band support. Indeed it has a dedicated chain called CHRD (Cryosat High Rate Demodulator). It has a prime and a backup (CHRD1 and CHRD2)."
},

{
"question":"IFR2 + IFR3 correspond to:",
"options":[
"RAU",
"TMUA",
"DCU (diversity combiner unit)",
"TMUB"
],
"correct":"DCU (diversity combiner unit)",
"explanation":"IFR2 and IFR3 correspond to the DCU (Diversity Combiner Unit) which combines TMUA and TMUB chains. TMUA = low bit rate. TMUB = high bit rate."
},

{
"question":"Baseband swap is justified when:",
"options":[
"Display freeze",
"Prime chain failure",
"Es/No fluctuation",
"Weak SPAN signal"
],
"correct":"Prime chain failure",
"explanation":"It is ok to try to troubleshoot and fix the current chain, however the priority is to provide support to the spacecraft. Unless it's easily fixable, do swap first and then take all the time to investigate properly. Last but not least, inform onsite maintenance team."
},

{
"question":"Tone ranging operates with:",
"options":[
"GMD (suppressed carrier)",
"RCD (remnant carrier)",
"TMUA",
"ADLS"
],
"correct":"RCD (remnant carrier)",
"explanation":"RCD stands for Remnant Carrier. Tone ranging works only with Remnant Carrier."
},

{
"question":"Pseudo-noise ranging operates with:",
"options":[
"RCD (remnant carrier)",
"GMD (suppressed carrier)",
"RCD and GMD",
"RAU"
],
"correct":"RCD and GMD",
"explanation":"Pseudo noise ranging works with both Remnant Carrier (RCD) and Suppressed Carrier (GMD)."
},

{
"question":"Sweep is performed to:",
"options":[
"Increase transmit power",
"Improve spacecraft receiver lock",
"Stabilize AGC",
"Calibrate delay"
],
"correct":"Improve spacecraft receiver lock",
"explanation":"Sweep transmits the uplink across a wider frequency range, past the spacecraft margin of error, to help the spacecraft receiver acquire and lock onto the signal."
},

{
"question":"Telemetry degrades but carrier remains. First action:",
"options":[
"Re-sweep",
"Increase power",
"Repulse DMD",
"Stop uplink + Start uplink"
],
"correct":"Repulse DMD",
"explanation":"If telemetry degrades but the carrier remains, the demodulator may require a repulse to recover the lock. Additionally, you can repulse the Decoder as well, but only after the DMD has locked."
},

{
"question":"Re-sweep is more justified is one of the following cases:",
"options":[
"Deep space apogee",
"Supporting polar missions",
"During coherency",
"During ranging"
],
"correct":"Supporting polar missions",
"explanation":"Re-Sweep takes as long as the propagation delay to be confirmed (signal must reach the spacecraft and come back). For deep space support the EPD can be 15 minutes up to 1 hour, which would waste a large portion of the pass. Polar missions are much closer and confirmation takes only seconds."
},

{
"question":"In coherent mode downlink frequency is:",
"options":[
"Generated onboard",
"Derived from uplink signal",
"Controlled by ADLS",
"Set by SPAN"
],
"correct":"Derived from uplink signal",
"explanation":"In 2-way (Coherent) mode, the ground station transmits using its oscillator frequency, and the spacecraft converts the received frequency into its own transmission frequency."
},

{
"question":"Telemetry intermittent and DMD repulse fails. Next actions:",
"options":[
"Stop uplink/start uplink + re-sweep + recalculate uplink frequency",
"Recalculate downlink frequency + check TM rate + stop track/start track",
"Increase power + repulse decoder + check doppler compensation",
"Swap chain + reconfigure station manually"
],
"correct":"Recalculate downlink frequency + check TM rate + stop track/start track",
"explanation":"If repulsing the DMD doesn't restore lock, the demodulator might be configured with an outdated downlink frequency (How to: Jobs → New Frequency Plan); also check that S/C TM rate matches G/S TM rate (call mission on the voice loop); the job Start Track automatically recalculates the downlink frequency"
},

{
"question":"Radiation inhibited at 8° elevation during deep space support:",
"options":[
"RF Mute Deep Space profile",
"Inhibitor",
"Polarizer fault",
"SSPA disabled"
],
"correct":"RF Mute Deep Space profile",
"explanation":"The Deep Space RF Mute profile prevents radiation below 10° elevation."
},

{
"question":"What are Service Instances?",
"options":[
"Configuration files for return and forward sessions",
"Backup TTCP configurations",
"Spectrum analyser profiles",
"RF safety configurations"
],
"correct":"Configuration files for return and forward sessions",
"explanation":"Service Instances are configuration files that instruct the return session (links with mission) and the forward session (connection point for CLTU) about what spacecraft and what parameters to operate."
}

]

TOTAL_QUESTIONS = len(questions)

exam_state_serializer = URLSafeSerializer(app.secret_key, salt="exam-state")
LEADERBOARD_FILE = Path(__file__).with_name("leaderboard.txt")


def _encode_state(state):
    return exam_state_serializer.dumps(state)


def _decode_state(token):
    try:
        data = exam_state_serializer.loads(token)
    except BadSignature:
        return None

    if not isinstance(data, dict):
        return None

    order = data.get("order")
    idx = data.get("index")
    score = data.get("score")
    failed = data.get("failed")

    if not isinstance(order, list) or len(order) != TOTAL_QUESTIONS:
        return None
    if sorted(order) != list(range(TOTAL_QUESTIONS)):
        return None
    if not isinstance(idx, int) or idx < 0 or idx > TOTAL_QUESTIONS:
        return None
    if not isinstance(score, int) or score < 0 or score > TOTAL_QUESTIONS:
        return None
    if not isinstance(failed, list):
        return None

    return data


def _save_state_to_session(state):
    # Lightweight fallback for clients/proxies that drop hidden token values.
    session["exam_state"] = state


def _load_state_from_session():
    state = session.get("exam_state")
    if not isinstance(state, dict):
        return None

    order = state.get("order")
    idx = state.get("index")
    score = state.get("score")
    failed = state.get("failed")

    if not isinstance(order, list) or len(order) != TOTAL_QUESTIONS:
        return None
    if sorted(order) != list(range(TOTAL_QUESTIONS)):
        return None
    if not isinstance(idx, int) or idx < 0 or idx > TOTAL_QUESTIONS:
        return None
    if not isinstance(score, int) or score < 0 or score > TOTAL_QUESTIONS:
        return None
    if not isinstance(failed, list):
        return None

    return state


def _expand_failed(failed_compact):
    failed = []
    for item in failed_compact:
        q_idx = item.get("question_idx")
        if not isinstance(q_idx, int) or not (0 <= q_idx < TOTAL_QUESTIONS):
            continue
        q = questions[q_idx]
        failed.append({
            "question": q["question"],
            "your": item.get("your"),
            "correct": q["correct"],
            "explanation": q["explanation"],
        })
    return failed


def _load_leaderboard():
    leaderboard = []
    try:
        with LEADERBOARD_FILE.open("r", encoding="utf-8") as f:
            for line in f:
                raw = line.rstrip("\n")
                if not raw:
                    continue

                # Current format: name|score
                if "|" in raw:
                    name, score_str = raw.split("|", 1)
                # Legacy format support: Name — 20 / 25
                elif "—" in raw and "/" in raw:
                    name, score_str = raw.split("—", 1)
                    score_str = score_str.split("/", 1)[0]
                else:
                    continue

                name = name.strip()
                try:
                    score = int(score_str.strip())
                except ValueError:
                    continue

                leaderboard.append((name, score))
    except FileNotFoundError:
        return []

    leaderboard.sort(key=lambda item: item[1], reverse=True)
    return leaderboard[:20]


def _save_leaderboard_entry(name, score):
    safe_name = " ".join((name or "").strip().split())[:50]
    if not safe_name:
        return
    with LEADERBOARD_FILE.open("a", encoding="utf-8") as f:
        f.write(f"{safe_name}|{score}\n")


def _render_exam_from_state(state):
    q_idx = state["order"][state["index"]]
    q = questions[q_idx]
    options = q["options"].copy()
    random.shuffle(options)

    return render_template(
        "exam.html",
        state_token=_encode_state(state),
        number=state["index"] + 1,
        total=TOTAL_QUESTIONS,
        question=q["question"],
        options=options,
    )


def _render_result_from_state(state):
    score = state["score"]
    failed = _expand_failed(state["failed"])
    passed = score / TOTAL_QUESTIONS >= PASS_THRESHOLD

    return render_template(
        "result.html",
        result_token=_encode_state(state),
        score=score,
        total=TOTAL_QUESTIONS,
        passed=passed,
        failed=failed,
        leaderboard=_load_leaderboard(),
    )


# ---------------- HOME ----------------

@app.route("/")
def index():
    return render_template("index.html")


def _advance_exam(token, answer):
    state = _decode_state(token) if token else None
    if state is None:
        state = _load_state_from_session()
    if state is None or state["index"] >= TOTAL_QUESTIONS:
        return redirect("/start")

    q_idx = state["order"][state["index"]]
    q = questions[q_idx]

    if answer == q["correct"]:
        state["score"] += 1
    else:
        state["failed"].append({"question_idx": q_idx, "your": answer})

    state["index"] += 1
    _save_state_to_session(state)

    if state["index"] >= TOTAL_QUESTIONS:
        return _render_result_from_state(state)

    return _render_exam_from_state(state)


# ---------------- START EXAM ----------------

@app.route("/start", methods=["GET", "POST"])
def start():
    # Support legacy templates that POST answers back to /start (no explicit action).
    if request.method == "POST":
        token = request.form.get("state_token") or request.args.get("state_token", "")
        answer = request.form.get("answer") or request.args.get("answer")
        return _advance_exam(token, answer)

    state = {
        "order": random.sample(range(TOTAL_QUESTIONS), TOTAL_QUESTIONS),
        "index": 0,
        "score": 0,
        "failed": [],
    }
    _save_state_to_session(state)
    return _render_exam_from_state(state)


# ---------------- EXAM ----------------

@app.route("/exam", methods=["GET", "POST"])
def exam():
    token = request.form.get("state_token") or request.args.get("state_token", "")
    answer = request.form.get("answer") or request.args.get("answer")
    # Accept both GET and POST so accidental GET form submissions do not reset flow.
    return _advance_exam(token, answer)


# ---------------- RESULT ----------------

@app.route("/result", methods=["POST"])
def result():
    token = request.form.get("result_token", "")
    state = _decode_state(token) if token else None
    if state is None:
        state = _load_state_from_session()
    if state is None or state["index"] < TOTAL_QUESTIONS:
        return redirect("/")

    name = request.form.get("name", "")
    _save_leaderboard_entry(name, state["score"])
    return _render_result_from_state(state)


if __name__ == "__main__":
    app.run()
