import { ArrowLeft, ArrowRight, BookOpen } from "lucide-react";
import "./help.css";

const sections = [
  ["purpose", "What it does"],
  ["first-case", "Your first investigation"],
  ["read-results", "Understand the results"],
  ["next-step", "Find the next step"],
  ["request", "Reports & reviewed requests"],
  ["coverage", "Live data & limitations"],
  ["questions", "Common questions"],
];

export function HowItWorks({
  signedIn,
  canWrite,
  busy,
  onTraining,
  onReturn,
}: {
  signedIn: boolean;
  canWrite: boolean;
  busy: boolean;
  onTraining: () => void;
  onReturn: () => void;
}) {
  return (
    <div className="help-page">
      <div className="page-heading">
        <div>
          <span className="eyebrow">A PRACTICAL GUIDE</span>
          <h1>How TraceSetu works</h1>
          <p>
            From a wallet address to a supported next step. No blockchain
            expertise needed to get started.
          </p>
        </div>
        <button className="button" onClick={onReturn}>
          <ArrowLeft size={15} />
          {signedIn ? "Back to workspace" : "Back to sign in"}
        </button>
      </div>
      <div className="help-layout">
        <nav className="help-contents" aria-label="Guide contents">
          <span className="eyebrow">IN THIS GUIDE</span>
          {sections.map(([id, title], i) => (
            <a key={id} href={`#guide-${id}`}>
              <span>{String(i + 1).padStart(2, "0")}</span>
              {title}
            </a>
          ))}
          <p>
            First time here? Read the overview, then try a clearly labelled
            training case.
          </p>
        </nav>
        <div className="help-article">
          <section id="guide-purpose" aria-labelledby="guide-purpose-title">
            <span className="eyebrow">01 / THE PURPOSE</span>
            <h2 id="guide-purpose-title">
              Find where the trail reaches a service.
            </h2>
            <p>
              You have a cryptocurrency wallet address. You want to understand
              where its funds went and whether the trail reaches an exchange or
              a custodial wallet provider. These businesses are called{" "}
              <strong>Virtual Asset Service Providers, or VASPs</strong>.
            </p>
            <p>
              TraceSetu follows recorded transfers, checks the available
              service labels and identifies the{" "}
              <strong>first supported receiving service on each path</strong>.
              It keeps the evidence and missing information beside the result so
              an investigator can decide what to check or request next.
            </p>
            <figure className="help-example">
              <figcaption>
                Illustration only — not a real transaction
              </figcaption>
              <ol aria-label="Example fund movement">
                <li>
                  <strong>Reported wallet</strong>
                  <span>Your starting address</span>
                </li>
                <li>
                  <strong>Another wallet</strong>
                  <span>An intermediate transfer</span>
                </li>
                <li>
                  <strong>Supported service</strong>
                  <span>First custody boundary</span>
                </li>
              </ol>
              <p>
                A shorter path is “nearer” only within the history and labels
                available. Missing information may hide a closer service.
              </p>
            </figure>
            <p>
              <strong>What you get:</strong> a transfer graph, source-backed
              findings, visible gaps, an evidence report and a reviewed request
              package when the required evidence and recipient are available.
            </p>
            <div className="help-note">
              <strong>What the result does not tell you</strong>
              <p>
                A wallet address does not identify its owner. This app cannot
                reveal a customer’s identity, recover funds or freeze assets by
                itself. Official SAHYOG is not connected in this installation.
              </p>
            </div>
          </section>

          <section
            id="guide-first-case"
            aria-labelledby="guide-first-case-title"
          >
            <span className="eyebrow">02 / GET STARTED</span>
            <h2 id="guide-first-case-title">Run your first investigation.</h2>
            <div className="help-start">
              <BookOpen size={20} />
              <div>
                <strong>The easiest way to learn</strong>
                <p>
                  Open a training case. It creates a separate case with invented
                  wallets, transfers and services so you can explore the full
                  workflow. It is always marked{" "}
                  <strong>SYNTHETIC TRAINING</strong>.
                </p>
                {signedIn && canWrite ? (
                  <button
                    className="button primary small"
                    disabled={busy}
                    onClick={onTraining}
                  >
                    Open a training case <ArrowRight size={14} />
                  </button>
                ) : (
                  <p className="muted">
                    {signedIn
                      ? "As a reviewer, open a case shared with you. An investigator can create the training case."
                      : "Sign in with your issued account, then choose Open training case in Investigations."}
                  </p>
                )}
              </div>
            </div>
            <p>
              For a wallet you need to investigate, use these steps instead:
            </p>
            <ol className="help-steps">
              <li>
                <strong>Create the case.</strong>
                <p>
                  In <b>Investigations</b>, choose <b>New investigation</b>. Add
                  a title, your case reference and a description. Add the
                  colleague who will review evidence or requests as a case
                  member.
                </p>
              </li>
              <li>
                <strong>Choose the input.</strong>
                <p>
                  Open the case and select <b>Analyse wallet</b>. Choose the
                  blockchain, paste the wallet address and set the start and end
                  times in <b>UTC</b>. The same-looking address on another
                  blockchain is a different subject.
                </p>
              </li>
              <li>
                <strong>Choose the evidence mode.</strong>
                <p>
                  <b>Live provider acquisition</b> fetches real data from a
                  configured provider. <b>Imported evidence snapshot</b>{" "}
                  analyses a previously imported, structured snapshot.{" "}
                  <b>Synthetic training scenario</b> uses invented data. These
                  modes stay visibly separate.
                </p>
              </li>
              <li>
                <strong>Set the bounds and submit.</strong>
                <p>
                  <b>Maximum custody hops</b> limits how far the trace can go.{" "}
                  <b>Maximum provider requests</b> limits how many data requests
                  a run may make. Larger limits can take longer; they do not
                  guarantee an answer. Submit the form and wait for the job to
                  finish.
                </p>
              </li>
              <li>
                <strong>Read the answer and its gaps.</strong>
                <p>
                  Start with <b>Overview</b>. Inspect the first supported
                  service, if one exists, then check its evidence and the
                  unresolved branches. Use <b>Evidence</b> to read exact
                  transfer amounts and the limits of the result.
                </p>
              </li>
            </ol>
            <p className="help-footnote">
              An investigator creates and analyses cases. A reviewer checks
              submissions shared with them and cannot approve their own
              submission. An administrator also manages access. Buttons reflect
              your role and case permissions.
            </p>
          </section>

          <section
            id="guide-read-results"
            aria-labelledby="guide-results-title"
          >
            <span className="eyebrow">03 / READ THE ANSWER</span>
            <h2 id="guide-results-title">What each result means.</h2>
            <dl className="help-definitions">
              <div>
                <dt>First supported receiving service</dt>
                <dd>
                  A service named by the available evidence on a reachable path.
                  Click <b>Inspect evidence</b> to see who supplied the label
                  and its evidence grade. A service label and acceptance of
                  direct deposits are separate claims.
                </dd>
              </div>
              <div>
                <dt>No service identified yet</dt>
                <dd>
                  No supported service attribution was found in this analysis.
                  The wallet could still belong to a service. This does not mean
                  self-custody, low risk or no relevant activity.
                </dd>
              </div>
              <div>
                <dt>Custody paths and hops</dt>
                <dd>
                  A path is a route through the observed transfers. A hop is a
                  step along that route. Multiple paths may reach the same
                  service; the path count is not the number of different
                  exchanges.
                </dd>
              </div>
              <div>
                <dt>Unresolved branches</dt>
                <dd>
                  Parts of the trail that need more history, a trustworthy label
                  or protocol evidence. A hop or request limit can also stop the
                  trace. These are leads for the next check.
                </dd>
              </div>
              <div>
                <dt>Nearestness certificate</dt>
                <dd>
                  A statement of what “nearest” is supported by this bounded
                  snapshot. “Established” for a known target does not prove that
                  no closer, unlabelled service exists.
                </dd>
              </div>
              <div>
                <dt>Evidence grades and risk signals</dt>
                <dd>
                  Provider claims, hypotheses and reviewed assertions are shown
                  separately. Risk signals cite their source; <b>Unassessed</b>{" "}
                  means there is not enough evidence to assess risk. There is no
                  validated percentage confidence score.
                </dd>
              </div>
              <div>
                <dt>Completed with gaps</dt>
                <dd>
                  The run has finished, but some paths or data remain
                  incomplete. Read the stated reason. A finished job is not a
                  complete picture of the blockchain.
                </dd>
              </div>
            </dl>
            <h3>Read the graph</h3>
            <p>
              The dark circle is the reported wallet. Other nodes represent
              wallets, service assertions or Bitcoin transactions. Arrows show
              observed movement; select a wallet or transfer to open its
              evidence drawer. Use <b>+</b>, <b>−</b> and <b>Fit graph</b> to
              explore. The <b>Evidence</b> table provides the amounts and
              transaction references in text.
            </p>
            <p>
              Observed amounts are not automatically the amount of stolen money.
              In Bitcoin, a transaction can combine several inputs and create
              several outputs. Dashed links show possible exposure, not a proven
              allocation from one input to one output.
            </p>
          </section>

          <section id="guide-next-step" aria-labelledby="guide-next-title">
            <span className="eyebrow">04 / FOLLOW UP</span>
            <h2 id="guide-next-title">
              Check the answer. Then choose the next query.
            </h2>
            <ol className="help-steps">
              <li>
                <strong>Challenge a source.</strong>
                <p>
                  Choose <b>Challenge source</b> in the evidence drawer, or open{" "}
                  <b>Assumptions</b>. The app recomputes the answer without that
                  source family. If a finding disappears, you know what it
                  depended on. The original evidence is preserved.
                </p>
              </li>
              <li>
                <strong>Plan within a budget.</strong>
                <p>
                  In Overview, select <b>Plan within a request budget</b>, enter
                  a limit and save. The app prioritises missing evidence,
                  including gaps closer to the reported wallet. Planning alone
                  does not fetch anything, and request estimates are not a
                  quoted provider price.
                </p>
              </li>
              <li>
                <strong>Run the selected queries.</strong>
                <p>
                  When eligible queries are available, choose{" "}
                  <b>Execute selected queries</b>, review the scopes, then{" "}
                  <b>Start selected queries</b>. A new result preserves the
                  parent analysis. In training, the button says{" "}
                  <b>Execute training expansion</b> and uses synthetic data with
                  zero provider calls.
                </p>
              </li>
              <li>
                <strong>Use the right update action.</strong>
                <p>
                  <b>Refresh live data</b> acquires current provider data in a
                  new run using the existing bounds.{" "}
                  <b>Reassess recorded evidence</b> uses already recorded
                  transfers and newly reviewed evidence; it is not a fresh
                  blockchain fetch. Neither action overwrites the earlier
                  analysis.
                </p>
              </li>
            </ol>
            <h3>When funds cross a chain or enter a mixer</h3>
            <p>
              The app needs protocol evidence to connect different chains. The
              current training workflow supports reviewed CCTP V2 USDC proofs
              between Ethereum and Polygon. Use <b>Review a bridge case</b> to
              practise proof submission, separate review and reassessment.
              Unsupported bridges, swaps and mixer paths stay unresolved; the
              app does not guess their exits.
            </p>
          </section>

          <section id="guide-request" aria-labelledby="guide-request-title">
            <span className="eyebrow">05 / PRESERVE & ACT</span>
            <h2 id="guide-request-title">
              Take the evidence to a reviewed next step.
            </h2>
            <ol className="help-steps">
              <li>
                <strong>Export and check the evidence.</strong>
                <p>
                  Use <b>Report</b> for the investigation PDF or{" "}
                  <b>Evidence → Signed evidence bundle</b> for the portable
                  package. In <b>Verify evidence</b>, upload that ZIP and choose{" "}
                  <b>Verify bundle</b>. A successful result checks file
                  integrity and replays the analysis. It does not prove the
                  ownership labels are true.
                </p>
              </li>
              <li>
                <strong>Establish the recipient.</strong>
                <p>
                  In <b>VASP directory</b>, an investigator proposes the exact
                  service entity, jurisdiction and contact channel with a
                  verification source. A separate reviewer checks and approves
                  the entry. The directory entry must be current and match the
                  candidate.
                </p>
              </li>
              <li>
                <strong>Prepare and review the request.</strong>
                <p>
                  In the case’s <b>Requests</b> tab, choose{" "}
                  <b>Prepare request</b>. Select the supported candidate,
                  verified recipient, request type, legal basis and scope. A
                  different authorised reviewer approves that exact payload
                  before export.
                </p>
              </li>
              <li>
                <strong>Keep responses and corrections attached.</strong>
                <p>
                  Supported signed responses can be imported for independent
                  review. Approved corrections or evidence withdrawals may
                  invalidate old findings; reassess before exporting affected
                  reports or requests.
                </p>
              </li>
            </ol>
            <div className="help-note">
              <strong>An export is not a sent notice.</strong>
              <p>
                This installation produces <b>NOT_SENT / NOT_CONNECTED</b>{" "}
                packages. Official SAHYOG delivery, VASP acceptance and any
                freezing action require the appropriate external access and
                authorised process.
              </p>
            </div>
            <p>
              <b>Monitoring</b> can schedule bounded live checks while this
              installation runs. Changes appear as case alerts.{" "}
              <b>Audit trail</b> shows recorded case activity, including
              evidence and review actions.
            </p>
          </section>

          <section id="guide-coverage" aria-labelledby="guide-coverage-title">
            <span className="eyebrow">06 / KNOW THE COVERAGE</span>
            <h2 id="guide-coverage-title">
              Live, imported and training are different.
            </h2>
            <div className="help-modes">
              <div>
                <h3>Live acquisition</h3>
                <p>
                  Real provider requests. Read the source and retrieval time in
                  the live-data strip. A bounded public Bitcoin sample, refresh
                  and evidence verification have passed here. This is on-demand
                  acquisition, not a continuous stream.
                </p>
              </div>
              <div>
                <h3>Imported snapshot</h3>
                <p>
                  A fixed set of previously acquired evidence. It is useful for
                  replay and review. Upload the app’s structured snapshot format
                  through <b>Evidence → Import snapshot</b>; an arbitrary
                  screenshot or explorer CSV is not that format.
                </p>
              </div>
              <div>
                <h3>Synthetic training</h3>
                <p>
                  Invented transactions and labels for learning the complete
                  workflow. It does not prove that a real wallet belongs to a
                  named exchange. Training and operational evidence must remain
                  separate.
                </p>
              </div>
            </div>
            <p>
              Bitcoin, Ethereum, Tron, BNB Chain, Solana and Polygon adapters
              are implemented. Broader live wallet coverage and ownership
              validation remain incomplete. Some providers need API credentials
              or endpoint access. Open <b>Data & coverage</b> to check
              configuration and limitations before presenting a result.
            </p>
            <p>
              A live-provider failure stays visible. The app never silently
              substitutes training data. In the existing <b>LIVE-BTC</b>{" "}
              demonstration, a real transfer was found but no verified service
              label was available, so the app correctly returned no service
              attribution.
            </p>
          </section>

          <section id="guide-questions" aria-labelledby="guide-questions-title">
            <span className="eyebrow">07 / IF YOU GET STUCK</span>
            <h2 id="guide-questions-title">Common questions</h2>
            <div className="help-faq">
              <details>
                <summary>
                  I have a wallet address. What do I need before starting?
                </summary>
                <p>
                  The correct blockchain, the address, a relevant UTC time
                  window and an authorised case. Live analysis also needs a
                  reachable, configured data provider. Service ownership needs
                  additional source-backed labels; transaction history alone
                  does not supply them.
                </p>
              </details>
              <details>
                <summary>
                  The graph is empty. Did the wallet do nothing?
                </summary>
                <p>
                  Not necessarily. Check the selected chain, UTC window,
                  acquired coverage, provider error and request limits in{" "}
                  <b>Evidence</b> and <b>Data & coverage</b>. The current trace
                  follows outgoing transfers; no returned outgoing event is not
                  proof of no wallet activity.
                </p>
              </details>
              <details>
                <summary>Why is a review or request button missing?</summary>
                <p>
                  Check your role and case membership. Review requires a
                  different authorised person from the submitter. A request also
                  needs a supported candidate and a current, approved matching
                  recipient. Withdrawn supporting evidence can block export
                  until the analysis is reassessed.
                </p>
              </details>
              <details>
                <summary>
                  Can I use this without buying an intelligence API?
                </summary>
                <p>
                  You can explore training cases, import suitable evidence and
                  use configured public sources where available. Those sources
                  have access and coverage limits. They do not replace a
                  reliable ownership database or official disclosure access.
                </p>
              </details>
              <details>
                <summary>
                  What is the useful difference in this approach?
                </summary>
                <p>
                  It shows where the evidence first supports custody, what the
                  answer depends on, which nearer branches remain unresolved and
                  which permitted query to try next. You can challenge a source
                  and replay the evidence. Accuracy or time savings have not yet
                  been established by an independent field benchmark.
                </p>
              </details>
              <details>
                <summary>
                  How should I explain the prototype in a presentation?
                </summary>
                <p>
                  Show a real Bitcoin acquisition with its timestamp and
                  limitations. Then visibly switch to a synthetic training case
                  to demonstrate attribution, source challenge, query planning,
                  bridge review and request packaging. Keep the mode and
                  NOT_SENT status visible. Do not describe a training service
                  label as a real-world identification.
                </p>
              </details>
            </div>
          </section>
          <div className="help-end">
            <p>Ready to try it?</p>
            <button className="button" onClick={onReturn}>
              {signedIn ? "Return to the workspace" : "Go to sign in"}
              <ArrowRight size={15} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
