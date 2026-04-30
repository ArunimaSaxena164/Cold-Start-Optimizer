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

export default function ChartView({ containers = [], requests = [], title = "Simulation", label1 = "Containers" }) {

  const chartData = {
    labels: containers.map((_, i) => i),
    datasets: [
      {
        label: label1,   // 🔥 dynamic label
        data: containers,
        borderColor: "#22c55e",
        borderWidth: 2,
        pointRadius: 0
      },
      ...(requests.length > 0
        ? [{
            label: "Requests",
            data: requests,
            borderColor: "#f97316",
            borderWidth: 2,
            pointRadius: 0
          }]
        : [])
    ]
  };

  return (
    <div className="chart">
      <h3 style={{ textAlign: "center" }}>{title}</h3>
      <Line data={chartData} />
    </div>
  );
}