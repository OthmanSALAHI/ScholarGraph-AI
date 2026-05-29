import React, { FormEvent, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  askQuestion,
  getPaper,
  getPapers,
  getSummary,
  Paper,
  PaperAnalysis,
  PaperChunk,
  uploadPaper,
} from "../lib/api";
import "./styles.css";

const sectionOrder = ["abstract", "introduction", "methodology", "results", "conclusion"];

function App() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [activePaper, setActivePaper] = useState<Paper | null>(null);
  const [analysis, setAnalysis] = useState<PaperAnalysis | null>(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<PaperChunk[]>([]);
  const [status, setStatus] = useState("");
  const [isBusy, setIsBusy] = useState(false);

  useEffect(() => {
    refreshPapers();
  }, []);

  const visibleSections = useMemo(() => {
    if (!activePaper) return [];
    return sectionOrder
      .map((name) => [name, activePaper.sections[name]] as const)
      .filter(([, value]) => typeof value === "string" && value.trim());
  }, [activePaper]);

  async function refreshPapers() {
    try {
      setPapers(await getPapers());
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Could not load papers.");
    }
  }

  async function openPaper(paperId: string) {
    setIsBusy(true);
    setStatus("");
    try {
      const paper = await getPaper(paperId);
      setActivePaper(paper);
      setAnalysis(await getSummary(paper.paper_id));
      setAnswer("");
      setSources([]);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Could not open paper.");
    } finally {
      setIsBusy(false);
    }
  }

  async function handleUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsBusy(true);
    setStatus("Processing paper...");
    try {
      const paper = await uploadPaper(file);
      await refreshPapers();
      await openPaper(paper.paper_id);
      setStatus("Paper processed.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Upload failed.");
    } finally {
      setIsBusy(false);
      event.target.value = "";
    }
  }

  async function handleAsk(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!activePaper || !question.trim()) return;

    setIsBusy(true);
    setStatus("");
    try {
      const response = await askQuestion(activePaper.paper_id, question.trim());
      setAnswer(response.answer);
      setSources(response.sources);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Question failed.");
    } finally {
      setIsBusy(false);
    }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">ScholarGraph AI</div>
        <label className="upload-control">
          <span>Upload PDF</span>
          <input type="file" accept="application/pdf" onChange={handleUpload} disabled={isBusy} />
        </label>

        <div className="paper-list">
          {papers.map((paper) => (
            <button
              className={paper.paper_id === activePaper?.paper_id ? "paper active" : "paper"}
              key={paper.paper_id ?? paper.filename}
              onClick={() => openPaper(paper.paper_id)}
              type="button"
            >
              <strong>{paper.paper_id}</strong>
              <span>{paper.original_filename ?? paper.filename}</span>
            </button>
          ))}
        </div>
      </aside>

      <section className="workspace">
        {status && <div className="status">{status}</div>}

        {!activePaper ? (
          <div className="empty-state">Upload or select a paper to begin.</div>
        ) : (
          <>
            <header className="paper-header">
              <div>
                <p>{activePaper.paper_id}</p>
                <h1>{analysis?.title || activePaper.original_filename || activePaper.filename}</h1>
              </div>
              <span>{activePaper.chunks?.length ?? 0} chunks</span>
            </header>

            {analysis && (
              <section className="analysis-grid">
                <AnalysisBlock label="Problem" value={analysis.problem} />
                <AnalysisBlock label="Objective" value={analysis.objective} />
                <AnalysisBlock label="Method" value={analysis.method} />
              </section>
            )}

            <section className="content-grid">
              <div className="sections-panel">
                <h2>Sections</h2>
                {visibleSections.map(([name, value]) => (
                  <article className="section-block" key={name}>
                    <h3>{name}</h3>
                    <p>{value as string}</p>
                  </article>
                ))}
              </div>

              <div className="chat-panel">
                <h2>Ask</h2>
                <form onSubmit={handleAsk} className="question-form">
                  <textarea
                    value={question}
                    onChange={(event) => setQuestion(event.target.value)}
                    placeholder="What problem does this paper solve?"
                    rows={4}
                  />
                  <button type="submit" disabled={isBusy || !question.trim()}>
                    Ask question
                  </button>
                </form>

                {answer && (
                  <article className="answer-block">
                    <h3>Answer</h3>
                    <p>{answer}</p>
                  </article>
                )}

                {sources.length > 0 && (
                  <div className="sources">
                    <h3>Sources</h3>
                    {sources.map((source) => (
                      <article className="source" key={source.chunk_id}>
                        <span>
                          {source.section} {source.page ? `page ${source.page}` : ""}
                        </span>
                        <p>{source.text}</p>
                      </article>
                    ))}
                  </div>
                )}
              </div>
            </section>
          </>
        )}
      </section>
    </main>
  );
}

function AnalysisBlock({ label, value }: { label: string; value: string }) {
  return (
    <article className="analysis-block">
      <h2>{label}</h2>
      <p>{value || "Not detected."}</p>
    </article>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
