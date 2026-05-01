import { useState } from "react";
import { getPrediction } from "../services/api";
import ChartView from "./ChartView";

function Simulator({ setSimulatedData }) {
  const [requests, setRequests] = useState(10);
  const [machines, setMachines] = useState(2);

  const [containers, setContainers] = useState(0);
  const [history, setHistory] = useState([]);
  const [reqHistory, setReqHistory] = useState([]);
  const [coldHistory, setColdHistory] = useState([]);

  const [extra, setExtra] = useState({});

  const simulate = async () => {
    const res = await getPrediction({ requests, machines });

    console.log("API RESPONSE:", res); // 🔥 DEBUG

    // safer extraction (IMPORTANT FIX)
    const containerVal = res.containers_needed ?? 0;
    const coldVal = res.cold_start ?? 0;

    setContainers(containerVal);
    setExtra(res);

    setHistory(prev => {
      const updated = [...prev, containerVal];
      setSimulatedData(updated); // keep this
      return updated;
    });

    setReqHistory(prev => [...prev, requests]);
    setColdHistory(prev => [...prev, coldVal]);
  };

  return (
    <div>
      <h2 style={{ paddingBottom: "50px", fontSize: "50px", paddingTop: "100px" }}>
        Simulator
      </h2>

      {/* INPUT */}
      <div className="panel">
        <div>
          <label style={{ paddingRight: "20px" }}>Requests</label>
          <input
            type="number"
            value={requests}
            onChange={e => setRequests(+e.target.value)}
          />
        </div>

        <div>
          <label style={{ paddingRight: "20px" }}>Machines</label>
          <input
            type="number"
            value={machines}
            onChange={e => setMachines(+e.target.value)}
          />
        </div>

        <button onClick={simulate}>🚀 Simulate</button>
      </div>

      {/* METRICS */}
      <div className="cards">
        <div className="card">
          <h3>Containers</h3>
          <span>{containers !== undefined ? containers : "-"}</span>
        </div>

        <div className="card">
          <h3>Prediction</h3>
          <span>
            {extra.prediction !== undefined
              ? extra.prediction.toFixed(2)
              : "-"}
          </span>
        </div>

        <div className="card">
          <h3>Prewarm</h3>
          <span>{extra.prewarm !== undefined ? extra.prewarm : "-"}</span>
        </div>
<div className="card">
  <h3>Required</h3>
  <span>{extra.required || 0}</span>
</div>
        <div className="card">
          <h3>Capacity</h3>
          <span>
            {extra.capacity !== undefined
              ? extra.capacity.toFixed(2)
              : "-"}
          </span>
        </div>

        <div className="card">
          <h3>Cold Start</h3>
          <span>
            {extra.cold_start !== undefined ? extra.cold_start : "-"}
          </span>
        </div>
      </div>

      {/* CHARTS */}
      <div className="charts">
        <ChartView
          containers={history}
          requests={reqHistory}
          title="Requests vs Containers"
        />

        <ChartView
          containers={coldHistory}
          title="Cold Starts Over Time"
        />
      </div>
    </div>
  );
}

export default Simulator;