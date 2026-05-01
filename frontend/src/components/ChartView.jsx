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

function ChartView({ containers = [], requests = [], title = "Simulation" }) {

  const data = {
    labels: containers.map((_, i) => i),
    datasets: [
      {
        label: "Containers",
        data: containers,
        borderColor: "#22c55e",
        yAxisID: "y1",
        borderWidth: 2,
        pointRadius: 0
      },
      ...(requests.length > 0
        ? [{
            label: "Requests",
            data: requests,
            borderColor: "#f97316",
            yAxisID: "y2",
            borderWidth: 2,
            pointRadius: 0
          }]
        : [])
    ]
  };

  const options = {
    responsive: true,
    scales: {
      y1: {
        type: "linear",
        position: "left",
        title: {
          display: true,
          text: "Containers"
        }
      },
      y2: {
        type: "linear",
        position: "right",
        title: {
          display: true,
          text: "Requests"
        },
        grid: {
          drawOnChartArea: false
        }
      }
    }
  };

  return (
    <div className="chart">
      <h3 style={{ textAlign: "center" }}>{title}</h3>
      <Line data={data} options={options} />
    </div>
  );
}

export default ChartView;