import { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Legend
} from "chart.js";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Legend);

function DatasetView({ simulated = [] }) {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/dataset")
      .then(res => res.json())
      .then(d => setData(d.data))
      .catch(err => console.error("Dataset fetch error:", err));
  }, []);

  // 🔥 NORMALIZATION FUNCTION (FIXES SCALING ISSUE)
  const normalize = (arr) => {
    if (!arr || arr.length === 0) return [];
    const max = Math.max(...arr);
    const min = Math.min(...arr);
    return arr.map(v => (v - min) / (max - min + 1e-6));
  };

  const normalizedActual = normalize(data);
  const normalizedSim = normalize(simulated);

  const chartData = {
    labels: normalizedActual.map((_, i) => i),
    datasets: [
      {
        label: "Actual Workload (Normalized)",
        data: normalizedActual,
        borderColor: "#3b82f6",
        borderWidth: 2,
        pointRadius: 0
      },
      {
        label: "Simulated Containers (Normalized)",
        data: normalizedSim,
        borderColor: "#22c55e",
        borderWidth: 2,
        pointRadius: 0
      }
    ]
  };

  return (
    <div className="chart">
      <h2 style={{ textAlign: "center", marginBottom: "20px" }}>
        Dataset vs Simulation
      </h2>
      <Line data={chartData} />
    </div>
  );
}

export default DatasetView;