"use client";

import { useEffect, useState } from "react";
import styles from "./page.module.css";

interface HealthData {
  status: string;
  database: string;
  service: string;
}

export default function Home() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastChecked, setLastChecked] = useState<string>("");

  const apiUrl =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const fetchHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${apiUrl}/health`, {
        cache: "no-store",
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      const data: HealthData = await res.json();
      setHealth(data);
      setLastChecked(new Date().toLocaleTimeString());
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Failed to connect to FastAPI";
      setError(message);
      setHealth(null);
      setLastChecked(new Date().toLocaleTimeString());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const isApiOnline = !error && health?.status === "ok";
  const isDbOnline = !error && health?.database === "connected";

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <div className={styles.header}>
          <span className={styles.tag}>Milestone 1 Complete</span>
          <h1 className={styles.title}>Climate Data Platform</h1>
          <p className={styles.subtitle}>
            Frontend & Backend Monorepo Foundation Bridge
          </p>
        </div>

        <div className={styles.statusGrid}>
          {/* FastAPI Card */}
          <div className={styles.statusItem}>
            <div className={styles.serviceInfo}>
              <h3>FastAPI Backend</h3>
              <p>Port 8000 / ASGI Uvicorn</p>
            </div>
            <div>
              {loading ? (
                <span className={`${styles.badge} ${styles.badgeLoading}`}>
                  <span className={styles.badgeDot}></span> Checking...
                </span>
              ) : isApiOnline ? (
                <span className={`${styles.badge} ${styles.badgeSuccess}`}>
                  <span className={styles.badgeDot}></span> Online
                </span>
              ) : (
                <span className={`${styles.badge} ${styles.badgeError}`}>
                  <span className={styles.badgeDot}></span> Offline
                </span>
              )}
            </div>
          </div>

          {/* PostgreSQL Card */}
          <div className={styles.statusItem}>
            <div className={styles.serviceInfo}>
              <h3>PostgreSQL Database</h3>
              <p>Port 5432 / climate_data</p>
            </div>
            <div>
              {loading ? (
                <span className={`${styles.badge} ${styles.badgeLoading}`}>
                  <span className={styles.badgeDot}></span> Checking...
                </span>
              ) : isDbOnline ? (
                <span className={`${styles.badge} ${styles.badgeSuccess}`}>
                  <span className={styles.badgeDot}></span> Connected
                </span>
              ) : (
                <span className={`${styles.badge} ${styles.badgeError}`}>
                  <span className={styles.badgeDot}></span> Disconnected
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Live response / error payload */}
        <div className={styles.details}>
          <div>
            <strong>Target API:</strong> {apiUrl}/health
          </div>
          <div>
            <strong>Last Checked:</strong> {lastChecked || "Never"}
          </div>
          {health && (
            <div style={{ marginTop: "0.5rem" }}>
              <strong>Response:</strong> {JSON.stringify(health, null, 2)}
            </div>
          )}
          {error && (
            <div style={{ marginTop: "0.5rem", color: "#f87171" }}>
              <strong>Error:</strong> {error}
            </div>
          )}
        </div>

        <div className={styles.footer}>
          <div className={styles.links}>
            <a
              href={`${apiUrl}/docs`}
              target="_blank"
              rel="noopener noreferrer"
            >
              Swagger Docs ↗
            </a>
            <a
              href={`${apiUrl}/health`}
              target="_blank"
              rel="noopener noreferrer"
            >
              API Health JSON ↗
            </a>
          </div>

          <button
            className={styles.refreshButton}
            onClick={fetchHealth}
            disabled={loading}
          >
            {loading ? "Checking..." : "Re-check Health"}
          </button>
        </div>
      </div>
    </div>
  );
}
