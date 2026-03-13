from flask import Flask, render_template, request, redirect, session
import random

app = Flask(__name__)
app.secret_key = "estrack_exam_secret"

PASS_THRESHOLD = 0.8

questions = [

{
"question":"The correct workstation startup command is:",
"options":[
"ssh -x stc@sce25 startupws.sh",
"ssh -x stc@sce25 > startupws.sh",
"ssh stc@sce25 -x > startupws.sh",
"startupws.sh | ssh -x stc@sce25"
],
"correct":"ssh -x stc@sce25 > startupws.sh",
"explanation":"This is the only correct syntax."
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
"question":"Carrier Loop Level (025) most directly reflects:",
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
"question":"Estimated Es/No (085) measures:",
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
"question":"Stable AGC with falling Es/No indicates:",
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
"question":"Actual Intermediate Frequency (004) displays:",
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
"question":"Only one spacecraft visible during MSPA support. First action:",
"options":[
"Change SPAN bandwidth",
"Change ADLS input",
"Check mission schedule and PPCP",
"Enable coherency"
],
"correct":"Check mission schedule and PPCP",
"explanation":"During Multiple Spacecraft Per Aperture support, the station is configured to receive telemetry for a maximum of 4 spacecraft, however we might start tracking one spacecraft hours later than another spacecraft. Always check PPCP."
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
"DCU diversity combiner",
"TMUB"
],
"correct":"DCU diversity combiner",
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
"GMD only",
"RCD",
"TMUA",
"ADLS"
],
"correct":"RCD",
"explanation":"RCD stands for Remnant Carrier. Tone ranging works only with Remnant Carrier."
},

{
"question":"Pseudo-noise ranging operates with:",
"options":[
"RCD only",
"GMD only",
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
"Ask mission to repulse DMD",
"Switch to coherent"
],
"correct":"Ask mission to repulse DMD",
"explanation":"If telemetry degrades but the carrier remains, the demodulator may require a repulse to recover the lock. Additionally, you can repulse the Decoder as well, but only after the DMD has locked."
},

{
"question":"Re-sweep is more justified when:",
"options":[
"Deep space apogee",
"Supporting polar missions with short EPD",
"During coherency",
"During ranging"
],
"correct":"Supporting polar missions with short EPD",
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
"question":"Telemetry intermittent and DMD repulse fails. Next action:",
"options":[
"Re-sweep",
"Recalculate downlink frequency",
"Increase power",
"Swap chain"
],
"correct":"Recalculate downlink frequency",
"explanation":"If repulsing the DMD doesn't restore lock, the demodulator might be configured with an outdated downlink frequency due to Doppler shift or spacecraft configuration change. In that case recalculate the downlink frequency. How to: Jobs → New Frequency Plan."
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

# ---------------- HOME ----------------

@app.route("/")
def index():
    return render_template("index.html")


# ---------------- START EXAM ----------------

@app.route("/start")
def start():

    session["questions"] = random.sample(questions, TOTAL_QUESTIONS)
    session["index"] = 0
    session["score"] = 0
    session["failed"] = []

    return redirect("/exam")


# ---------------- EXAM ----------------

@app.route("/exam", methods=["GET","POST"])
def exam():

    # if exam hasn't started
    if "questions" not in session:
        return redirect("/")

    if request.method == "POST":

        answer = request.form.get("answer")
        q = session["questions"][session["index"]]

        if answer == q["correct"]:
            session["score"] += 1
        else:
            session["failed"].append({
                "question": q["question"],
                "your": answer,
                "correct": q["correct"],
                "explanation": q["explanation"]
            })

        session["index"] += 1

    # exam finished
    if session["index"] >= TOTAL_QUESTIONS:
        return redirect("/result")

    q = session["questions"][session["index"]]

    options = q["options"].copy()
    random.shuffle(options)

    return render_template(
        "exam.html",
        number=session["index"] + 1,
        total=TOTAL_QUESTIONS,
        question=q["question"],
        options=options
    )


# ---------------- RESULT ----------------

@app.route("/result")
def result():

    if "score" not in session:
        return redirect("/")

    score = session["score"]
    failed = session["failed"]

    passed = score / TOTAL_QUESTIONS >= PASS_THRESHOLD

    return render_template(
        "result.html",
        score=score,
        total=TOTAL_QUESTIONS,
        passed=passed,
        failed=failed
    )


# ---------------- SERVER ----------------

if __name__ == "__main__":
    app.run()
