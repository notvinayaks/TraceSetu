import {
  useEffect,
  useState,
  useId,
  isValidElement,
  cloneElement,
  lazy,
  Suspense,
  type FormEvent,
  type ReactNode,
} from "react";
import {
  Activity,
  ArrowDownToLine,
  ArrowLeft,
  ArrowRight,
  Bell,
  BookOpen,
  Check,
  ChevronRight,
  CircleHelp,
  Database,
  FileCheck2,
  FileSearch,
  FolderClosed,
  GitBranch,
  Landmark,
  Layers3,
  LoaderCircle,
  LockKeyhole,
  LogOut,
  Network,
  Plus,
  Search,
  Settings2,
  ShieldCheck,
  ShieldAlert,
  SlidersHorizontal,
  Upload,
  UserRound,
  X,
} from "lucide-react";
import { api, post, setCsrf, date, short, amount, type Row } from "./api";
import { HowItWorks } from "./HowItWorks";
const LazyGraph = lazy(() =>
  import("./Graph").then((m) => ({ default: m.FundGraph })),
);
function FundGraph(props: { graph: Row; onSelect: (row: Row) => void }) {
  return (
    <Suspense
      fallback={<div className="panel empty">Loading interactive graph…</div>}
    >
      <LazyGraph {...props} />
    </Suspense>
  );
}

const chains = ["bitcoin", "ethereum", "tron", "bnb", "solana", "polygon"];
const labels: Record<string, string> = {
  bitcoin: "Bitcoin",
  ethereum: "Ethereum",
  tron: "Tron",
  bnb: "BNB Chain",
  solana: "Solana",
  polygon: "Polygon",
};
type Modal =
  | "case"
  | "analysis"
  | "snapshot"
  | "assertion"
  | "bridge"
  | "recipient"
  | "request"
  | "review"
  | "watch"
  | "feedback"
  | "withdrawal"
  | "plan"
  | "execute_plan"
  | "user"
  | "password"
  | null;
const epoch = (v: FormDataEntryValue | null) =>
  Math.floor(new Date(String(v) + "Z").getTime() / 1000);
const utcInput = (time: number) => new Date(time).toISOString().slice(0, 16);

function Tag({ children, tone = "" }: { children: ReactNode; tone?: string }) {
  return <span className={"tag " + tone}>{children}</span>;
}
function Field({
  label,
  children,
  hint,
}: {
  label: string;
  children: ReactNode;
  hint?: string;
}) {
  const id = useId();
  const control = isValidElement<{
    id?: string;
    "aria-labelledby"?: string;
    "aria-describedby"?: string;
  }>(children)
    ? cloneElement(children, {
        id,
        "aria-labelledby": id + "-label",
        "aria-describedby": hint ? id + "-hint" : undefined,
      })
    : children;
  return (
    <label className="field" htmlFor={id}>
      <span id={id + "-label"}>{label}</span>
      {control}
      {hint && <small id={id + "-hint"}>{hint}</small>}
    </label>
  );
}
function Empty({
  title,
  text,
  children,
  icon = <FileSearch size={34} />,
}: {
  title: string;
  text: string;
  children?: ReactNode;
  icon?: ReactNode;
}) {
  return (
    <div className="empty">
      <div className="empty-icon">{icon}</div>
      <h3>{title}</h3>
      <p>{text}</p>
      {children}
    </div>
  );
}
function Json({ value }: { value: unknown }) {
  return <pre className="json">{JSON.stringify(value, null, 2)}</pre>;
}

export default function App() {
  const [user, setUser] = useState<Row | null>(null);
  const [starting, setStarting] = useState(true);
  const [view, setView] = useState("cases");
  const [cases, setCases] = useState<Row[]>([]);
  const [users, setUsers] = useState<Row[]>([]);
  const [current, setCurrent] = useState<Row | null>(null);
  const [jobs, setJobs] = useState<Row[]>([]);
  const [job, setJob] = useState<Row | null>(null);
  const [plannedQueries, setPlannedQueries] = useState<Row | null>(null);
  const [records, setRecords] = useState<Row[]>([]);
  const [recipients, setRecipients] = useState<Row[]>([]);
  const [caps, setCaps] = useState<Row | null>(null);
  const [audit, setAudit] = useState<Row[]>([]);
  const [tab, setTab] = useState("Overview");
  const [search, setSearch] = useState("");
  const [caseStatus, setCaseStatus] = useState("All cases");
  const [casePage, setCasePage] = useState(1);
  const [modal, setModal] = useState<Modal>(null);
  const [target, setTarget] = useState<Row | null>(null);
  const [selected, setSelected] = useState<Row | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [mode, setMode] = useState("live");
  const [challengeResult, setChallengeResult] = useState<Row | null>(null);
  const [verified, setVerified] = useState<Row | null>(null);
  const analysis = job?.result?.analysis;
  const canWrite = user?.role !== "reviewer";
  const filteredCases = cases.filter(
    (c) =>
      (caseStatus === "All cases" || c.status === caseStatus) &&
      (c.title + " " + c.reference)
        .toLowerCase()
        .includes(search.trim().toLowerCase()),
  );
  const pageCount = Math.max(1, Math.ceil(filteredCases.length / 8));
  const activePage = Math.min(casePage, pageCount);
  const visibleCases = filteredCases.slice(
    (activePage - 1) * 8,
    activePage * 8,
  );
  useEffect(() => {
    setCasePage(1);
  }, [search, caseStatus]);
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [view, current?.id, tab]);
  useEffect(() => {
    if (tab !== "Overview") setSelected(null);
  }, [tab]);
  useEffect(() => {
    setSelected(null);
  }, [view, current?.id]);
  useEffect(() => {
    if (!notice) return;
    const timer = window.setTimeout(() => setNotice(""), 6000);
    return () => window.clearTimeout(timer);
  }, [notice]);
  useEffect(() => {
    if (!modal && !selected) return;
    const escape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        if (modal && !busy) setModal(null);
        else setSelected(null);
      }
    };
    window.addEventListener("keydown", escape);
    return () => window.removeEventListener("keydown", escape);
  }, [modal, selected, busy]);
  useEffect(() => {
    if (!modal) return;
    const previous = document.activeElement as HTMLElement | null;
    const dialog = document.querySelector<HTMLElement>('[role="dialog"]');
    const focusables = () =>
      [
        ...(dialog?.querySelectorAll<HTMLElement>(
          "button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), a[href], summary",
        ) || []),
      ].filter((element) => element.getClientRects().length > 0);
    const firstInput = dialog?.querySelector<HTMLElement>(
      'input:not([type="checkbox"]), select, textarea',
    );
    (firstInput || focusables()[0])?.focus();
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const trap = (event: KeyboardEvent) => {
      if (event.key !== "Tab") return;
      const controls = focusables();
      const first = controls[0],
        last = controls[controls.length - 1];
      if (
        event.shiftKey &&
        (document.activeElement === first ||
          !dialog?.contains(document.activeElement))
      ) {
        event.preventDefault();
        last?.focus();
      } else if (
        !event.shiftKey &&
        (document.activeElement === last ||
          !dialog?.contains(document.activeElement))
      ) {
        event.preventDefault();
        first?.focus();
      }
    };
    document.addEventListener("keydown", trap);
    return () => {
      document.removeEventListener("keydown", trap);
      document.body.style.overflow = overflow;
      if (previous?.isConnected) previous.focus();
    };
  }, [modal]);
  useEffect(() => {
    if (!selected) return;
    const previous = document.activeElement as HTMLElement | null;
    document
      .querySelector<HTMLElement>('[aria-label="Evidence inspector"]')
      ?.focus();
    return () => {
      if (previous?.isConnected) previous.focus();
    };
  }, [selected]);
  function clearSession() {
    setCsrf("");
    setUser(null);
    setCurrent(null);
    setCases([]);
    setJob(null);
    setPlannedQueries(null);
    setJobs([]);
    setUsers([]);
    setRecipients([]);
    setRecords([]);
    setAudit([]);
    setCaps(null);
    setSelected(null);
    setChallengeResult(null);
    setModal(null);
    setTarget(null);
    setVerified(null);
    setNotice("");
    setError("");
    setSearch("");
    setCaseStatus("All cases");
    setCasePage(1);
    setView("cases");
    setTab("Overview");
  }
  useEffect(() => {
    window.addEventListener("atlas:session-expired", clearSession);
    return () =>
      window.removeEventListener("atlas:session-expired", clearSession);
  }, []);

  async function perform(fn: () => Promise<void>) {
    setError("");
    setBusy(true);
    try {
      await fn();
    } catch (e) {
      setError(e instanceof Error ? e.message : "An error occurred");
    } finally {
      setBusy(false);
    }
  }
  async function refreshGlobals() {
    const [c, u, r, p] = await Promise.all([
      api<Row[]>("/cases"),
      api<Row[]>("/users"),
      api<Row[]>("/recipients"),
      api<Row>("/capabilities"),
    ]);
    setCases(c);
    setUsers(u);
    setRecipients(r);
    setCaps(p);
  }
  async function refreshCase(id: string) {
    const [c, j, r, a] = await Promise.all([
      api<Row>("/cases/" + id),
      api<Row[]>("/cases/" + id + "/analyses"),
      api<Row[]>("/cases/" + id + "/records"),
      api<Row[]>("/cases/" + id + "/audit"),
    ]);
    setCurrent(c);
    setJobs(j);
    setRecords(r);
    setAudit(a);
  }
  useEffect(() => {
    api("/auth/me")
      .then((r) => {
        setCsrf(r.csrf);
        setUser(r.user);
      })
      .catch(() => {})
      .finally(() => setStarting(false));
  }, []);
  useEffect(() => {
    if (user) perform(refreshGlobals);
  }, [user?.id]);
  useEffect(() => {
    if (!current?.id) return;
    let active = true;
    setJob(null);
    setSelected(null);
    setChallengeResult(null);
    setTab("Overview");
    Promise.all([
      api<Row[]>("/cases/" + current.id + "/analyses"),
      api<Row[]>("/cases/" + current.id + "/records"),
      api<Row[]>("/cases/" + current.id + "/audit"),
    ])
      .then(async ([j, r, a]) => {
        if (!active) return;
        setJobs(j);
        setRecords(r);
        setAudit(a);
        if (j[0]) {
          const detail = await api<Row>("/analyses/" + j[0].id);
          if (active) setJob(detail);
        }
      })
      .catch((e) => setError(e.message));
    return () => {
      active = false;
    };
  }, [current?.id]);
  useEffect(() => {
    if (!job || !["QUEUED", "RUNNING"].includes(job.status)) return;
    let active = true;
    const timer = window.setInterval(async () => {
      try {
        const j = await api<Row>("/analyses/" + job.id);
        if (active) {
          setJob(j);
          if (!["QUEUED", "RUNNING"].includes(j.status))
            await refreshCase(j.case_id);
        }
      } catch (e) {
        if (active) setError((e as Error).message);
      }
    }, 1800);
    return () => {
      active = false;
      clearInterval(timer);
    };
  }, [job?.id, job?.status]);
  useEffect(() => {
    setPlannedQueries(null);
  }, [job?.id]);
  useEffect(() => {
    if (!modal) return;
    const previous = document.activeElement as HTMLElement | null;
    const dialog = document.querySelector(
      '[role="dialog"]',
    ) as HTMLElement | null;
    (
      dialog?.querySelector("input, select, textarea") as HTMLElement | null
    )?.focus();
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape" && !busy) setModal(null);
      if (event.key !== "Tab" || !dialog) return;
      const elements = [
        ...dialog.querySelectorAll<HTMLElement>(
          "button:not(:disabled), input:not(:disabled), select:not(:disabled), textarea:not(:disabled), a[href]",
        ),
      ].filter((e) => e.getAttribute("type") !== "hidden");
      const first = elements[0],
        last = elements[elements.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last?.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first?.focus();
      }
    };
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
      previous?.focus();
    };
  }, [modal, busy]);
  function open(name: Modal, row: Row | null = null) {
    setTarget(row);
    setModal(name);
    setError("");
    if (name === "request")
      api<Row[]>("/recipients")
        .then(setRecipients)
        .catch((e) => setError(e.message));
  }
  async function login(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const data = new FormData(e.currentTarget);
    await perform(async () => {
      const r = await post("/auth/login", Object.fromEntries(data));
      setCsrf(r.csrf);
      setUser(r.user);
    });
  }
  async function training(scenario = "custody") {
    await perform(async () => {
      const c = await post("/cases", {
        title:
          scenario === "cctp-review"
            ? "Cross-chain bridge · training investigation"
            : "Custody frontier · training investigation",
        reference: "TRAINING-" + new Date().toISOString().slice(0, 10),
        description:
          scenario === "cctp-review"
            ? "Synthetic CCTP review exercise: invented receipts, local test attester and fictional exchange. No live evidence."
            : "Synthetic scenario: a direct deposit, a second custody path, a mixer boundary and an incomplete branch. All services and wallets are fictional.",
        members: users.map((u) => u.id),
      });
      await refreshGlobals();
      setCurrent(c);
      setView("cases");
      const j = await post(
        "/cases/" + c.id + "/analyses",
        {
          mode: "fixture",
          fixture_scenario: scenario,
          spec: {
            chain: "ethereum",
            address: "fixture:suspect",
            start: 1750000000,
            end: 1750001000,
          },
        },
        { "Idempotency-Key": crypto.randomUUID() },
      );
      setJob(j);
    });
  }
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const str = (name: string) => String(f.get(name) || "");
    const num = (name: string) => Number(f.get(name));
    await perform(async () => {
      if (modal === "case") {
        const body = {
          title: str("title"),
          reference: str("reference"),
          description: str("description"),
          members: f.getAll("members"),
          classification: str("classification"),
        };
        const c = target
          ? await api("/cases/" + target.id, {
              method: "PATCH",
              body: JSON.stringify({
                ...body,
                version: target.version,
                status: str("status"),
              }),
            })
          : await post("/cases", body);
        setCurrent(c);
        setView("cases");
      }
      if (modal === "analysis") {
        const imported = records.find((r) => r.id === str("snapshot_id"));
        const spec = {
          chain: str("chain"),
          address: str("address") || "fixture:suspect",
          start:
            mode === "imported"
              ? imported?.window_start
              : epoch(f.get("start")),
          end: mode === "imported" ? imported?.window_end : epoch(f.get("end")),
          max_hops: num("max_hops"),
          max_requests: num("max_requests"),
        };
        const j = await post(
          "/cases/" + current!.id + "/analyses",
          {
            mode,
            fixture_scenario: str("fixture_scenario") || "custody",
            spec,
            snapshot_id: mode === "imported" ? str("snapshot_id") : null,
          },
          { "Idempotency-Key": crypto.randomUUID() },
        );
        setJob(j);
        setChallengeResult(null);
      }
      if (modal === "snapshot") {
        const file = f.get("file") as File;
        await post("/cases/" + current!.id + "/snapshots", {
          snapshot: JSON.parse(await file.text()),
          provenance: str("provenance"),
        });
      }
      if (modal === "bridge") {
        const file = f.get("file") as File;
        await post("/cases/" + current!.id + "/bridges", {
          proof: target?.proof || JSON.parse(await file.text()),
          mode: str("mode"),
          rationale: str("rationale"),
        });
      }
      if (modal === "assertion")
        await post("/cases/" + current!.id + "/assertions", {
          rationale: str("rationale"),
          assertion: {
            id: "server-assigned",
            chain: str("chain"),
            address: str("address"),
            entity: str("entity"),
            category: str("category"),
            role: str("role"),
            grade: "hypothesis",
            source_family: str("source_family"),
            source: str("source"),
            evidence: [str("evidence")],
            risk_tags: str("risk_tags")
              .split(",")
              .map((s) => s.trim())
              .filter(Boolean),
          },
        });
      if (modal === "recipient")
        await post("/recipients", {
          mode: str("mode"),
          entity: str("entity"),
          jurisdiction: str("jurisdiction"),
          channel: str("channel"),
          verification_source: str("verification_source"),
          signing_public_key: str("signing_public_key") || null,
          expires_at: epoch(f.get("expires_at")),
        });
      if (modal === "request")
        await post("/cases/" + current!.id + "/requests", {
          job_id: job!.id,
          candidate_index: num("candidate_index"),
          recipient_id: str("recipient_id"),
          type: str("type"),
          legal_basis: str("legal_basis"),
          scope: str("scope"),
        });
      if (modal === "review")
        await post("/records/" + target!.id + "/review", {
          version: target!.version,
          decision: str("decision"),
          rationale: str("rationale"),
        });
      if (modal === "feedback")
        await post("/cases/" + current!.id + "/feedback", {
          request_id: str("request_id"),
          payload: JSON.parse(str("payload")),
          signature: str("signature"),
        });
      if (modal === "withdrawal")
        await post("/evidence/" + target!.id + "/withdrawal", {
          version: target!.version,
          rationale: str("rationale"),
        });
      if (modal === "plan") {
        const r = await post("/analyses/" + job!.id + "/query-plan", {
          budget_requests: num("budget_requests"),
        });
        setPlannedQueries({
          ...r.plan,
          record_id: r.id,
          version: r.version,
          sha256: r.sha256,
        });
      }
      if (modal === "execute_plan") {
        const r = await post(
          `/analyses/${job!.id}/query-plans/${target!.record_id}/execute`,
          {
            version: target!.version,
            plan_sha256: target!.sha256,
          },
          { "Idempotency-Key": "execute-" + target!.record_id },
        );
        setJob(r);
        setSelected(null);
        setChallengeResult(null);
        setTab("Overview");
        // Keep the running-job status in view when the result panels disappear.
        window.scrollTo({ top: 0, behavior: "auto" });
      }
      if (modal === "watch")
        await post("/cases/" + current!.id + "/watches", {
          spec: {
            chain: str("chain"),
            address: str("address"),
            start: epoch(f.get("start")),
            end: Math.floor(Date.now() / 1000),
            max_requests: num("max_requests"),
            max_hops: num("max_hops"),
          },
          interval_minutes: num("interval_minutes"),
          enabled: true,
        });
      if (modal === "user") await post("/users", Object.fromEntries(f));
      if (modal === "password") {
        await post("/auth/password", Object.fromEntries(f));
        clearSession();
        return;
      }
      setModal(null);
      setNotice("Saved successfully.");
      if (user) await refreshGlobals();
      if (current) await refreshCase(current.id);
      if (job && modal !== "analysis" && modal !== "execute_plan")
        setJob(await api("/analyses/" + job.id));
    });
  }
  async function challengeLabel(a: Row) {
    await perform(async () => {
      setChallengeResult(
        await post("/analyses/" + job!.id + "/challenge", {
          excluded: [a.source_family],
        }),
      );
      setTab("Assumptions");
    });
  }
  const field = (name: string, label: string, props: Row = {}) => (
    <Field label={label}>
      <input name={name} required {...props} />
    </Field>
  );
  const chainField = (
    <Field label="Blockchain">
      <select
        name="chain"
        defaultValue={job?.request?.spec?.chain || "ethereum"}
      >
        {chains.map((c) => (
          <option key={c} value={c}>
            {labels[c]}
          </option>
        ))}
      </select>
    </Field>
  );
  const specFields = (
    <>
      <div className="form-grid">
        {chainField}
        {field("address", "Reported wallet", {
          defaultValue: job?.request?.spec?.address?.startsWith("fixture:")
            ? ""
            : job?.request?.spec?.address,
        })}
      </div>
      <div className="form-grid">
        {field("start", "Start (UTC)", {
          type: "datetime-local",
          defaultValue: utcInput(Date.now() - 30 * 86400000),
        })}
        {field("end", "End (UTC)", {
          type: "datetime-local",
          defaultValue: utcInput(Date.now()),
        })}
      </div>
    </>
  );
  const budgetFields = (
    <div className="form-grid">
      {field("max_hops", "Maximum custody hops", {
        type: "number",
        min: 1,
        max: 8,
        defaultValue: 3,
      })}
      {field("max_requests", "Maximum provider requests", {
        type: "number",
        min: 1,
        max: 200,
        defaultValue: 30,
      })}
    </div>
  );
  const reviewButton = (r: Row) =>
    r.status === "pending" &&
    user?.role !== "investigator" &&
    r.created_by !== user?.id ? (
      <button className="button small" onClick={() => open("review", r)}>
        Review <ArrowRight size={13} />
      </button>
    ) : null;

  if (starting)
    return (
      <div className="loading-screen">
        <LoaderCircle className="spin" /> Loading workspace
      </div>
    );
  if (!user && view === "guide")
    return (
      <div className="public-guide">
        <header>
          <a
            className="brand"
            href="#"
            onClick={(e) => {
              e.preventDefault();
              setView("cases");
            }}
          >
            <img src="/favicon.svg" alt="" />
            <span>TraceSetu</span>
          </a>
        </header>
        <main className="content">
          <HowItWorks
            signedIn={false}
            canWrite={false}
            busy={busy}
            onTraining={() => {}}
            onReturn={() => setView("cases")}
          />
        </main>
      </div>
    );
  if (!user)
    return (
      <div className="login-page">
        <section className="login-art">
          <div className="brand">
            <img src="/favicon.svg" />
            <span>TraceSetu</span>
          </div>
          <div className="login-copy">
            <span className="eyebrow">THE INVESTIGATION DESK</span>
            <h1>
              A clear view
              <br />
              of the money trail.
            </h1>
            <p>
              Trace a reported wallet. Understand the evidence. Prepare the next
              step.
            </p>
            <ol className="login-steps">
              <li>
                <span>01</span>
                <div>
                  <strong>Follow the transfers</strong>
                  <small>Find the first supported receiving service.</small>
                </div>
              </li>
              <li>
                <span>02</span>
                <div>
                  <strong>Check the evidence</strong>
                  <small>
                    Review sources, missing history and assumptions.
                  </small>
                </div>
              </li>
              <li>
                <span>03</span>
                <div>
                  <strong>Prepare a reviewed request</strong>
                  <small>Keep every decision tied to its case.</small>
                </div>
              </li>
            </ol>
          </div>
          <footer>
            Independent installation{" "}
            <span>SAHYOG connection requires official access</span>
          </footer>
        </section>
        <section className="login-form">
          <div>
            <Tag tone="teal">
              <LockKeyhole size={12} /> Authorised access
            </Tag>
            <h2>Sign in to your workspace</h2>
            <p>Use the account issued by your administrator.</p>
            <form onSubmit={login}>
              {field("username", "Username", { autoComplete: "username" })}
              {field("password", "Password", {
                type: "password",
                autoComplete: "current-password",
              })}
              {error && (
                <div role="alert" className="error">
                  {error}
                </div>
              )}
              <button className="button primary full" disabled={busy}>
                {busy ? <LoaderCircle className="spin" size={17} /> : "Sign in"}
                <ArrowRight size={17} />
              </button>
            </form>
            <div className="login-note">
              <ShieldCheck size={19} />
              <span>
                Cases are access controlled. Evidence and review actions are
                recorded in the case audit trail.
              </span>
            </div>
            <button className="login-help" onClick={() => setView("guide")}>
              <BookOpen size={16} /> New to TraceSetu? See how it works{" "}
              <ArrowRight size={14} />
            </button>
          </div>
        </section>
      </div>
    );

  return (
    <div className="app">
      <aside className="sidebar">
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            setView("cases");
            setCurrent(null);
          }}
        >
          <img src="/favicon.svg" />
          <span>TraceSetu</span>
        </a>
        <div className="workspace-chip">
          <div>
            Investigation desk<small>Independent installation</small>
          </div>
        </div>
        <div className="nav-caption">WORKSPACE</div>
        <nav aria-label="Main navigation">
          {[
            ["cases", FolderClosed, "Investigations"],
            ["directory", Landmark, "VASP directory"],
            ["verify", FileCheck2, "Verify evidence"],
            ["system", Activity, "Data & coverage"],
            ["guide", BookOpen, "How it works"],
          ].map(([id, Icon, text]) => {
            const I = Icon as typeof FolderClosed;
            return (
              <button
                key={String(id)}
                className={view === id ? "active" : ""}
                aria-current={view === id ? "page" : undefined}
                onClick={() => {
                  setView(String(id));
                  if (id === "cases") setCurrent(null);
                }}
              >
                <I size={18} />
                {String(text)}
                {view === id && <ChevronRight size={15} />}
              </button>
            );
          })}
        </nav>
        <div className="sidebar-bottom">
          <div className="connection-note">
            <span className="status-dot amber" /> SAHYOG not connected
            <small>Reviewed packages can be exported</small>
          </div>
          <button className="user-card" onClick={() => setView("account")}>
            <div className="avatar">{user.name.slice(0, 1)}</div>
            <div>
              {user.name}
              <small>{user.role}</small>
            </div>
            <Settings2 size={16} />
          </button>
        </div>
      </aside>
      <div className="main">
        <header className="topbar">
          <div>
            <span>Workspace</span>
            <ChevronRight size={13} />
            <strong>
              {view === "cases"
                ? current?.reference || "Investigations"
                : view === "directory"
                  ? "VASP directory"
                  : view === "verify"
                    ? "Verify evidence"
                    : view === "account"
                      ? "Account & access"
                      : view === "guide"
                        ? "How it works"
                        : "Data & coverage"}
            </strong>
          </div>
          <div>
            <span className="restricted">
              <LockKeyhole size={12} /> Restricted
            </span>
            <span className="top-divider" />
            <button
              className="icon-button"
              aria-label="Account settings"
              onClick={() => setView("account")}
            >
              <UserRound size={18} />
            </button>
          </div>
        </header>
        {error && !modal && (
          <div role="alert" className="banner error">
            {error}
            <button onClick={() => setError("")} aria-label="Dismiss error">
              <X size={16} />
            </button>
          </div>
        )}
        {notice && (
          <div role="status" className="toast">
            <Check size={16} />
            {notice}
            <button
              aria-label="Dismiss notification"
              onClick={() => setNotice("")}
            >
              <X size={15} />
            </button>
          </div>
        )}
        <main className="content">
          {view === "guide" && (
            <HowItWorks
              signedIn
              canWrite={canWrite}
              busy={busy}
              onTraining={() => training()}
              onReturn={() => setView("cases")}
            />
          )}
          {view === "cases" && !current && (
            <>
              <div className="page-heading">
                <div>
                  <span className="eyebrow">YOUR WORKSPACE</span>
                  <h1>Investigations</h1>
                  <p>Open a case, follow the funds and review the evidence.</p>
                  <button
                    className="help-inline"
                    onClick={() => setView("guide")}
                  >
                    <BookOpen size={13} /> First time here? How it works
                  </button>
                </div>
                {canWrite && (
                  <button
                    className="button primary"
                    onClick={() => open("case")}
                  >
                    <Plus size={17} />
                    New investigation
                  </button>
                )}
              </div>
              <div className="training-strip">
                <div>
                  <strong>
                    Try a sample investigation{" "}
                    <Tag tone="amber">Synthetic data</Tag>
                  </strong>
                  <p>Follow a wallet trail or review a cross-chain transfer.</p>
                </div>
                {canWrite && (
                  <button
                    className="button"
                    onClick={() => training()}
                    disabled={busy}
                  >
                    Open training case <ArrowRight size={15} />
                  </button>
                )}
                {canWrite && (
                  <button
                    className="button"
                    onClick={() => training("cctp-review")}
                    disabled={busy}
                  >
                    Review a bridge case
                  </button>
                )}
              </div>
              <section className="panel case-register">
                <div className="panel-heading">
                  <div
                    className="case-filters"
                    role="group"
                    aria-label="Filter cases by status"
                  >
                    {["All cases", "Open", "Under review", "Closed"].map(
                      (status) => (
                        <button
                          key={status}
                          aria-pressed={caseStatus === status}
                          className={caseStatus === status ? "active" : ""}
                          onClick={() => setCaseStatus(status)}
                        >
                          {status}
                          {status === "All cases" && (
                            <span className="count">{cases.length}</span>
                          )}
                        </button>
                      ),
                    )}
                  </div>
                  <div className="search">
                    <Search size={16} />
                    <input
                      aria-label="Search cases"
                      placeholder="Search cases or references…"
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                    />
                  </div>
                </div>
                {filteredCases.length ? (
                  <div className="case-table">
                    <div className="table-head">
                      <span>CASE / REFERENCE</span>
                      <span>STATUS</span>
                      <span>CLASSIFICATION</span>
                      <span>LAST UPDATED</span>
                      <span />
                    </div>
                    {visibleCases.map((c) => (
                      <button
                        className="case-row"
                        data-case-id={c.id}
                        key={c.id}
                        onClick={() => setCurrent(c)}
                      >
                        <div>
                          <span className="case-icon">
                            <FolderClosed size={20} />
                          </span>
                          <span>
                            <strong>{c.title}</strong>
                            <small>{c.reference}</small>
                          </span>
                        </div>
                        <span>
                          <Tag tone={c.status === "Open" ? "teal" : ""}>
                            {c.status}
                          </Tag>
                        </span>
                        <span>{c.classification}</span>
                        <span>{date(c.updated)}</span>
                        <ChevronRight size={17} />
                      </button>
                    ))}
                  </div>
                ) : (
                  <Empty
                    title={
                      cases.length
                        ? "No matching investigations"
                        : "Your first investigation starts here"
                    }
                    text={
                      cases.length
                        ? "Try a different case name, reference or status."
                        : "Create a case or open a sample investigation to get started."
                    }
                  />
                )}
                <div className="table-pagination">
                  <span>
                    {filteredCases.length
                      ? `${(activePage - 1) * 8 + 1}–${Math.min(activePage * 8, filteredCases.length)} of ${filteredCases.length} cases`
                      : "0 cases"}
                  </span>
                  <div className="row">
                    <button
                      className="button small"
                      disabled={activePage === 1}
                      onClick={() => setCasePage(activePage - 1)}
                    >
                      Previous
                    </button>
                    <span>
                      Page {activePage} of {pageCount}
                    </span>
                    <button
                      className="button small"
                      disabled={activePage === pageCount}
                      onClick={() => setCasePage(activePage + 1)}
                    >
                      Next
                    </button>
                  </div>
                </div>
              </section>
            </>
          )}

          {view === "cases" && current && (
            <>
              <button className="back-link" onClick={() => setCurrent(null)}>
                <ArrowLeft size={14} />
                All investigations
              </button>
              <div className="page-heading case-heading">
                <div>
                  <div className="row">
                    <span className="eyebrow">{current.reference}</span>
                    <Tag tone="teal">{current.status}</Tag>
                  </div>
                  <h1>{current.title}</h1>
                  <details className="case-description">
                    <summary>Case notes</summary>
                    <p>
                      {current.description || "No case description provided."}
                    </p>
                  </details>
                </div>
                <div className="actions">
                  {canWrite && (
                    <button
                      className="button"
                      onClick={() => open("case", current)}
                    >
                      <Settings2 size={15} />
                      Manage case
                    </button>
                  )}
                  {analysis && !job?.evidence_changes?.length && (
                    <a
                      className="button"
                      href={"/api/analyses/" + job!.id + "/report.pdf"}
                    >
                      <ArrowDownToLine size={16} />
                      Report
                    </a>
                  )}
                  {canWrite && (
                    <button
                      className="button primary"
                      onClick={() => {
                        setMode("live");
                        open("analysis");
                      }}
                    >
                      <Plus size={16} />
                      Analyse wallet
                    </button>
                  )}
                </div>
              </div>
              <div className="case-toolbar">
                <div className="row">
                  <Layers3 size={16} />
                  <select
                    aria-label="Select analysis"
                    value={job?.id || ""}
                    onChange={(e) =>
                      perform(async () => {
                        setJob(await api("/analyses/" + e.target.value));
                        setSelected(null);
                        setChallengeResult(null);
                      })
                    }
                  >
                    <option value="" disabled>
                      No analysis selected
                    </option>
                    {jobs.map((j) => (
                      <option key={j.id} value={j.id}>
                        {j.request.mode.toUpperCase()} ·{" "}
                        {short(j.request.spec.address, 10)} · {date(j.created)}
                      </option>
                    ))}
                  </select>
                  {job && (
                    <Tag
                      tone={job.request.mode === "fixture" ? "amber" : "blue"}
                    >
                      {job.request.mode === "fixture"
                        ? "SYNTHETIC TRAINING"
                        : job.request.mode.toUpperCase()}
                    </Tag>
                  )}
                </div>
                <span>
                  {job
                    ? job.status.replaceAll("_", " ").toLowerCase()
                    : "Ready to investigate"}
                </span>
              </div>
              {job?.request.mode === "fixture" && (
                <div className="fixture-banner">
                  <CircleHelp size={16} />
                  <span>
                    Training case. All wallets, services and transactions are
                    fictional.
                  </span>
                </div>
              )}
              {job?.request.mode === "live" && analysis && (
                <div className="live-acquisition" role="status">
                  <div>
                    <strong>
                      <span
                        className={
                          "status-dot" +
                          (job.result.raw_evidence.length ? "" : " amber")
                        }
                      />
                      {job.result.raw_evidence.length
                        ? "Live data acquired"
                        : "No provider data acquired"}
                    </strong>
                    <span>
                      {job.result.raw_evidence.length
                        ? `${[...new Set(job.result.raw_evidence.map((r: Row) => r.provider))].join(", ")} · ${analysis.graph.events.length} observed transfer(s) · fetched ${date(Math.max(...job.result.raw_evidence.map((r: Row) => r.retrieved_at)))}`
                        : "Check the acquisition limits below. No training data has been substituted."}
                    </span>
                  </div>
                  {canWrite && (
                    <button
                      className="button small"
                      disabled={busy}
                      onClick={() =>
                        perform(async () => {
                          setJob(
                            await post(
                              "/cases/" + current.id + "/analyses",
                              {
                                mode: "live",
                                spec: {
                                  ...job.request.spec,
                                  end: Math.floor(Date.now() / 1000),
                                },
                              },
                              { "Idempotency-Key": crypto.randomUUID() },
                            ),
                          );
                          setSelected(null);
                          setChallengeResult(null);
                          setTab("Overview");
                          await refreshCase(current.id);
                        })
                      }
                    >
                      Refresh live data
                    </button>
                  )}
                </div>
              )}
              <div className="tabs">
                {[
                  "Overview",
                  "Evidence",
                  "Assumptions",
                  "Requests",
                  "Monitoring",
                  "Audit trail",
                ].map((t) => (
                  <button
                    key={t}
                    className={tab === t ? "active" : ""}
                    onClick={() => setTab(t)}
                    aria-current={tab === t ? "page" : undefined}
                  >
                    {t}
                    {t === "Requests" &&
                      records.some(
                        (r) => r.kind === "request" && r.status === "pending",
                      ) && <i />}
                  </button>
                ))}
              </div>
              {!!job?.evidence_changes?.length && (
                <div className="callout">
                  <ShieldAlert size={18} />
                  <span>
                    Supporting evidence was withdrawn after this analysis.
                    Historical results are preserved; reassess before preparing
                    or exporting requests and reports.
                  </span>
                </div>
              )}
              {analysis && canWrite && (
                <div className="section-actions reassess-bar">
                  <p className="muted">
                    New evidence reviewed? Update this analysis.
                  </p>
                  <button
                    className="button small"
                    disabled={busy}
                    onClick={() =>
                      perform(async () => {
                        setJob(
                          await post(
                            "/analyses/" + job!.id + "/reassess",
                            {},
                            { "Idempotency-Key": crypto.randomUUID() },
                          ),
                        );
                        setTab("Overview");
                        setChallengeResult(null);
                      })
                    }
                  >
                    Reassess recorded evidence
                  </button>
                </div>
              )}
              {tab === "Overview" &&
                (!analysis ? (
                  <section className="panel">
                    <Empty
                      icon={
                        job && ["QUEUED", "RUNNING"].includes(job.status) ? (
                          <LoaderCircle className="spin" size={32} />
                        ) : (
                          <Network size={34} />
                        )
                      }
                      title={job ? job.stage : "Build an evidence-backed trace"}
                      text={
                        job?.error ||
                        "Select a blockchain, reported address and investigation window. Provider failures and incomplete coverage will remain visible."
                      }
                    >
                      {job &&
                        ["QUEUED", "RUNNING"].includes(job.status) &&
                        canWrite && (
                          <button
                            className="button"
                            onClick={() =>
                              perform(async () => {
                                setJob(
                                  await post("/analyses/" + job.id + "/cancel"),
                                );
                              })
                            }
                          >
                            Cancel analysis
                          </button>
                        )}
                      {!job && canWrite && (
                        <button
                          className="button primary"
                          onClick={() => open("analysis")}
                        >
                          Start analysis <ArrowRight size={16} />
                        </button>
                      )}
                    </Empty>
                  </section>
                ) : (
                  <>
                    <section
                      className="result-summary"
                      aria-label="Analysis summary"
                    >
                      <div className="result-answer">
                        <span className="eyebrow">
                          FIRST SUPPORTED RECEIVING SERVICE
                        </span>
                        <strong>
                          {analysis.candidates.length
                            ? (() => {
                                const names = [
                                  ...new Set(
                                    analysis.candidates
                                      .filter(
                                        (c: Row) =>
                                          c.hops ===
                                          analysis.certificate
                                            .nearest_evidenced_hops,
                                      )
                                      .map((c: Row) => c.entity),
                                  ),
                                ];
                                return names.length === 1
                                  ? String(names[0])
                                  : `${names.length} services at the same distance`;
                              })()
                            : "No service identified yet"}
                        </strong>
                        <p>
                          {analysis.certificate.nearest_evidenced_hops !==
                            null && (
                            <b>
                              {analysis.certificate.nearest_evidenced_hops}{" "}
                              {analysis.certificate.nearest_evidenced_hops === 1
                                ? "hop"
                                : "hops"}{" "}
                              from the reported wallet.{" "}
                            </b>
                          )}
                          Based on this evidence only. Unlabelled services may
                          be closer.
                        </p>
                      </div>
                      <div className="result-count">
                        <strong>{analysis.candidates.length}</strong>
                        <span>Custody paths</span>
                      </div>
                      <div className="result-count">
                        <strong>{analysis.query_plan.length}</strong>
                        <span>Unresolved branches</span>
                      </div>
                    </section>
                    <div className="investigation-grid">
                      <div>
                        <FundGraph
                          graph={analysis.graph}
                          onSelect={setSelected}
                        />
                        {selected && (
                          <section
                            className="panel inspector"
                            role="region"
                            aria-label="Evidence inspector"
                            tabIndex={-1}
                          >
                            <div className="panel-heading">
                              <h2>
                                {selected.type === "event"
                                  ? "Transfer evidence"
                                  : "Wallet inspection"}
                              </h2>
                              <button
                                className="icon-button"
                                aria-label="Close inspector"
                                onClick={() => setSelected(null)}
                              >
                                <X size={16} />
                              </button>
                            </div>
                            <div className="panel-body">
                              {selected.type === "event" ? (
                                <>
                                  <code className="block-code">
                                    {selected.txid}
                                  </code>
                                  <div className="key-values">
                                    <span>
                                      {selected.kind === "bridge"
                                        ? "Net delivery amount"
                                        : "Observed amount"}
                                    </span>
                                    <strong>
                                      {amount(
                                        selected.amount,
                                        selected.decimals,
                                      )}{" "}
                                      ({selected.amount} base units)
                                    </strong>
                                    <span>Asset identity</span>
                                    <code>{selected.asset}</code>
                                    <span>Finality</span>
                                    <span>{selected.finality}</span>
                                    <span>Observed at</span>
                                    <span>{date(selected.timestamp)}</span>
                                  </div>
                                  <p className="muted">
                                    {selected.kind === "bridge"
                                      ? "Protocol-correlated delivery: the source burn and destination mint are separate transactions. "
                                      : "This transfer is observed. "}
                                    Allocation of incident funds through mixed
                                    balances is not established.
                                  </p>
                                  {selected.bridge_details && (
                                    <section className="callout bridge-detail">
                                      <strong>
                                        CCTP V2 delivery ·{" "}
                                        {labels[selected.chain]} →{" "}
                                        {labels[selected.destination_chain]}
                                      </strong>
                                      <p>
                                        Burned{" "}
                                        {amount(
                                          selected.bridge_details.burned_amount,
                                          6,
                                        )}{" "}
                                        USDC; fee{" "}
                                        {amount(
                                          selected.bridge_details.fee_amount,
                                          6,
                                        )}
                                        ; minted{" "}
                                        {amount(
                                          selected.bridge_details.minted_amount,
                                          6,
                                        )}
                                        .
                                      </p>
                                      <p>
                                        Destination mint:{" "}
                                        {date(
                                          selected.bridge_details
                                            .destination_timestamp,
                                        )}
                                      </p>
                                      <code className="block-code">
                                        {
                                          selected.bridge_details
                                            .destination_txhash
                                        }
                                      </code>
                                      <p>{selected.bridge_details.trust}</p>
                                      <details>
                                        <summary>
                                          Protocol proof details
                                        </summary>
                                        <Json value={selected.bridge_details} />
                                      </details>
                                    </section>
                                  )}
                                  {selected.evidence.map((h: string) => (
                                    <div className="evidence-reference" key={h}>
                                      {job!.result.raw_evidence.some(
                                        (r: Row) => r.sha256 === h,
                                      ) ? (
                                        <a
                                          href={`/api/analyses/${job!.id}/evidence/${h}`}
                                          target="_blank"
                                          rel="noreferrer"
                                        >
                                          Raw evidence: {short(h)}
                                        </a>
                                      ) : (
                                        <code>{h}</code>
                                      )}
                                    </div>
                                  ))}
                                </>
                              ) : (
                                <>
                                  <code className="block-code">
                                    {selected.address || selected.txid}
                                  </code>
                                  {selected.labels?.length ? (
                                    selected.labels.map((a: Row) => (
                                      <div
                                        className="assertion-line"
                                        key={a.id}
                                      >
                                        <div>
                                          <strong>{a.entity}</strong>
                                          <p>
                                            {a.category} · {a.role} · {a.grade}
                                          </p>
                                          <small>
                                            {a.source_family} — {a.source}
                                          </small>
                                        </div>
                                        <button
                                          className="button small"
                                          onClick={() => challengeLabel(a)}
                                        >
                                          Challenge source
                                        </button>
                                      </div>
                                    ))
                                  ) : (
                                    <p className="muted">
                                      No ownership assertion. Unknown does not
                                      mean self-custody or low risk.
                                    </p>
                                  )}
                                </>
                              )}
                            </div>
                          </section>
                        )}
                        <section className="panel certificate">
                          <div className="panel-heading">
                            <h2>
                              <FileCheck2 size={17} /> Nearestness certificate
                            </h2>
                            <Tag tone="blue">Inspectable</Tag>
                          </div>
                          <div className="panel-body">
                            <div className="certificate-line">
                              <span>
                                Nearest known target in the bounded snapshot
                              </span>
                              <Tag
                                tone={
                                  analysis.certificate
                                    .nearest_known_target_in_snapshot_proven
                                    ? "teal"
                                    : "amber"
                                }
                              >
                                {analysis.certificate
                                  .nearest_known_target_in_snapshot_proven
                                  ? "Established"
                                  : "Not established"}
                              </Tag>
                            </div>
                            <div className="certificate-line">
                              <span>
                                Nearest actual service, including unlabelled
                                wallets
                              </span>
                              <Tag tone="amber">Not established</Tag>
                            </div>
                            <p>{analysis.certificate.scope}</p>
                            <code className="hash-line">
                              Snapshot SHA-256{" "}
                              {analysis.certificate.snapshot_sha256}
                            </code>
                          </div>
                        </section>
                        <section className="panel spaced">
                          <div className="panel-heading">
                            <h2>Risk signals</h2>
                            <Tag
                              tone={analysis.risk.signals.length ? "amber" : ""}
                            >
                              {analysis.risk.signals.length
                                ? "Source-tagged exposure"
                                : "Unassessed"}
                            </Tag>
                          </div>
                          <div className="panel-body">
                            <p className="muted">
                              A source tag is an investigative lead, not a
                              finding of criminal activity. Unknown ownership
                              does not mean low risk.
                            </p>
                            {analysis.risk.signals.map(
                              (signal: Row, index: number) => (
                                <div className="risk-signal" key={index}>
                                  <strong>
                                    {signal.tag.replaceAll("_", " ")}
                                  </strong>
                                  <code>{signal.node}</code>
                                  <small>
                                    {signal.grade} · Assertion:{" "}
                                    {signal.assertion_id}
                                  </small>
                                </div>
                              ),
                            )}
                          </div>
                        </section>
                      </div>
                      <aside className="findings">
                        <section className="panel">
                          <div className="panel-heading">
                            <h2>Custody boundaries</h2>
                            <span className="count">
                              {analysis.candidates.length}
                            </span>
                          </div>
                          {analysis.candidates.length ? (
                            analysis.candidates.map((c: Row, i: number) => (
                              <div className="candidate" key={i}>
                                <div className="row between">
                                  <span className="candidate-icon">
                                    <Landmark size={17} />
                                  </span>
                                  <Tag
                                    tone={
                                      c.status === "evidenced"
                                        ? "teal"
                                        : "amber"
                                    }
                                  >
                                    {c.hops} {c.hops === 1 ? "hop" : "hops"}
                                  </Tag>
                                </div>
                                <h3>{c.entity}</h3>
                                <p>
                                  {c.deposit_role === "deposit"
                                    ? "Deposit wallet assertion"
                                    : "Deposit acceptance not established"}
                                </p>
                                <code>{short(c.address, 12)}</code>
                                <div className="candidate-bottom">
                                  <Tag>{c.status}</Tag>
                                  <button
                                    onClick={() =>
                                      setSelected({
                                        type: "node",
                                        address: c.address,
                                        labels: c.assertions,
                                      })
                                    }
                                  >
                                    Inspect evidence <ArrowRight size={13} />
                                  </button>
                                </div>
                              </div>
                            ))
                          ) : (
                            <div className="panel-body muted">
                              No custody attribution is available from this
                              evidence.
                            </div>
                          )}
                        </section>
                        <section className="panel next-steps">
                          <div className="panel-heading">
                            <h2>
                              <SlidersHorizontal size={17} /> Next evidence
                              actions
                            </h2>
                          </div>
                          <div className="panel-body">
                            <p className="muted">
                              Check the nearest gaps first. Set a request budget
                              to prioritise which wallet history to acquire
                              next. Estimates do not guarantee complete
                              coverage.
                            </p>
                            {job?.result.acquisition_metrics && (
                              <p className="muted">
                                This run{" "}
                                {job.result.acquisition_metrics
                                  .request_count_kind ===
                                "reserved_attempt_slots"
                                  ? "reserved"
                                  : "used"}{" "}
                                {
                                  job.result.acquisition_metrics
                                    .attempted_http_requests
                                }{" "}
                                {job.result.acquisition_metrics
                                  .request_count_kind ===
                                "reserved_attempt_slots"
                                  ? "request slots"
                                  : "HTTP requests"}{" "}
                                (
                                {
                                  job.result.acquisition_metrics
                                    .within_job_cache_hits
                                }{" "}
                                cache hits). Vendor billing units are unknown.
                              </p>
                            )}
                            {job?.result.execution && (
                              <div className="callout query-execution">
                                <strong>Query execution complete</strong>
                                <p>
                                  {job.result.execution.mode === "fixture"
                                    ? "Synthetic expansion; zero provider calls."
                                    : "Selected scopes acquired under a shared job budget."}{" "}
                                  Parent evidence is preserved. Reserved slots
                                  survive retries and may include a call lost
                                  before dispatch.
                                </p>
                                <details>
                                  <summary>
                                    Execution outcomes and input binding
                                  </summary>
                                  <Json value={job.result.execution} />
                                </details>
                              </div>
                            )}
                            <button
                              className="button small"
                              onClick={() => open("plan")}
                            >
                              Plan within a request budget
                            </button>
                            {plannedQueries && (
                              <div>
                                <p className="muted">
                                  {plannedQueries.selected_estimated_requests}{" "}
                                  of {plannedQueries.budget_requests} requests
                                  allocated by estimate. Advisory only; nothing
                                  fetched. {plannedQueries.availability_basis}
                                </p>
                                {canWrite &&
                                  !job?.evidence_changes?.length &&
                                  plannedQueries.actions.some(
                                    (a: Row) =>
                                      a.status === "selected_estimate" &&
                                      a.action === "reacquire_history",
                                  ) && (
                                    <button
                                      className="button primary small"
                                      onClick={() =>
                                        open("execute_plan", plannedQueries)
                                      }
                                    >
                                      {analysis.mode === "fixture"
                                        ? "Execute training expansion"
                                        : "Execute selected queries"}
                                    </button>
                                  )}
                              </div>
                            )}
                            {(plannedQueries?.actions || analysis.query_plan)
                              .slice(0, 6)
                              .map((q: Row, i: number) => (
                                <div className="query-action" key={i}>
                                  <span>{i + 1}</span>
                                  <div>
                                    <strong>
                                      {q.action.replaceAll("_", " ")}
                                    </strong>
                                    <code>{short(q.address, 10)}</code>
                                    <small>
                                      {(
                                        q.reason || q.reasons.join(", ")
                                      ).replaceAll("_", " ")}{" "}
                                      · hop {q.hops}
                                    </small>
                                    {q.status && (
                                      <small>
                                        {q.status.replaceAll("_", " ")} ·{" "}
                                        {q.estimated_calls === null
                                          ? "manual review"
                                          : q.estimated_calls +
                                            " estimated calls"}
                                      </small>
                                    )}
                                  </div>
                                </div>
                              ))}
                            {plannedQueries && (
                              <details>
                                <summary>
                                  Planning assumptions and full queue
                                </summary>
                                <Json value={plannedQueries} />
                              </details>
                            )}
                          </div>
                        </section>
                      </aside>
                    </div>
                  </>
                ))}
              {tab === "Evidence" && (
                <>
                  <div className="section-actions">
                    <div>
                      <h2>Evidence & provenance</h2>
                      <p>
                        Keep source material, submitted claims and reviewed
                        assertions distinguishable.
                      </p>
                    </div>
                    <div className="actions">
                      {canWrite && (
                        <>
                          <button
                            className="button"
                            onClick={() => open("snapshot")}
                          >
                            <Upload size={15} />
                            Import snapshot
                          </button>
                          <button
                            className="button"
                            onClick={() => open("assertion")}
                          >
                            <Plus size={15} />
                            Propose label
                          </button>
                          <button
                            className="button"
                            onClick={() => open("bridge")}
                          >
                            Import bridge proof
                          </button>
                          {job?.request.fixture_scenario === "cctp-review" && (
                            <button
                              className="button"
                              disabled={busy}
                              onClick={() =>
                                perform(async () => {
                                  const fixture = await api<Row>(
                                    "/fixtures/cctp-review",
                                  );
                                  open("bridge", {
                                    proof: fixture.bridge_proofs[0],
                                  });
                                })
                              }
                            >
                              Propose training bridge
                            </button>
                          )}
                        </>
                      )}
                      {analysis && !job?.evidence_changes?.length && (
                        <a
                          className="button primary"
                          href={"/api/analyses/" + job!.id + "/bundle.zip"}
                        >
                          <ArrowDownToLine size={15} />
                          Signed evidence bundle
                        </a>
                      )}
                    </div>
                  </div>
                  {analysis && (
                    <section className="panel">
                      <div className="panel-heading">
                        <h2>Observed transfers</h2>
                        <a
                          className="text-link"
                          href={"/api/analyses/" + job!.id + "/snapshot"}
                        >
                          Download snapshot JSON <ArrowDownToLine size={14} />
                        </a>
                      </div>
                      <div className="scroll-table">
                        <table>
                          <thead>
                            <tr>
                              <th>Transaction / event</th>
                              <th>Sender → recipient</th>
                              <th>Amount</th>
                              <th>Asset / finality</th>
                            </tr>
                          </thead>
                          <tbody>
                            {analysis.graph.events.map((e: Row) => (
                              <tr key={e.id}>
                                <td>
                                  <code>{short(e.txid, 12)}</code>
                                  <small>{date(e.timestamp)}</small>
                                  {e.kind === "bridge" && (
                                    <button
                                      className="text-link"
                                      onClick={() => {
                                        setSelected({ type: "event", ...e });
                                        setTab("Overview");
                                      }}
                                    >
                                      Inspect CCTP delivery
                                    </button>
                                  )}
                                </td>
                                <td>
                                  <code>
                                    {e.senders
                                      .map((s: string) => short(s, 10))
                                      .join(", ")}
                                    <br />→ {short(e.recipient, 12)}
                                  </code>
                                </td>
                                <td>
                                  {amount(e.amount, e.decimals)}
                                  <small>{e.amount} base units</small>
                                </td>
                                <td>
                                  <code>{short(e.asset, 12)}</code>
                                  <small>
                                    {e.finality} · {e.kind}
                                  </small>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </section>
                  )}
                  <section className="panel spaced">
                    <div className="panel-heading">
                      <h2>Case evidence register</h2>
                    </div>
                    {records
                      .filter((r) =>
                        [
                          "snapshot",
                          "assertion",
                          "bridge",
                          "feedback",
                          "withdrawal",
                          "challenge",
                        ].includes(r.kind),
                      )
                      .map((r) => (
                        <div className="record-row" key={r.id}>
                          <div className="record-icon">
                            <Database size={19} />
                          </div>
                          <div className="grow">
                            <strong>
                              {r.assertion?.entity ||
                                r.origin ||
                                (r.kind === "challenge"
                                  ? "Assumption challenge"
                                  : r.kind === "withdrawal"
                                    ? "Evidence withdrawal"
                                    : r.kind === "bridge"
                                      ? "CCTP V2 bridge proof"
                                      : "Signed service response")}
                            </strong>
                            <p>
                              {r.kind} · {date(r.created)}
                            </p>
                            <code>
                              {short(r.sha256 || r.assertion?.address || r.id)}
                            </code>
                          </div>
                          {r.status && (
                            <Tag
                              tone={r.status === "approved" ? "teal" : "amber"}
                            >
                              {r.status}
                            </Tag>
                          )}
                          {reviewButton(r)}
                          {canWrite &&
                            ["assertion", "bridge"].includes(r.kind) &&
                            r.status === "approved" && (
                              <button
                                className="button small"
                                onClick={() => open("withdrawal", r)}
                              >
                                Propose withdrawal
                              </button>
                            )}
                          <details>
                            <summary>Details</summary>
                            <Json value={r} />
                          </details>
                        </div>
                      ))}
                    {!records.some((r) =>
                      [
                        "snapshot",
                        "assertion",
                        "bridge",
                        "feedback",
                        "withdrawal",
                        "challenge",
                      ].includes(r.kind),
                    ) && (
                      <Empty
                        title="No submitted evidence yet"
                        text="Import a normalised snapshot or propose a source-backed service label for independent review."
                      />
                    )}
                  </section>
                  {analysis && (
                    <section className="panel spaced">
                      <div className="panel-heading">
                        <h2>Coverage and interpretation limits</h2>
                      </div>
                      <div className="panel-body">
                        <ul className="limitations">
                          {analysis.limitations.map((l: string, i: number) => (
                            <li key={i}>{l}</li>
                          ))}
                        </ul>
                        <details>
                          <summary>View unresolved branch details</summary>
                          <Json value={analysis.frontiers} />
                        </details>
                      </div>
                    </section>
                  )}
                </>
              )}
              {tab === "Assumptions" && (
                <>
                  <div className="section-actions">
                    <div>
                      <h2>Challenge the attribution</h2>
                      <p>
                        See how the answer changes when a source is excluded.
                        Your original analysis stays unchanged.
                      </p>
                    </div>
                  </div>
                  {analysis ? (
                    <div className="two-columns">
                      <section className="panel">
                        <div className="panel-heading">
                          <h2>Evidence families</h2>
                        </div>
                        <div className="panel-body">
                          {Array.from(
                            new Set<string>([
                              ...analysis.graph.nodes.flatMap((n: Row) =>
                                n.labels.map((a: Row) => a.source_family),
                              ),
                              ...analysis.graph.events
                                .filter((e: Row) => e.bridge_details)
                                .map(
                                  (e: Row) => e.bridge_details.source_family,
                                ),
                            ]),
                          ).map((f) => (
                            <div className="assertion-line" key={f}>
                              <div>
                                <strong>{f}</strong>
                                <p>
                                  Temporarily exclude this source and its
                                  related claims.
                                </p>
                              </div>
                              <button
                                className="button small"
                                onClick={() =>
                                  challengeLabel({ source_family: f })
                                }
                                disabled={busy}
                              >
                                Challenge <GitBranch size={14} />
                              </button>
                            </div>
                          ))}
                          {!analysis.graph.events.some(
                            (e: Row) => e.bridge_details,
                          ) &&
                            !analysis.graph.nodes.some(
                              (n: Row) => n.labels.length,
                            ) && (
                              <p className="muted">
                                There are no attribution assertions to challenge
                                in this result.
                              </p>
                            )}
                          <div className="callout">
                            An opened branch may require more acquisition. The
                            challenge will not invent unseen downstream
                            transfers.
                          </div>
                        </div>
                      </section>
                      <section className="panel">
                        <div className="panel-heading">
                          <h2>Recomputed outcome</h2>
                        </div>
                        {challengeResult ? (
                          <div className="panel-body">
                            <Tag
                              tone={
                                challengeResult.requires_expansion
                                  ? "amber"
                                  : "teal"
                              }
                            >
                              {challengeResult.requires_expansion
                                ? "More evidence required"
                                : "Recomputed on existing evidence"}
                            </Tag>
                            <h3>
                              {challengeResult.removed_candidates.length}{" "}
                              custody path(s) removed
                            </h3>
                            <p>
                              Excluded: {challengeResult.excluded.join(", ")}
                            </p>
                            <p>
                              Nearest evidenced custody:{" "}
                              {challengeResult.result.certificate
                                .nearest_evidenced_hops ?? "No answer"}{" "}
                              hops.
                            </p>
                            <details>
                              <summary>
                                View changed paths and unresolved branches
                              </summary>
                              <Json
                                value={{
                                  removed: challengeResult.removed_candidates,
                                  added: challengeResult.added_candidates,
                                  unresolved: challengeResult.result.query_plan,
                                }}
                              />
                            </details>
                          </div>
                        ) : (
                          <Empty
                            title="Test what the answer depends on"
                            text="Choose a source family to see which findings survive its removal."
                            icon={<GitBranch size={30} />}
                          />
                        )}
                      </section>
                    </div>
                  ) : (
                    <Empty
                      title="Run an analysis first"
                      text="An immutable analysis snapshot is needed to compare assumptions."
                    />
                  )}
                </>
              )}
              {tab === "Requests" && (
                <>
                  <div className="section-actions">
                    <div>
                      <h2>Reviewed action packages</h2>
                      <p>
                        Prepare a request, obtain independent review, then
                        export the exact approved payload.
                      </p>
                    </div>
                    <div className="actions">
                      {canWrite && (
                        <>
                          <button
                            className="button"
                            onClick={() => open("feedback")}
                          >
                            <Upload size={15} />
                            Import signed response
                          </button>
                          <button
                            className="button primary"
                            disabled={
                              !analysis?.candidates.length ||
                              !!job?.evidence_changes?.length
                            }
                            onClick={() => open("request")}
                          >
                            <Plus size={16} />
                            Prepare request
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                  <div className="callout">
                    <LockKeyhole size={18} />
                    <span>
                      SAHYOG is not connected. Exporting a package does not send
                      a notice, freeze assets, or establish acceptance by a
                      VASP.
                    </span>
                  </div>
                  <section className="panel spaced">
                    {records
                      .filter((r) => r.kind === "request")
                      .map((r) => (
                        <div className="record-row" key={r.id}>
                          <FileCheck2 size={22} />
                          <div className="grow">
                            <strong>{r.body.candidate.entity}</strong>
                            <p>
                              {r.body.type.replaceAll("_", " ")} ·{" "}
                              {date(r.created)} · {r.body.mode}
                            </p>
                            <code>{short(r.body_sha256)}</code>
                          </div>
                          <Tag
                            tone={r.status === "approved" ? "teal" : "amber"}
                          >
                            {r.status}
                          </Tag>
                          {reviewButton(r)}
                          {r.status === "approved" && (
                            <a
                              className="button small"
                              href={"/api/requests/" + r.id + "/export"}
                            >
                              Export <ArrowDownToLine size={14} />
                            </a>
                          )}
                          <details>
                            <summary>Details</summary>
                            <Json value={r} />
                          </details>
                        </div>
                      ))}
                    {!records.some((r) => r.kind === "request") && (
                      <Empty
                        title="No requests prepared"
                        text="A supported custody candidate and a reviewed, current recipient entry are required. Add recipient evidence in the VASP directory."
                        icon={<Landmark size={30} />}
                      />
                    )}
                  </section>
                </>
              )}
              {tab === "Monitoring" && (
                <>
                  <div className="section-actions">
                    <div>
                      <h2>Wallet monitoring</h2>
                      <p>
                        Bounded live re-analysis while this installation is
                        running. Alerts stay within the case.
                      </p>
                    </div>
                    {canWrite && (
                      <button
                        className="button primary"
                        onClick={() => open("watch")}
                      >
                        <Plus size={16} />
                        Add watch
                      </button>
                    )}
                  </div>
                  <section className="panel">
                    {records
                      .filter((r) => r.kind === "watch")
                      .map((r) => (
                        <div className="record-row" key={r.id}>
                          <Bell size={21} />
                          <div className="grow">
                            <strong>
                              {labels[r.spec.chain]} · {short(r.spec.address)}
                            </strong>
                            <p>
                              Every {r.interval_minutes} minutes ·{" "}
                              {r.spec.max_requests} calls maximum per analysis
                            </p>
                            <small>
                              Next scheduled check: {date(r.next_run)}
                            </small>
                          </div>
                          <Tag tone={r.enabled ? "teal" : ""}>
                            {r.enabled ? "Enabled" : "Paused"}
                          </Tag>
                          {canWrite && (
                            <button
                              className="button small"
                              onClick={() =>
                                perform(async () => {
                                  await post("/watches/" + r.id + "/toggle");
                                  await refreshCase(current.id);
                                })
                              }
                            >
                              {r.enabled ? "Pause" : "Enable"}
                            </button>
                          )}
                        </div>
                      ))}
                    {!records.some((r) => r.kind === "watch") && (
                      <Empty
                        title="No active watches"
                        text="Add a wallet and a bounded query budget. Data or provider-access limitations are included in each result."
                        icon={<Bell size={30} />}
                      />
                    )}
                  </section>
                  <h2 className="spaced">Case alerts</h2>
                  {records
                    .filter((r) => r.kind === "alert")
                    .map((r) => (
                      <div className="callout" key={r.id}>
                        <Bell size={18} />
                        <div>
                          {r.message}
                          <small>{date(r.created)}</small>
                        </div>
                      </div>
                    ))}
                  {!records.some((r) => r.kind === "alert") && (
                    <p className="muted">
                      No change alerts have been recorded.
                    </p>
                  )}
                </>
              )}
              {tab === "Audit trail" && (
                <section className="panel">
                  <div className="panel-heading">
                    <h2>Case activity</h2>
                    <button
                      className="button small"
                      onClick={() => perform(() => refreshCase(current.id))}
                    >
                      Refresh
                    </button>
                  </div>
                  <div className="audit-note">
                    Database audit trail. External immutable retention and
                    agency signing are production deployment requirements.
                  </div>
                  {audit.map((a) => (
                    <div className="audit-row" key={a.id}>
                      <span className="audit-dot" />
                      <div>
                        <strong>{a.action.replaceAll(".", " / ")}</strong>
                        <p>
                          {users.find((u) => u.id === a.actor)?.name || a.actor}
                        </p>
                        <details>
                          <summary>Event details</summary>
                          <Json value={a.details} />
                        </details>
                      </div>
                      <time>{date(a.created)}</time>
                    </div>
                  ))}
                </section>
              )}
            </>
          )}

          {view === "directory" && (
            <>
              <div className="page-heading">
                <div>
                  <span className="eyebrow">LAWFUL REQUEST ROUTING</span>
                  <h1>VASP directory</h1>
                  <p>
                    Verified recipient channels and signing keys, with explicit
                    review and expiry.
                  </p>
                </div>
                {canWrite && (
                  <button
                    className="button primary"
                    onClick={() => open("recipient")}
                  >
                    <Plus size={16} />
                    Propose recipient
                  </button>
                )}
              </div>
              <div className="callout">
                <ShieldCheck size={20} />
                <span>
                  Recipient details must come from an authorised source. No
                  contact address or government integration is guessed or
                  pre-populated.
                </span>
              </div>
              <section className="panel spaced">
                {recipients.length ? (
                  recipients.map((r) => (
                    <div className="record-row" key={r.id}>
                      <span className="directory-icon">
                        <Landmark size={23} />
                      </span>
                      <div className="grow">
                        <strong>{r.entity}</strong>
                        <Tag tone={r.mode === "operational" ? "blue" : "amber"}>
                          {r.mode || "unclassified purpose"}
                        </Tag>
                        <p>
                          {r.jurisdiction} · {r.channel}
                        </p>
                        <small>Verification expires {date(r.expires_at)}</small>
                      </div>
                      <Tag
                        tone={
                          r.status === "approved" &&
                          r.expires_at * 1000 > Date.now()
                            ? "teal"
                            : "amber"
                        }
                      >
                        {r.expires_at * 1000 < Date.now()
                          ? "expired"
                          : r.status}
                      </Tag>
                      {reviewButton(r)}
                      <details>
                        <summary>Verification evidence</summary>
                        <p>{r.verification_source}</p>
                        <code>
                          {r.signing_public_key ||
                            "No response signing key registered"}
                        </code>
                      </details>
                    </div>
                  ))
                ) : (
                  <Empty
                    title="Build a verified routing directory"
                    text="Propose the legal entity, jurisdiction, delivery channel and verification source. A separate reviewer must approve the entry before use."
                    icon={<Landmark size={34} />}
                  />
                )}
              </section>
            </>
          )}
          {view === "verify" && (
            <>
              <div className="page-heading">
                <div>
                  <span className="eyebrow">PORTABLE EVIDENCE</span>
                  <h1>Verify an evidence bundle</h1>
                  <p>
                    Check the signature, every member hash, and deterministic
                    analysis replay.
                  </p>
                </div>
              </div>
              <div className="two-columns">
                <section className="panel">
                  <div className="panel-body">
                    <div className="upload-illustration">
                      <FileCheck2 size={42} />
                    </div>
                    <h2>Drop in a TraceSetu evidence bundle</h2>
                    <p className="muted">
                      Select the signed ZIP exported from an investigation.
                      Verification is performed locally by this installation.
                    </p>
                    <form
                      onSubmit={(e) => {
                        e.preventDefault();
                        const data = new FormData(e.currentTarget);
                        perform(async () =>
                          setVerified(
                            await api("/evidence/verify", {
                              method: "POST",
                              body: data,
                            }),
                          ),
                        );
                      }}
                    >
                      <Field label="Evidence ZIP (maximum 10 MB)">
                        <input type="file" name="file" accept=".zip" required />
                      </Field>
                      <button className="button primary" disabled={busy}>
                        {busy ? (
                          <LoaderCircle className="spin" size={16} />
                        ) : (
                          <ShieldCheck size={16} />
                        )}
                        Verify bundle
                      </button>
                    </form>
                  </div>
                </section>
                <section className="panel">
                  <div className="panel-heading">
                    <h2>Verification result</h2>
                  </div>
                  {verified ? (
                    <div className="panel-body">
                      <Tag tone="teal">
                        <Check size={13} />
                        Integrity valid · replay matched
                      </Tag>
                      <p>{verified.files} evidence files checked.</p>
                      <Field label="Signer fingerprint">
                        <code className="block-code">
                          {verified.signer_sha256}
                        </code>
                      </Field>
                      <div className="callout">
                        A cryptographically valid bundle does not establish the
                        signer's identity. Confirm this fingerprint through a
                        trusted channel. Provider claims still need evidential
                        review.
                      </div>
                      <Tag tone="amber">{verified.mode}</Tag>
                    </div>
                  ) : (
                    <Empty
                      title="No bundle checked yet"
                      text="Upload a signed bundle to check its files and replay the analysis. Ownership claims still require review."
                      icon={<ShieldCheck size={30} />}
                    />
                  )}
                </section>
              </div>
            </>
          )}
          {view === "system" && (
            <>
              <div className="page-heading">
                <div>
                  <span className="eyebrow">CAPABILITY REGISTER</span>
                  <h1>Data & coverage</h1>
                  <p>
                    Implementation, configuration and real-world validation are
                    separate states.
                  </p>
                </div>
                <button
                  className="button"
                  onClick={() => perform(refreshGlobals)}
                >
                  Refresh status
                </button>
              </div>
              <section className="panel">
                <div className="panel-heading">
                  <h2>Blockchain acquisition</h2>
                  <Tag>6 chain adapters</Tag>
                </div>
                <div className="scroll-table">
                  <table>
                    <thead>
                      <tr>
                        <th>Chain</th>
                        <th>Source</th>
                        <th>Configured</th>
                        <th>Full validation</th>
                        <th>Coverage</th>
                      </tr>
                    </thead>
                    <tbody>
                      {caps?.chains.map((c: Row) => (
                        <tr key={c.chain}>
                          <td>
                            <strong>{labels[c.chain]}</strong>
                          </td>
                          <td>{c.provider}</td>
                          <td>
                            <Tag tone={c.configured ? "teal" : "amber"}>
                              {c.configured ? "Yes" : "Key required"}
                            </Tag>
                          </td>
                          <td>
                            <Tag tone="amber">
                              {c.live_validated ? "Validated" : "Pending"}
                            </Tag>
                          </td>
                          <td>{c.coverage}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
              {caps?.cross_chain && (
                <section className="panel spaced">
                  <div className="panel-heading">
                    <h2>Cross-chain protocol coverage</h2>
                    <Tag tone="amber">Live validation pending</Tag>
                  </div>
                  <div className="panel-body">
                    <strong>
                      {caps.cross_chain.protocol} · {caps.cross_chain.scope}
                    </strong>
                    <p>{caps.cross_chain.status}</p>
                    <p>
                      Read-only acquisition:{" "}
                      {caps.cross_chain.configured
                        ? "enabled with a configured key"
                        : "disabled or provider key missing"}
                      . Reviewed proof import is available.
                    </p>
                  </div>
                </section>
              )}
              <div className="two-columns spaced">
                <section className="panel">
                  <div className="panel-heading">
                    <h2>Attribution data</h2>
                  </div>
                  <div className="panel-body">
                    <p>{caps?.identity_data}</p>
                    <p className="muted">
                      Transaction access alone does not identify a wallet's
                      operator. Source-backed assertions require provenance and
                      case review.
                    </p>
                  </div>
                </section>
                <section className="panel">
                  <div className="panel-heading">
                    <h2>SAHYOG integration</h2>
                    <Tag tone="amber">Not connected</Tag>
                  </div>
                  <div className="panel-body">
                    <p>{caps?.sahyog.status}</p>
                    <p className="muted">
                      No automated freezing capability or delivery
                      acknowledgement is claimed.
                    </p>
                  </div>
                </section>
              </div>
              <div className="callout spaced">
                <Activity size={18} />
                <span>{caps?.runtime}</span>
              </div>
            </>
          )}
          {view === "account" && (
            <>
              <div className="page-heading">
                <div>
                  <span className="eyebrow">WORKSPACE ACCESS</span>
                  <h1>Account & team</h1>
                  <p>
                    {user.name} · {user.role}
                  </p>
                </div>
                <div className="actions">
                  <button className="button" onClick={() => open("password")}>
                    <LockKeyhole size={15} />
                    Change password
                  </button>
                  <button
                    className="button"
                    onClick={() =>
                      perform(async () => {
                        await post("/auth/logout");
                        clearSession();
                      })
                    }
                  >
                    <LogOut size={15} />
                    Sign out
                  </button>
                </div>
              </div>
              <section className="panel">
                <div className="panel-heading">
                  <h2>Agency users</h2>
                  {user.role === "admin" && (
                    <button
                      className="button primary small"
                      onClick={() => open("user")}
                    >
                      <Plus size={14} />
                      Add user
                    </button>
                  )}
                </div>
                {users.map((u) => (
                  <div className="record-row" key={u.id}>
                    <div className="avatar light">{u.name.slice(0, 1)}</div>
                    <div className="grow">
                      <strong>{u.name}</strong>
                      <p>{u.username}</p>
                    </div>
                    <Tag>{u.role}</Tag>
                  </div>
                ))}
              </section>
            </>
          )}
        </main>
        <footer className="page-footer">
          <span>TraceSetu · Follow the funds. Find the receiving service.</span>
          <span>Unknown ownership remains unknown.</span>
        </footer>
      </div>

      {modal && (
        <div
          className="modal-overlay"
          role="presentation"
          onMouseDown={(e) => {
            if (e.target === e.currentTarget && !busy) setModal(null);
          }}
        >
          <section
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-title"
          >
            <div className="modal-heading">
              <div>
                <span className="eyebrow">TRACESETU</span>
                <h2 id="modal-title">
                  {
                    {
                      case: target
                        ? "Manage investigation"
                        : "New investigation",
                      analysis: "Analyse a reported wallet",
                      snapshot: "Import an evidence snapshot",
                      assertion: "Propose a service label",
                      bridge: "Submit a CCTP V2 bridge proof",
                      recipient: "Propose a VASP recipient",
                      request: "Prepare a reviewed request",
                      review: "Independent evidence review",
                      watch: "Monitor a reported wallet",
                      feedback: "Import a signed service response",
                      withdrawal: "Propose an evidence withdrawal",
                      plan: "Budget the next evidence queries",
                      execute_plan: "Execute the selected evidence queries",
                      user: "Add an agency user",
                      password: "Change your password",
                    }[modal]
                  }
                </h2>
              </div>
              <button
                className="icon-button"
                aria-label="Close dialog"
                onClick={() => setModal(null)}
                disabled={busy}
              >
                <X size={20} />
              </button>
            </div>
            <form onSubmit={submit}>
              <div className="modal-body">
                {modal === "case" && (
                  <>
                    {field("title", "Case title", {
                      placeholder: "e.g. Reported investment fraud",
                      defaultValue: target?.title,
                    })}
                    {field("reference", "Agency case reference", {
                      placeholder: "Your authorised reference",
                      defaultValue: target?.reference,
                    })}
                    <Field label="Description">
                      <textarea
                        name="description"
                        rows={3}
                        defaultValue={target?.description}
                      />
                    </Field>
                    <Field label="Classification">
                      <select
                        name="classification"
                        defaultValue={target?.classification || "Restricted"}
                      >
                        <option>Restricted</option>
                        <option>Confidential</option>
                      </select>
                    </Field>
                    {target && (
                      <Field label="Case status">
                        <select name="status" defaultValue={target.status}>
                          <option>Open</option>
                          <option>Under review</option>
                          <option>Closed</option>
                        </select>
                      </Field>
                    )}
                    <Field label="Case members">
                      <div className="member-list">
                        {users
                          .filter((u) => u.id !== user.id)
                          .map((u) => (
                            <label key={u.id}>
                              <input
                                type="checkbox"
                                name="members"
                                value={u.id}
                                defaultChecked={target?.members.includes(u.id)}
                              />
                              {u.name}
                              <small>{u.role}</small>
                            </label>
                          ))}
                      </div>
                    </Field>
                    <p className="muted">
                      You will be added automatically. Add a reviewer to enable
                      independent case approvals.
                    </p>
                  </>
                )}
                {modal === "analysis" && (
                  <>
                    <Field label="Evidence mode">
                      <select
                        value={mode}
                        onChange={(e) => setMode(e.target.value)}
                      >
                        <option value="live">Live provider acquisition</option>
                        <option value="imported">
                          Imported evidence snapshot
                        </option>
                        <option value="fixture">
                          Synthetic training scenario
                        </option>
                      </select>
                    </Field>
                    {mode === "live" ? (
                      specFields
                    ) : mode === "imported" ? (
                      <>
                        <Field label="Imported snapshot">
                          <select name="snapshot_id" required>
                            <option value="">Select a case snapshot</option>
                            {records
                              .filter((r) => r.kind === "snapshot")
                              .map((r) => (
                                <option key={r.id} value={r.id}>
                                  {r.origin} · {r.event_count} events
                                </option>
                              ))}
                          </select>
                        </Field>
                        <div className="form-grid">
                          {chainField}
                          {field("address", "Seed address in snapshot")}
                        </div>
                      </>
                    ) : (
                      <>
                        <div className="callout">
                          Training uses invented transactions and services. It
                          is explicitly marked in every result and export.
                        </div>
                        <Field label="Training scenario">
                          <select name="fixture_scenario">
                            <option value="custody">
                              Custody frontier and uncertainty
                            </option>
                            <option value="cctp-review">
                              CCTP bridge with independent review
                            </option>
                          </select>
                        </Field>
                        <input name="chain" type="hidden" value="ethereum" />
                        <input
                          name="start"
                          type="hidden"
                          value="2025-06-15T00:00"
                        />
                        <input
                          name="end"
                          type="hidden"
                          value="2025-06-16T00:00"
                        />
                      </>
                    )}
                    {budgetFields}
                    <p className="muted">
                      The engine stops at the first custody boundary on each
                      path. Budgets can leave unresolved branches; these will be
                      recorded.
                    </p>
                  </>
                )}
                {modal === "snapshot" && (
                  <>
                    <Field label="Normalised snapshot JSON">
                      <input type="file" accept=".json" name="file" required />
                    </Field>
                    <Field label="Source, collection method and permission">
                      <textarea
                        name="provenance"
                        minLength={10}
                        required
                        rows={4}
                      />
                    </Field>
                    <div className="callout">
                      The file must match the versioned Snapshot schema in the
                      API. Imported labels begin as hypotheses. Imports never
                      masquerade as live acquisition.
                    </div>
                  </>
                )}
                {modal === "bridge" && (
                  <>
                    <div className="callout">
                      Checks protocol bytes, signatures and both transaction
                      receipts for native USDC between Ethereum and Polygon. A
                      reviewer must establish the origin of the receipts and
                      attester keys. Cryptographic consistency alone does not
                      authenticate Circle.
                    </div>
                    <Field label="Bridge evidence purpose">
                      <select
                        name="mode"
                        defaultValue={
                          target?.proof || job?.request.mode === "fixture"
                            ? "training"
                            : "operational"
                        }
                      >
                        <option value="operational">
                          Operational evidence
                        </option>
                        <option value="training">
                          Synthetic training evidence
                        </option>
                      </select>
                    </Field>
                    {target?.proof ? (
                      <>
                        <p>
                          SYNTHETIC: locally signed test proof, never acquired
                          from Circle.
                        </p>
                        <details>
                          <summary>Training proof JSON</summary>
                          <Json value={target.proof} />
                        </details>
                      </>
                    ) : (
                      <Field label="Bridge proof JSON">
                        <input
                          type="file"
                          name="file"
                          accept=".json"
                          required
                        />
                      </Field>
                    )}
                    <Field label="Proof provenance and verification performed">
                      <textarea
                        name="rationale"
                        required
                        minLength={10}
                        maxLength={3000}
                        rows={4}
                      />
                    </Field>
                  </>
                )}
                {modal === "assertion" && (
                  <>
                    <div className="form-grid">
                      {chainField}
                      {field("address", "Wallet address")}
                    </div>
                    {field("entity", "Legal entity or service name")}
                    <div className="form-grid">
                      <Field label="Service category">
                        <select name="category">
                          {[
                            "exchange",
                            "custodian",
                            "mixer",
                            "bridge",
                            "defi",
                            "unknown",
                          ].map((c) => (
                            <option key={c}>{c}</option>
                          ))}
                        </select>
                      </Field>
                      <Field label="Wallet role">
                        <select name="role">
                          {[
                            "unknown",
                            "deposit",
                            "hot",
                            "cluster",
                            "contract",
                          ].map((c) => (
                            <option key={c}>{c}</option>
                          ))}
                        </select>
                      </Field>
                    </div>
                    {field("source_family", "Original provenance family", {
                      placeholder: "Group sources that share the same origin",
                    })}
                    {field("source", "Source reference / URL")}
                    {field(
                      "evidence",
                      "Evidence document identifier or SHA-256",
                    )}
                    {field(
                      "risk_tags",
                      "Risk tags (optional, comma separated)",
                      { required: false },
                    )}
                    <Field label="Attribution rationale">
                      <textarea
                        name="rationale"
                        minLength={10}
                        required
                        rows={3}
                      />
                    </Field>
                    <div className="callout">
                      This creates a hypothesis for independent review. A
                      reviewed grade is an evidence category, not a probability.
                    </div>
                  </>
                )}
                {modal === "recipient" && (
                  <>
                    <Field label="Directory purpose">
                      <select name="mode" defaultValue="operational">
                        <option value="operational">
                          Operational investigation recipient
                        </option>
                        <option value="training">
                          Synthetic training recipient
                        </option>
                      </select>
                    </Field>
                    {field("entity", "Exact service / legal entity name")}
                    <div className="form-grid">
                      {field("jurisdiction", "Jurisdiction")}
                      {field("expires_at", "Verification expiry (UTC)", {
                        type: "datetime-local",
                        defaultValue: utcInput(Date.now() + 90 * 86400000),
                      })}
                    </div>
                    {field("channel", "Authorised delivery channel")}
                    <Field label="Verification source and method">
                      <textarea
                        name="verification_source"
                        minLength={10}
                        required
                        rows={3}
                      />
                    </Field>
                    {field(
                      "signing_public_key",
                      "Ed25519 response public key (Base64, optional)",
                      { required: false },
                    )}
                    <div className="callout">
                      A second reviewer must validate the recipient and key
                      identity before this entry can be used.
                    </div>
                  </>
                )}
                {modal === "request" && (
                  <>
                    <Field label="Evidenced custody candidate">
                      <select name="candidate_index" required>
                        {analysis?.candidates.map(
                          (c: Row, i: number) =>
                            c.status === "evidenced" && (
                              <option key={i} value={i}>
                                {c.entity} · {c.hops} hops ·{" "}
                                {short(c.address, 10)}
                              </option>
                            ),
                        )}
                      </select>
                    </Field>
                    <Field label="Reviewed recipient">
                      <select name="recipient_id" required>
                        <option value="">
                          Choose matching verified entity
                        </option>
                        {recipients
                          .filter(
                            (r) =>
                              r.status === "approved" &&
                              r.mode ===
                                (job?.request.mode === "fixture"
                                  ? "training"
                                  : "operational"),
                          )
                          .map((r) => (
                            <option key={r.id} value={r.id}>
                              {r.entity} · {r.jurisdiction}
                            </option>
                          ))}
                      </select>
                    </Field>
                    <Field label="Request purpose">
                      <select name="type">
                        <option value="disclosure">Disclosure request</option>
                        <option value="preservation">
                          Preservation request
                        </option>
                        <option value="freezing_review">
                          Asset-freezing request for legal review
                        </option>
                      </select>
                    </Field>
                    <Field label="Applicable legal authority / basis">
                      <textarea
                        name="legal_basis"
                        minLength={10}
                        required
                        rows={3}
                      />
                    </Field>
                    <Field label="Specific scope, period and requested records">
                      <textarea name="scope" minLength={10} required rows={3} />
                    </Field>
                    <div className="callout">
                      Saving creates a pending package. A different reviewer
                      must approve its exact content before export. No external
                      delivery occurs.
                    </div>
                  </>
                )}
                {modal === "review" && (
                  <>
                    <div className="review-payload">
                      <Json value={target} />
                    </div>
                    <Field label="Decision">
                      <select name="decision">
                        <option value="approve">
                          Approve the reviewed evidence
                        </option>
                        <option value="reject">Reject</option>
                      </select>
                    </Field>
                    <Field label="Review rationale and verification performed">
                      <textarea
                        name="rationale"
                        rows={4}
                        minLength={10}
                        required
                      />
                    </Field>
                    <div className="callout">
                      Your decision is recorded against this version. Approval
                      must be based on your independent review of the evidence
                      and authority.
                    </div>
                  </>
                )}
                {modal === "watch" && (
                  <>
                    {specFields}
                    {budgetFields}
                    {field("interval_minutes", "Check interval (minutes)", {
                      type: "number",
                      min: 15,
                      max: 10080,
                      defaultValue: 60,
                    })}
                    <div className="callout">
                      Each run extends the window to the current time and
                      consumes up to the selected provider budget. No external
                      notification is sent.
                    </div>
                  </>
                )}
                {modal === "withdrawal" && (
                  <>
                    <p>
                      Withdraw the reviewed evidence for{" "}
                      {target?.assertion?.entity || "this CCTP bridge"}. A
                      different reviewer must approve this change. Prior
                      evidence stays intact and affected analyses require
                      reassessment.
                    </p>
                    <Field label="Reason and supporting evidence">
                      <textarea
                        name="rationale"
                        required
                        minLength={10}
                        maxLength={3000}
                        rows={5}
                      />
                    </Field>
                  </>
                )}
                {modal === "plan" && (
                  <>
                    {field("budget_requests", "HTTP request budget", {
                      type: "number",
                      min: 1,
                      max: 200,
                      defaultValue: job?.request.spec.max_requests || 30,
                    })}
                    <p>
                      The plan uses adapter endpoint counts and previously
                      observed pagination. It will show unavailable providers
                      and manual reviews separately. This action records an
                      advisory plan; it does not call blockchain providers.
                    </p>
                  </>
                )}
                {modal === "execute_plan" && target && (
                  <>
                    <p>
                      Create a new analysis from the selected scopes below. The
                      parent analysis remains available.
                    </p>
                    <div className="callout">
                      {target.mode === "fixture"
                        ? "TRAINING ONLY: adds an invented example transfer with zero HTTP calls."
                        : "Calls configured blockchain providers. Entitlements and billed units are not established by local configuration."}
                    </div>
                    <p>
                      <strong>
                        Hard budget: {target.budget_requests} request slots
                        across all selected scopes and recovery attempts.
                      </strong>{" "}
                      Estimated allocation: {target.selected_estimated_requests}
                      . Incomplete scopes remain explicit.
                    </p>
                    {target.actions
                      .filter(
                        (a: Row) =>
                          a.status === "selected_estimate" &&
                          a.action === "reacquire_history",
                      )
                      .map((a: Row) => (
                        <p key={a.chain + a.address}>
                          <strong>{labels[a.chain]}</strong>
                          <br />
                          <code>{a.address}</code>
                          <br />
                          {a.estimated_calls} estimated requests
                        </p>
                      ))}
                    <details>
                      <summary>Bound plan and parent analysis</summary>
                      <p>{job?.id}</p>
                      <code>{target.sha256}</code>
                    </details>
                  </>
                )}
                {modal === "feedback" && (
                  <>
                    <Field label="Approved request">
                      <select name="request_id" required>
                        {records
                          .filter(
                            (r) =>
                              r.kind === "request" && r.status === "approved",
                          )
                          .map((r) => (
                            <option key={r.id} value={r.id}>
                              {r.body.candidate.entity} · {r.id}
                            </option>
                          ))}
                      </select>
                    </Field>
                    <Field label="Signed response JSON">
                      <textarea
                        name="payload"
                        required
                        rows={7}
                        placeholder={
                          '{"request_id":"...","request_sha256":"...","findings":{}}'
                        }
                      />
                    </Field>
                    {field("signature", "Ed25519 signature (Base64)")}
                    <div className="callout">
                      The response must bind to the approved request ID and
                      payload hash. A verified recipient key and a separate
                      review are required. A structured
                      atlas.service-response.v1 attestation can promote only the
                      requested wallet and entity, within its stated validity
                      interval. Unstructured findings never create a label.
                    </div>
                  </>
                )}
                {modal === "user" && (
                  <>
                    {field("username", "Username", {
                      pattern: "[a-zA-Z0-9_.-]{3,100}",
                    })}
                    {field("display_name", "Display name")}
                    {field("password", "Initial password", {
                      type: "password",
                      minLength: 14,
                      autoComplete: "new-password",
                    })}
                    <Field label="Role">
                      <select name="role">
                        <option>investigator</option>
                        <option>reviewer</option>
                        <option>admin</option>
                      </select>
                    </Field>
                  </>
                )}
                {modal === "password" && (
                  <>
                    {field("current", "Current password", {
                      type: "password",
                      autoComplete: "current-password",
                    })}
                    {field(
                      "password",
                      "New password (at least 14 characters)",
                      {
                        type: "password",
                        minLength: 14,
                        autoComplete: "new-password",
                      },
                    )}
                    <p className="muted">
                      Changing your password ends all your current sessions.
                    </p>
                  </>
                )}
                {error && (
                  <div className="error" role="alert">
                    {error}
                  </div>
                )}
              </div>
              <div className="modal-footer">
                <button
                  className="button"
                  type="button"
                  onClick={() => setModal(null)}
                  disabled={busy}
                >
                  Cancel
                </button>
                <button className="button primary" disabled={busy}>
                  {busy ? (
                    <LoaderCircle size={16} className="spin" />
                  ) : (
                    <Check size={16} />
                  )}
                  {modal === "analysis"
                    ? "Start analysis"
                    : modal === "execute_plan"
                      ? "Start selected queries"
                      : modal === "review"
                        ? "Record decision"
                        : "Save"}
                </button>
              </div>
            </form>
          </section>
        </div>
      )}
    </div>
  );
}
