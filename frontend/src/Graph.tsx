import { useEffect, useRef, useState } from "react";
import cytoscape from "cytoscape";
import { Maximize2, Plus, Minus, Network } from "lucide-react";
import { type Row, short, amount } from "./api";

export function FundGraph({
  graph,
  onSelect,
}: {
  graph: Row;
  onSelect: (row: Row) => void;
}) {
  const container = useRef<HTMLDivElement>(null);
  const cy = useRef<cytoscape.Core | null>(null);
  const [layout, setLayout] = useState("paths");
  const selectRef = useRef(onSelect);
  selectRef.current = onSelect;
  useEffect(() => {
    if (!container.current) return;
    const nodes = new Map<string, Row>();
    graph.nodes.forEach((n: Row) =>
      nodes.set(n.id, {
        data: {
          ...n,
          label:
            (n.labels[0]?.entity ||
              (n.seed ? "Reported wallet" : short(n.address, 9))) +
            "\n" +
            n.chain,
        },
        classes: n.seed
          ? "seed"
          : n.labels.some((a: Row) => a.category === "mixer")
            ? "risk"
            : n.labels.some((a: Row) =>
                  ["exchange", "custodian"].includes(a.category),
                )
              ? "custody"
              : "unknown",
      }),
    );
    const edges: Row[] = [];
    graph.events.forEach((e: Row) => {
      const target = `${e.destination_chain || e.chain}:${e.recipient}`;
      if (!nodes.has(target))
        nodes.set(target, {
          data: {
            id: target,
            label: short(e.recipient, 9),
            address: e.recipient,
            chain: e.destination_chain || e.chain,
            labels: [],
          },
          classes: "unknown",
        });
      if (e.kind === "utxo") {
        const tx = `tx:${e.txid}`;
        nodes.set(tx, {
          data: { ...e, id: tx, label: "UTXO transaction" },
          classes: "transaction",
        });
        e.senders.forEach((s: string) => {
          const id = `${e.chain}:${s}`;
          if (!nodes.has(id))
            nodes.set(id, {
              data: {
                id,
                label: short(s, 9),
                address: s,
                chain: e.chain,
                labels: [],
              },
              classes: "unknown",
            });
          if (!edges.some((x) => x.data.id === `${tx}:${id}`))
            edges.push({
              data: {
                id: `${tx}:${id}`,
                source: id,
                target: tx,
                label: "input",
                event: e,
              },
              classes: "possible",
            });
        });
        edges.push({
          data: {
            id: e.id,
            source: tx,
            target,
            label: `${amount(e.amount, e.decimals)} BTC`,
            event: e,
          },
          classes: "possible",
        });
      } else
        e.senders.forEach((s: string, i: number) => {
          const source = `${e.chain}:${s}`;
          if (!nodes.has(source))
            nodes.set(source, {
              data: { id: source, label: short(s, 9), labels: [] },
              classes: "unknown",
            });
          edges.push({
            data: {
              id: e.id + ":" + i,
              source,
              target,
              label:
                e.kind === "bridge"
                  ? `${amount(e.amount, e.decimals)} USDC · CCTP`
                  : amount(e.amount, e.decimals) +
                    (e.asset.endsWith(":native") ? " native" : " token"),
              event: e,
            },
            classes: e.kind === "bridge" ? "bridge" : "",
          });
        });
    });
    const levels = new Map<string, number>();
    const queue = [...nodes.values()]
      .filter((n) => n.data.seed)
      .map((n) => n.data.id as string);
    for (const id of queue) levels.set(id, 0);
    for (let i = 0; i < queue.length; i++)
      for (const edge of edges.filter((e) => e.data.source === queue[i])) {
        if (!levels.has(edge.data.target)) {
          levels.set(edge.data.target, levels.get(queue[i])! + 1);
          queue.push(edge.data.target);
        }
      }
    const columns = new Map<number, Row[]>();
    for (const node of nodes.values()) {
      const d = levels.get(node.data.id) ?? 0;
      columns.set(d, [...(columns.get(d) || []), node]);
    }
    for (const [depth, column] of columns)
      column.forEach((n, i) => {
        n.position = { x: depth * 220, y: (i - (column.length - 1) / 2) * 100 };
      });
    const instance = cytoscape({
      container: container.current,
      elements: [...nodes.values(), ...edges] as any,
      minZoom: 0.25,
      maxZoom: 2.5,
      wheelSensitivity: 0.18,
      style: [
        {
          selector: "node",
          style: {
            "background-color": "#e7e9e5",
            width: 38,
            height: 38,
            label: "data(label)",
            color: "#354640",
            "font-size": 12,
            "font-family": "Segoe UI, Arial, sans-serif",
            "text-valign": "bottom",
            "text-margin-y": 10,
            "text-wrap": "wrap",
            "text-max-width": "125px",
            "border-width": 2,
            "border-color": "#a5ada7",
          },
        },
        {
          selector: ".seed",
          style: {
            "background-color": "#385970",
            "border-color": "#385970",
            width: 46,
            height: 46,
          },
        },
        {
          selector: ".custody",
          style: {
            "background-color": "#e1ecdf",
            "border-color": "#628768",
            shape: "round-rectangle",
            width: 46,
            height: 46,
          },
        },
        {
          selector: ".risk",
          style: {
            "background-color": "#f4e6cc",
            "border-color": "#af8a4d",
            shape: "diamond",
            width: 44,
            height: 44,
          },
        },
        {
          selector: ".transaction",
          style: {
            shape: "rectangle",
            "background-color": "#d5dce5",
            width: 20,
            height: 20,
          },
        },
        {
          selector: "edge",
          style: {
            width: 1.5,
            "line-color": "#a2aca7",
            "target-arrow-color": "#7e8e83",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            label: "data(label)",
            "font-size": 11,
            color: "#546358",
            "text-background-color": "#fcfcfa",
            "text-background-opacity": 1,
            "text-background-padding": "3px",
            "text-rotation": "autorotate",
          },
        },
        { selector: ".possible", style: { "line-style": "dashed" } },
        {
          selector: "edge.bridge",
          style: {
            "line-color": "#7b7493",
            "target-arrow-color": "#7b7493",
            width: 3,
          },
        },
        {
          selector: ":selected",
          style: {
            "border-color": "#243b53",
            "border-width": 3,
            "line-color": "#243b53",
            "target-arrow-color": "#243b53",
          },
        },
      ],
      layout: {
        name: layout === "paths" ? "preset" : layout,
        directed: true,
        padding: 32,
        spacingFactor: 1,
      } as any,
    });
    instance.on("tap", "node", (e) =>
      selectRef.current({ type: "node", ...e.target.data() }),
    );
    instance.on("tap", "edge", (e) =>
      selectRef.current({ type: "event", ...e.target.data().event }),
    );
    cy.current = instance;
    const observer = new ResizeObserver(() => {
      instance.resize();
      instance.fit(undefined, 24);
    });
    observer.observe(container.current);
    return () => {
      observer.disconnect();
      instance.destroy();
    };
  }, [graph, layout]);
  return (
    <div className="graph-shell">
      <div className="graph-toolbar">
        <span>
          <Network size={15} /> Observed fund movement
        </span>
        <div>
          <button
            aria-label="Zoom in"
            onClick={() => cy.current?.zoom(cy.current.zoom() * 1.2)}
          >
            <Plus size={15} />
          </button>
          <button
            aria-label="Zoom out"
            onClick={() => cy.current?.zoom(cy.current.zoom() / 1.2)}
          >
            <Minus size={15} />
          </button>
          <button
            aria-label="Fit graph"
            onClick={() => cy.current?.fit(undefined, 60)}
          >
            <Maximize2 size={15} />
          </button>
          <select
            aria-label="Graph layout"
            value={layout}
            onChange={(e) => setLayout(e.target.value)}
          >
            <option value="paths">Path layout</option>
            <option value="circle">Circular layout</option>
          </select>
        </div>
      </div>
      <div className="graph-canvas" ref={container} />
      <div className="graph-legend">
        <span>
          <i className="seed-dot" />
          Reported
        </span>
        <span>
          <i className="custody-dot" />
          Custody assertion
        </span>
        <span>
          <i className="unknown-dot" />
          Unknown
        </span>
        <span>
          <i className="risk-dot" />
          Mixer assertion
        </span>
        <small>Select a wallet or transfer to inspect evidence</small>
      </div>
    </div>
  );
}
